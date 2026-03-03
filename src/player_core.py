import time
import cv2
import torch
import numpy as np
import mss
import threading
import queue
import traceback
import os
import sys
import shutil
import warnings
import tkinter as tk
from tkinter import ttk, messagebox

warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# 🔧 环境路径配置
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
lib_path = os.path.join(project_root, "lib")

if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
os.environ["NUNIF_HOME"] = lib_path

try:
    from iw3.utils import create_depth_model
except ImportError:
    print(f"❌ 严重错误: 无法在 {lib_path} 中找到 iw3 库")
    def create_depth_model(**kwargs): return None

# === 库检测 ===
try: import psutil; HAS_PSUTIL = True
except ImportError: HAS_PSUTIL = False

try: import pynvml; HAS_NVML = True
except ImportError: HAS_NVML = False

try: import dxcam; HAS_DXCAM = True
except ImportError: HAS_DXCAM = False

# === 全局默认配置 ===
CONFIG = {
    "model": "Base",       
    "fill_mode": "Fit",     
    "res_mode": "1920x1080 (1080p FHD)", # 默认分辨率
    "monitor_id": 1,       
    "capture_backend": "Camera",  
    "buffer": 0,                  
    "dxcam_list_idx": 0,
    "camera_idx": 0,        
    "started": False 
}

DIVERGENCE = 0.13       
SWAP_EYES = False       
FOCUS_EMA = 0.15        
CENTER_REGION = 0.25    
STEP_SIZE = 0.005
DEVICE = "cuda"
INFER_WIDTH = 518 

frame_queue = None
running = True
thread_error = None
show_osd = True 
SCREEN_W = 0
SCREEN_H = 0
DXCAM_MONITOR_LIST = []
CAMERA_LIST = [] 

# ==========================================
# 工具函数
# ==========================================
def scan_dxcam_monitors():
    if not HAS_DXCAM: return []
    monitors = []
    for dev_idx in range(4):
        try:
            for out_idx in range(4):
                try:
                    cam = dxcam.create(device_idx=dev_idx, output_idx=out_idx)
                    if cam:
                        monitors.append({"device": dev_idx, "output": out_idx, "res": f"{cam.width}x{cam.height}", "name": f"GPU{dev_idx}-Out{out_idx}"})
                        del cam 
                except: break 
        except: pass 
    return monitors

def scan_cameras():
    monitors = []
    print("\n[INFO] Scanning Cameras (OBS/Webcams)... This may take a second.")
    for i in range(4):
        cap = cv2.VideoCapture(i) 
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            monitors.append({"device": i, "name": f"Camera Device {i}", "res": f"{w}x{h}"})
            cap.release()
    return monitors

def get_multiple_of_14(size): return int(round(size / 14) * 14)

def get_gpu_load():
    if not HAS_NVML: return 0.0
    try: return pynvml.nvmlDeviceGetUtilizationRates(pynvml.nvmlDeviceGetHandleByIndex(0)).gpu
    except: return 0.0

def parse_resolution(res_str):
    """解析 GUI 选择的分辨率字符串为宽高数字"""
    if "Native" in res_str: 
        return None, None
    try:
        parts = res_str.split(" ")[0].split("x")
        return int(parts[0]), int(parts[1])
    except:
        return 1920, 1080

# ==========================================
# GUI 启动器
# ==========================================
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Realtime 3D Player (Open Source v14.2)")
        self.root.geometry("480x580")
        x = (root.winfo_screenwidth() - 480) // 2
        y = (root.winfo_screenheight() - 580) // 2
        root.geometry(f"+{x}+{y}")

        style = ttk.Style()
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TButton", font=("Microsoft YaHei", 11, "bold"))
        
        # === Capture Engine ===
        ttk.Label(root, text="Capture Engine", padding=(0, 10, 0, 5)).pack()
        self.backend_var = tk.StringVar(value=CONFIG["capture_backend"])
        be_frame = ttk.Frame(root)
        be_frame.pack()
        
        dx_state = tk.NORMAL if HAS_DXCAM else tk.DISABLED
        ttk.Radiobutton(be_frame, text="DXCam", variable=self.backend_var, value="DXCam", state=dx_state, command=self.update_sources).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(be_frame, text="MSS", variable=self.backend_var, value="MSS", command=self.update_sources).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(be_frame, text="Camera (OBS)", variable=self.backend_var, value="Camera", command=self.update_sources).pack(side=tk.LEFT, padx=5)
        
        if self.backend_var.get() == "Auto": self.backend_var.set("DXCam" if HAS_DXCAM else "MSS")

        # === AI Model ===
        ttk.Label(root, text="AI Model", padding=(0, 10, 0, 5)).pack()
        self.model_var = tk.StringVar(value=CONFIG["model"])
        model_frame = ttk.Frame(root)
        model_frame.pack()
        ttk.Radiobutton(model_frame, text="Small", variable=self.model_var, value="Small").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Base", variable=self.model_var, value="Base").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Large", variable=self.model_var, value="Large").pack(side=tk.LEFT, padx=5)

        # === Fill Mode ===
        ttk.Label(root, text="Fill Mode", padding=(0, 15, 0, 5)).pack()
        self.fill_var = tk.StringVar(value=CONFIG["fill_mode"])
        fill_frame = ttk.Frame(root)
        fill_frame.pack()
        ttk.Radiobutton(fill_frame, text="Fit (Black Bars)", variable=self.fill_var, value="Fit").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(fill_frame, text="Stretch", variable=self.fill_var, value="Stretch").pack(side=tk.LEFT, padx=10)

        # === Resolution (新增主流分辨率下拉菜单) ===
        ttk.Label(root, text="Target Resolution (Controls OBS & Rendering)", padding=(0, 15, 0, 5)).pack()
        self.res_var = tk.StringVar(value=CONFIG["res_mode"])
        res_combo = ttk.Combobox(root, textvariable=self.res_var, state="readonly", width=30)
        res_combo['values'] = [
            "Native (Auto/Source)",
            "3840x2160 (4K UHD)",
            "2560x1440 (2K QHD)",
            "1920x1080 (1080p FHD)",
            "1600x900 (900p HD+)",
            "1280x720 (720p HD)",
            "854x480 (480p WVGA)"
        ]
        res_combo.pack()

        # === Source Selection ===
        ttk.Label(root, text="Select Source", padding=(0, 15, 0, 5)).pack()
        self.mon_combo = ttk.Combobox(root, width=45, state="readonly")
        self.mon_combo.pack()
        self.update_sources() 

        # === Buffer ===
        ttk.Label(root, text="Buffer Size (0=Realtime)", padding=(0, 15, 0, 5)).pack()
        self.buf_spin = ttk.Spinbox(root, from_=0, to=999, width=5)
        self.buf_spin.set(CONFIG["buffer"])
        self.buf_spin.pack()

        ttk.Button(root, text="START PLAYER", command=self.on_start).pack(pady=20, ipadx=30, ipady=10)

    def update_sources(self):
        backend = self.backend_var.get()
        values = []
        if backend == "DXCam":
            global DXCAM_MONITOR_LIST
            DXCAM_MONITOR_LIST = scan_dxcam_monitors()
            for idx, m in enumerate(DXCAM_MONITOR_LIST):
                values.append(f"DXCam: {m['name']} ({m['res']}) [ID={idx}]")
        elif backend == "MSS":
            try:
                sct = mss.mss()
                for i, m in enumerate(sct.monitors):
                    if i == 0: continue 
                    values.append(f"MSS: Screen {i} ({m['width']}x{m['height']})")
            except: pass
        elif backend == "Camera":
            global CAMERA_LIST
            CAMERA_LIST = scan_cameras()
            for m in CAMERA_LIST:
                values.append(f"Camera: {m['name']} [ID={m['device']}]")

        if not values: values = ["No source found"]
        self.mon_combo['values'] = values
        
        current_idx = 0
        current_val = self.mon_combo.get()
        if not current_val and values:
            if backend == "DXCam":
                 for i, v in enumerate(values):
                     if f"[ID={CONFIG['dxcam_list_idx']}]" in v: current_idx = i; break
            elif backend == "Camera":
                 for i, v in enumerate(values):
                     if f"[ID={CONFIG['camera_idx']}]" in v: current_idx = i; break
            else:
                for i, v in enumerate(values):
                     if f"Screen {CONFIG['monitor_id']}" in v: current_idx = i; break
        self.mon_combo.current(current_idx)

    def on_start(self):
        CONFIG["model"] = self.model_var.get()
        CONFIG["fill_mode"] = self.fill_var.get()
        CONFIG["res_mode"] = self.res_var.get()
        CONFIG["capture_backend"] = self.backend_var.get()
        
        try: CONFIG["buffer"] = max(0, int(self.buf_spin.get()))
        except: CONFIG["buffer"] = 0
        
        selection = self.mon_combo.get()
        if CONFIG["capture_backend"] == "DXCam":
            try: CONFIG["dxcam_list_idx"] = int(selection.split("[ID=")[1].split("]")[0])
            except: CONFIG["dxcam_list_idx"] = 0
        elif CONFIG["capture_backend"] == "MSS":
            try:
                import re
                match = re.search(r"Screen (\d+)", selection)
                CONFIG["monitor_id"] = int(match.group(1)) if match else 1
            except: CONFIG["monitor_id"] = 1
        elif CONFIG["capture_backend"] == "Camera":
            try: CONFIG["camera_idx"] = int(selection.split("[ID=")[1].split("]")[0])
            except: CONFIG["camera_idx"] = 0
            
        fname_map = {"Small": "depth_anything_v2_vits.pth", "Base":  "depth_anything_v2_vitb.pth", "Large": "depth_anything_v2_vitl.pth"}
        fname = fname_map.get(CONFIG["model"], "depth_anything_v2_vitb.pth")
        user_path = os.path.join(project_root, "models", fname)
        
        if not os.path.exists(user_path):
            messagebox.showerror("Error", f"Model not found at:\n{user_path}\n\nPlease check your 'models' folder.")
            return
        
        CONFIG["started"] = True
        self.root.destroy()

# ==========================================
# ⚙️ 采集线程
# ==========================================
def capture_thread_func():
    global running, thread_error, SCREEN_W, SCREEN_H, frame_queue
    backend = CONFIG["capture_backend"]
    print(f"[INFO] Capture Engine: {backend}")
    realtime_mode = (CONFIG["buffer"] <= 1)

    try:
        if backend == "Camera":
            cam_idx = CONFIG.get("camera_idx", 0)
            print(f"[INFO] Connecting to Camera/OBS Device {cam_idx}...")
            cap = cv2.VideoCapture(cam_idx)
            
            # 解析 GUI 设置的分辨率，并强制 OBS 吐出对应尺寸
            req_w, req_h = parse_resolution(CONFIG["res_mode"])
            if req_w and req_h:
                print(f"[INFO] Requesting OBS resolution: {req_w}x{req_h}")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, req_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, req_h)
            else:
                # 若选择 Native，为防止 640x480 bug，保底请求 1080P
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            SCREEN_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            SCREEN_H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if not cap.isOpened() or SCREEN_W == 0:
                raise Exception(f"无法打开设备 ID={cam_idx}，请确认 OBS 虚拟摄像机已启动。")
                
            print(f"[INFO] Camera Connected: {SCREEN_W}x{SCREEN_H}")

            while running:
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    if realtime_mode:
                        while not frame_queue.empty():
                            try: frame_queue.get_nowait()
                            except: break
                        frame_queue.put(frame_rgb)
                    else:
                        if not frame_queue.full(): frame_queue.put(frame_rgb)
                        else: time.sleep(0.001)
                else:
                    time.sleep(0.01)
            cap.release()

        elif backend == "DXCam":
            list_idx = CONFIG.get("dxcam_list_idx", 0)
            if list_idx < len(DXCAM_MONITOR_LIST):
                target = DXCAM_MONITOR_LIST[list_idx]
                dev_idx, out_idx = target["device"], target["output"]
            else: dev_idx, out_idx = 0, 0
            
            camera = dxcam.create(device_idx=dev_idx, output_idx=out_idx)
            camera.start(target_fps=60, video_mode=True)
            SCREEN_W, SCREEN_H = camera.width, camera.height

            while running:
                img = camera.get_latest_frame() 
                if img is not None:
                    if realtime_mode:
                        while not frame_queue.empty():
                            try: frame_queue.get_nowait()
                            except: break
                        frame_queue.put(img)
                    else:
                        if not frame_queue.full(): frame_queue.put(img)
                        else: time.sleep(0.001)
                else: time.sleep(0.001)
            camera.stop()
            del camera

        elif backend == "MSS":
            sct = mss.mss()
            monitor_id = CONFIG["monitor_id"]
            if monitor_id >= len(sct.monitors): monitor_id = 1
            monitor = sct.monitors[monitor_id]
            SCREEN_W, SCREEN_H = monitor['width'], monitor['height']

            while running:
                if not running: break
                sct_img = sct.grab(monitor)
                if realtime_mode:
                    while not frame_queue.empty():
                        try: frame_queue.get_nowait()
                        except: break
                if not frame_queue.full(): frame_queue.put(sct_img)
                else: time.sleep(0.002)

    except Exception as e:
        thread_error = f"Capture Error: {str(e)}"
        running = False

def apply_smart_stereo_gpu(img_tensor, depth_tensor, strength, focus_plane, swap):
    B, C, H, W = img_tensor.shape
    d_min, d_max = depth_tensor.min(), depth_tensor.max()
    depth_norm = (depth_tensor - d_min) / (d_max - d_min + 1e-6)
    shift = (depth_norm - focus_plane) * (strength * 0.1)
    
    xx = torch.linspace(-1, 1, W, device=DEVICE, dtype=img_tensor.dtype)
    yy = torch.linspace(-1, 1, H, device=DEVICE, dtype=img_tensor.dtype)
    grid_y, grid_x = torch.meshgrid(yy, xx, indexing='ij')
    grid = torch.stack((grid_x, grid_y), dim=-1).unsqueeze(0).expand(B, -1, -1, -1)
    
    grid_l, grid_r = grid.clone(), grid.clone()
    shift_sq = shift.squeeze(1)
    if not swap:
        grid_l[..., 0] -= shift_sq
        grid_r[..., 0] += shift_sq
    else:
        grid_l[..., 0] += shift_sq
        grid_r[..., 0] -= shift_sq
        
    left = torch.nn.functional.grid_sample(img_tensor, grid_l, mode='bilinear', padding_mode='reflection', align_corners=False)
    right = torch.nn.functional.grid_sample(img_tensor, grid_r, mode='bilinear', padding_mode='reflection', align_corners=False)
    return left, right

def add_black_borders_gpu(img_tensor, target_w, target_h):
    _, _, h, w = img_tensor.shape
    pad_h = target_h - h
    pad_w = target_w - w
    if pad_h <= 0 and pad_w <= 0: return img_tensor
    return torch.nn.functional.pad(img_tensor, (pad_w//2, pad_w-pad_w//2, pad_h//2, pad_h-pad_h//2), mode='constant', value=0)

def draw_osd_full(img, fps, focus, str_val, buffer_size, gpu_load, ram_gb, cpu_percent, vram_gb, in_res, out_res):
    h, w = img.shape[:2]
    font, scale, color, thick = cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 127), 2
    fps_col = (0, 0, 255) if fps < 20 else color
    buf_str = "REALTIME" if CONFIG["buffer"] <= 1 else f"{buffer_size}/{CONFIG['buffer']}"
    
    lines_l = [(f"FPS : {fps:.1f}", fps_col), (f"Buf : {buf_str}", color), (f"Str : {str_val:.3f}", color), (f"Foc : {focus:.2f}", color)]
    lines_r = [(f"GPU : {gpu_load}%", color), (f"VRAM: {vram_gb:.1f}G", color), (f"CPU : {cpu_percent:.0f}%", color), (f"RAM : {ram_gb:.1f}G", color)]
    
    y = 40
    for text, col in lines_l:
        cv2.putText(img, text, (22, y+2), font, scale, (0,0,0), thick+1)
        cv2.putText(img, text, (20, y), font, scale, col, thick)
        y += 30
    y = 40
    for text, col in lines_r:
        cv2.putText(img, text, (242, y+2), font, scale, (0,0,0), thick+1)
        cv2.putText(img, text, (240, y), font, scale, col, thick)
        y += 30
    
    res_info = f"In: {in_res[0]}x{in_res[1]} -> Out: {out_res[0]}x{out_res[1]} | Model: {CONFIG['model']}"
    cv2.putText(img, res_info, (20, h - 45), font, 0.5, (200, 200, 200), 1)
    cv2.putText(img, f"Press 'ESC' to Menu, 'Q' to Quit", (20, h - 20), font, 0.5, (255, 255, 0), 1)

# ==========================================
# ▶️ 播放器主逻辑
# ==========================================
def start_player():
    global running, DIVERGENCE, SWAP_EYES, thread_error, show_osd, SCREEN_W, SCREEN_H, frame_queue
    running = True
    thread_error = None
    SCREEN_W, SCREEN_H = 0, 0
    restart_requested = False
    
    q_size = 1 if CONFIG["buffer"] <= 1 else CONFIG["buffer"] + 5
    frame_queue = queue.Queue(maxsize=q_size)

    if HAS_NVML: 
        try: pynvml.nvmlInit()
        except: pass

    model_type_map = {"Small": "Any_V2_S", "Base": "Any_V2_B", "Large": "Any_V2_L"}
    model_type = model_type_map[CONFIG["model"]]
    win_name = f"3D Player ({CONFIG['capture_backend']})"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    
    t = threading.Thread(target=capture_thread_func)
    t.daemon = True
    t.start()
    
    render_w, render_h = 1920, 1080 
    
    def update_loading(text):
        global running 
        if not running: return
        loading_img = np.zeros((render_h, render_w, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.2, 2)[0]
        text_x = (render_w - text_size[0]) // 2
        text_y = (render_h + text_size[1]) // 2
        cv2.putText(loading_img, text, (text_x, text_y), font, 1.2, (255, 255, 255), 2)
        cv2.putText(loading_img, "Press Q to Quit", (render_w//2 - 50, render_h - 100), font, 0.8, (150, 150, 150), 1)
        cv2.imshow(win_name, loading_img)
        if cv2.waitKey(1) & 0xFF == ord('q'): running = False; return False 

    print("[INFO] Waiting for capture resolution...")
    for _ in range(50):
        if not running: break
        update_loading("Waiting for source connection...")
        if SCREEN_W > 0: break
        time.sleep(0.1)
    
    if not running: return False
    
    # 根据 GUI 解析出的分辨率来决定渲染画框的大小
    req_w, req_h = parse_resolution(CONFIG["res_mode"])
    target_render_w, target_render_h = (req_w, req_h) if (req_w and req_h) else (SCREEN_W or 1920, SCREEN_H or 1080)
    
    cv2.resizeWindow(win_name, target_render_w, target_render_h)
    render_w, render_h = target_render_w, target_render_h

    try:
        fname_map = {"Small": "depth_anything_v2_vits.pth", "Base":  "depth_anything_v2_vitb.pth", "Large": "depth_anything_v2_vitl.pth"}
        fname = fname_map.get(CONFIG["model"], "depth_anything_v2_vitb.pth")
        user_path = os.path.join(project_root, "models", fname)
        iw3_target_path = os.path.join(project_root, "lib", "iw3", "pretrained_models", "hub", "checkpoints", fname)

        update_loading("Checking model files...")
        if not os.path.exists(user_path): raise FileNotFoundError(f"Missing: {user_path}")

        update_loading("Adapting model for iw3...")
        if not os.path.exists(iw3_target_path):
            os.makedirs(os.path.dirname(iw3_target_path), exist_ok=True)
            try: os.link(user_path, iw3_target_path)
            except OSError: shutil.copy2(user_path, iw3_target_path)
        
        update_loading(f"Initializing {CONFIG['model']}...")
        model_wrapper = create_depth_model(model_type=model_type) 
        if hasattr(model_wrapper, "load"): model_wrapper.load(gpu=0)
        model = model_wrapper.model if hasattr(model_wrapper, "model") else model_wrapper
        model = model.to(DEVICE).half().eval()
        
    except Exception as e:
        messagebox.showerror("Load Error", str(e))
        running = False
        return True 

    prev_depth, current_focus, frame_cnt, start_time = None, 0.5, 0, time.time()
    fps_val, gpu_load, cpu_val, ram_val, vram_val = 0.0, 0.0, 0.0, 0.0, 0.0

    print(f"[INFO] Core Loop Started. Output Render: {target_render_w}x{target_render_h}")

    while running:
        if thread_error: break
        try: captured_data = frame_queue.get(timeout=0.01)
        except: continue

        if CONFIG["capture_backend"] == "Camera" or CONFIG["capture_backend"] == "DXCam":
            src_h, src_w = captured_data.shape[:2]
            img_gpu_raw = torch.from_numpy(captured_data).to(DEVICE, non_blocking=True).permute(2, 0, 1).unsqueeze(0).half() / 255.0
        else:
            raw_data = np.frombuffer(captured_data.raw, dtype=np.uint8)
            src_h, src_w = captured_data.height, captured_data.width
            img_bgra = torch.from_numpy(raw_data.copy()).view(src_h, src_w, 4)
            img_gpu_raw = img_bgra.to(DEVICE, non_blocking=True).permute(2, 0, 1).unsqueeze(0).half() / 255.0
            img_gpu_raw = img_gpu_raw[:, [2, 1, 0], :, :] 

        if not (src_w == target_render_w and src_h == target_render_h):
            if CONFIG["fill_mode"] == "Stretch":
                 img_render = torch.nn.functional.interpolate(img_gpu_raw, size=(target_render_h, target_render_w), mode='bilinear', align_corners=False)
                 final_h, final_w = target_render_h, target_render_w
            else:
                 scale = min(target_render_w / src_w, target_render_h / src_h)
                 fit_w, fit_h = int(src_w * scale), int(src_h * scale)
                 img_render = torch.nn.functional.interpolate(img_gpu_raw, size=(fit_h, fit_w), mode='bilinear', align_corners=False)
                 final_h, final_w = fit_h, fit_w
        else:
            img_render = img_gpu_raw
            final_h, final_w = target_render_h, target_render_w 

        ai_h, ai_w = get_multiple_of_14(int(INFER_WIDTH * src_h / src_w)), get_multiple_of_14(INFER_WIDTH)
        img_ai = torch.nn.functional.interpolate(img_gpu_raw, size=(ai_h, ai_w), mode='bilinear', align_corners=False)

        with torch.inference_mode():
            raw_depth = model(img_ai)
            if isinstance(raw_depth, dict): raw_depth = list(raw_depth.values())[0]
            elif isinstance(raw_depth, (list, tuple)): raw_depth = raw_depth[0]
            
            d_min, d_max = raw_depth.min(), raw_depth.max()
            depth_norm = (raw_depth - d_min) / (d_max - d_min + 1e-6)
            
            h_d, w_d = depth_norm.shape[-2:]
            rh, rw = int(h_d * CENTER_REGION), int(w_d * CENTER_REGION)
            center_crop = depth_norm[..., h_d//2-rh:h_d//2+rh, w_d//2-rw:w_d//2+rw]
            target_depth = torch.quantile(center_crop.float(), 0.8).item()
            current_focus = current_focus * (1 - FOCUS_EMA) + target_depth * FOCUS_EMA

            if prev_depth is None: prev_depth = raw_depth
            else: prev_depth = prev_depth * 0.7 + raw_depth * 0.3
            
            depth_render = torch.nn.functional.interpolate(prev_depth.unsqueeze(1), size=(final_h, final_w), mode='bilinear', align_corners=False)
            left, right = apply_smart_stereo_gpu(img_render, depth_render, DIVERGENCE, current_focus, SWAP_EYES)
            anaglyph = torch.cat((left[:, 0:1], right[:, 1:2], right[:, 2:3]), dim=1)
            
            if CONFIG["fill_mode"] == "Fit" and not (src_w == target_render_w and src_h == target_render_h): 
                anaglyph = add_black_borders_gpu(anaglyph, target_render_w, target_render_h)
            
            final_show = (anaglyph.squeeze(0).permute(1, 2, 0)[..., [2, 1, 0]] * 255).clamp(0, 255).to(torch.uint8).cpu().numpy()

        if show_osd: 
            draw_osd_full(final_show, fps_val, current_focus, DIVERGENCE, frame_queue.qsize(), gpu_load, ram_val, cpu_val, vram_val, (src_w, src_h), (target_render_w, target_render_h))
        
        cv2.imshow(win_name, final_show)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'): 
            running = False
            restart_requested = False
        elif key == 27: 
            running = False
            restart_requested = True
        elif key & 0xFF == ord('f'):
            is_full = cv2.getWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_FULLSCREEN
            cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL if is_full else cv2.WINDOW_FULLSCREEN)
        elif key & 0xFF == ord(']'): DIVERGENCE = min(5.0, DIVERGENCE + STEP_SIZE)
        elif key & 0xFF == ord('['): DIVERGENCE = max(0.0, DIVERGENCE - STEP_SIZE)
        elif key & 0xFF == ord(' '): SWAP_EYES = not SWAP_EYES
        elif key & 0xFF == 9: show_osd = not show_osd

        frame_cnt += 1
        if frame_cnt % 10 == 0:
            now = time.time(); fps_val = 10 / (now - start_time); start_time = now
            gpu_load = get_gpu_load()
            if HAS_PSUTIL: cpu_val, ram_val = psutil.cpu_percent(), psutil.virtual_memory().used / 1024**3
            vram_val = torch.cuda.memory_reserved(0) / 1024**3
            
    cv2.destroyAllWindows()
    if HAS_NVML: 
        try: pynvml.nvmlShutdown()
        except: pass
    
    if t.is_alive():
        running = False 
        t.join(timeout=2.0)
    
    return restart_requested

if __name__ == "__main__":
    pass