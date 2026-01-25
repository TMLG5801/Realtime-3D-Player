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
import tkinter as tk
from tkinter import ttk, messagebox

# 这里的 iw3 引用现在是安全的，因为 main.py 已经把 lib 加进去了
try:
    from iw3.utils import create_depth_model
except ImportError:
    print("❌ 错误: 无法导入 iw3。请确保 'lib/iw3' 文件夹存在。")
    # 为了防闪退，定义一个空函数
    def create_depth_model(**kwargs): return None

# === 库检测 ===
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False

try:
    import dxcam
    HAS_DXCAM = True
except ImportError:
    HAS_DXCAM = False

# === 全局配置 ===
CONFIG = {
    "model": "Base",       
    "fill_mode": "Fit",     
    "res_mode": "Native",   
    "monitor_id": 1,       
    "capture_backend": "Auto",
    "buffer": 60,
    "dxcam_list_idx": 0,
    "started": False  # 新增：用于通知 main.py 用户是否点击了 Start
}

# 内部参数
DIVERGENCE = 0.13       
SWAP_EYES = False       
FOCUS_EMA = 0.15        
CENTER_REGION = 0.25    
STEP_SIZE = 0.005
DEVICE = "cuda"
INFER_WIDTH = 518 

# 队列将在 start_player 中初始化
frame_queue = None
running = True
thread_error = None
show_osd = True 
SCREEN_W = 0
SCREEN_H = 0
DXCAM_MONITOR_LIST = []

# ==========================================
# 路径管理 (关键修改：去本地化)
# ==========================================
def get_model_path(model_name):
    # 获取项目根目录 (假设 src 在根目录下一级)
    # 或者是从 main.py 运行时的 cwd
    base_dir = os.getcwd() 
    
    filename_map = {
        "Small": "depth_anything_v2_vits.pth",
        "Base":  "depth_anything_v2_vitb.pth",
        "Large": "depth_anything_v2_vitl.pth"
    }
    
    filename = filename_map.get(model_name, "depth_anything_v2_vitb.pth")
    return os.path.join(base_dir, "models", filename)

# ==========================================
# 辅助函数
# ==========================================
def scan_dxcam_monitors():
    if not HAS_DXCAM: 
        return []
    monitors = []
    print("\n[INFO] Scanning DXCam monitors...")
    for dev_idx in range(4):
        try:
            for out_idx in range(4):
                try:
                    cam = dxcam.create(device_idx=dev_idx, output_idx=out_idx)
                    if cam:
                        monitors.append({
                            "device": dev_idx, 
                            "output": out_idx, 
                            "res": f"{cam.width}x{cam.height}",
                            "name": f"GPU{dev_idx}-Out{out_idx}"
                        })
                        del cam 
                except:
                    break 
        except:
            pass 
    return monitors

def get_multiple_of_14(size):
    return int(round(size / 14) * 14)

def get_gpu_load():
    if not HAS_NVML: return 0.0
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        return pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
    except: return 0.0

# ==========================================
# GUI 启动器
# ==========================================
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Realtime 3D Player (Open Source v1.0)")
        self.root.geometry("480x580")
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 480) // 2
        y = (screen_height - 580) // 2
        root.geometry(f"+{x}+{y}")

        style = ttk.Style()
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TButton", font=("Microsoft YaHei", 11, "bold"))
        
        # Logo or Title
        ttk.Label(root, text="Realtime 2D to 3D Converter", font=("Arial", 14, "bold"), padding=(0, 20, 0, 10)).pack()

        ttk.Label(root, text="Capture Engine", padding=(0, 10, 0, 5)).pack()
        self.backend_var = tk.StringVar(value="Auto")
        be_frame = ttk.Frame(root)
        be_frame.pack()
        dx_state = tk.NORMAL if HAS_DXCAM else tk.DISABLED
        ttk.Radiobutton(be_frame, text="DXCam (NVIDIA Only)", variable=self.backend_var, value="DXCam", state=dx_state).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(be_frame, text="MSS (Compatible)", variable=self.backend_var, value="MSS").pack(side=tk.LEFT, padx=5)

        ttk.Label(root, text="AI Model", padding=(0, 10, 0, 5)).pack()
        self.model_var = tk.StringVar(value="Base")
        model_frame = ttk.Frame(root)
        model_frame.pack()
        ttk.Radiobutton(model_frame, text="Small (Fast)", variable=self.model_var, value="Small").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Base (Balanced)", variable=self.model_var, value="Base").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Large (Best)", variable=self.model_var, value="Large").pack(side=tk.LEFT, padx=5)

        ttk.Label(root, text="Fill Mode", padding=(0, 15, 0, 5)).pack()
        self.fill_var = tk.StringVar(value="Fit")
        fill_frame = ttk.Frame(root)
        fill_frame.pack()
        ttk.Radiobutton(fill_frame, text="Fit (Black Bars)", variable=self.fill_var, value="Fit").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(fill_frame, text="Stretch", variable=self.fill_var, value="Stretch").pack(side=tk.LEFT, padx=10)

        ttk.Label(root, text="Resolution", padding=(0, 15, 0, 5)).pack()
        self.res_var = tk.StringVar(value="1080p")
        res_frame = ttk.Frame(root)
        res_frame.pack()
        ttk.Radiobutton(res_frame, text="Native", variable=self.res_var, value="Native").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(res_frame, text="1080P", variable=self.res_var, value="1080p").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(res_frame, text="720P", variable=self.res_var, value="720p").pack(side=tk.LEFT, padx=5)

        ttk.Label(root, text="Select Source", padding=(0, 15, 0, 5)).pack()
        self.mon_combo = ttk.Combobox(root, width=45, state="readonly")
        self.scan_and_fill_monitors()
        self.mon_combo.pack()

        ttk.Label(root, text="Buffer Size (1=Realtime)", padding=(0, 15, 0, 5)).pack()
        self.buf_spin = ttk.Spinbox(root, from_=1, to=9999, width=5)
        self.buf_spin.set(60)
        self.buf_spin.pack()

        ttk.Button(root, text="START PLAYER", command=self.on_start).pack(pady=20, ipadx=30, ipady=10)

    def scan_and_fill_monitors(self):
        values = []
        try:
            sct = mss.mss()
            for i, m in enumerate(sct.monitors):
                if i == 0: continue 
                values.append(f"MSS: Screen {i} ({m['width']}x{m['height']})")
        except: 
            pass

        global DXCAM_MONITOR_LIST
        if HAS_DXCAM:
            DXCAM_MONITOR_LIST = scan_dxcam_monitors()
            for idx, m in enumerate(DXCAM_MONITOR_LIST):
                values.append(f"DXCam: {m['name']} ({m['res']}) [ID={idx}]")
        
        if not values: 
            values = ["No monitors found"]
        self.mon_combo['values'] = values
        if values: 
            self.mon_combo.current(0)

    def on_start(self):
        CONFIG["model"] = self.model_var.get()
        CONFIG["fill_mode"] = self.fill_var.get()
        CONFIG["res_mode"] = self.res_var.get()
        try:
            val = int(self.buf_spin.get())
            if val <= 0: val = 1
            CONFIG["buffer"] = val
        except: 
            CONFIG["buffer"] = 60
        
        selection = self.mon_combo.get()
        if "DXCam" in selection:
            CONFIG["capture_backend"] = "DXCam"
            try:
                idx_str = selection.split("[ID=")[1].split("]")[0]
                CONFIG["dxcam_list_idx"] = int(idx_str)
            except: 
                CONFIG["dxcam_list_idx"] = 0
        else:
            CONFIG["capture_backend"] = "MSS"
            try:
                import re
                match = re.search(r"Screen (\d+)", selection)
                if match: 
                    CONFIG["monitor_id"] = int(match.group(1))
                else: 
                    CONFIG["monitor_id"] = 1
            except: 
                CONFIG["monitor_id"] = 1
            
        path = get_model_path(CONFIG["model"])
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Model file not found!\nExpected at:\n{path}\n\nPlease check 'models' folder.")
            return
        
        CONFIG["started"] = True
        self.root.destroy()

# ==========================================
# ⚙️ 采集逻辑
# ==========================================
def capture_thread_func():
    global running, thread_error, SCREEN_W, SCREEN_H, frame_queue
    backend = CONFIG["capture_backend"]
    print(f"[INFO] Capture Engine: {backend}")
    
    realtime_mode = (CONFIG["buffer"] == 1)

    try:
        if backend == "DXCam":
            list_idx = CONFIG.get("dxcam_list_idx", 0)
            if list_idx < len(DXCAM_MONITOR_LIST):
                target = DXCAM_MONITOR_LIST[list_idx]
                dev_idx, out_idx = target["device"], target["output"]
            else: 
                dev_idx, out_idx = 0, 0 

            print(f"[INFO] DXCam Init: GPU{dev_idx} Output{out_idx}")
            camera = dxcam.create(device_idx=dev_idx, output_idx=out_idx)
            camera.start(target_fps=60, video_mode=True)
            SCREEN_W, SCREEN_H = camera.width, camera.height

            while running:
                img = camera.get_latest_frame() 
                if img is not None:
                    if realtime_mode:
                        # 极速模式：强行清空队列
                        while not frame_queue.empty():
                            try: frame_queue.get_nowait()
                            except: break
                        frame_queue.put(img)
                    else:
                        if not frame_queue.full():
                            frame_queue.put(img)
                        else:
                            time.sleep(0.001)
                else:
                    time.sleep(0.001)
            camera.stop()

        else:
            # MSS
            sct = mss.mss()
            monitor_id = CONFIG["monitor_id"]
            if monitor_id >= len(sct.monitors): monitor_id = 1
            monitor = sct.monitors[monitor_id]
            SCREEN_W, SCREEN_H = monitor['width'], monitor['height']
            print(f"[INFO] MSS Started: {SCREEN_W}x{SCREEN_H}")

            while running:
                if realtime_mode:
                    sct_img = sct.grab(monitor)
                    while not frame_queue.empty():
                        try: frame_queue.get_nowait()
                        except: break
                    frame_queue.put(sct_img)
                else:
                    if not frame_queue.full():
                        sct_img = sct.grab(monitor)
                        frame_queue.put(sct_img)
                    else: 
                        time.sleep(0.002)

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

    grid_l = grid.clone()
    grid_r = grid.clone()
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

    pad_left = pad_w // 2
    pad_right = pad_w - pad_left
    pad_top = pad_h // 2
    pad_bottom = pad_h - pad_top
    return torch.nn.functional.pad(img_tensor, (pad_left, pad_right, pad_top, pad_bottom), mode='constant', value=0)

def draw_osd_full(img, fps, focus, str_val, buffer_size, gpu_load, ram_gb, cpu_percent, vram_gb, in_res, out_res):
    h, w = img.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    color = (0, 255, 127) 
    thick = 2
    fps_col = (0, 0, 255) if fps < 20 else color
    
    buf_str = f"{buffer_size}/{CONFIG['buffer']}"
    if CONFIG["buffer"] == 1:
        buf_str = "REALTIME"

    lines_l = [
        (f"FPS : {fps:.1f}", fps_col),
        (f"Buf : {buf_str}", color),
        (f"Str : {str_val:.3f}", color),
        (f"Foc : {focus:.2f}", color),
    ]
    lines_r = [
        (f"GPU : {gpu_load}%", color),
        (f"VRAM: {vram_gb:.1f}G", color),
        (f"CPU : {cpu_percent:.0f}%", color),
        (f"RAM : {ram_gb:.1f}G", color),
    ]
    
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
    
    res_info = f"In: {in_res[0]}x{in_res[1]} -> Out: {out_res[0]}x{out_res[1]}"
    eng_info = f"Engine: {CONFIG['capture_backend']} | Model: {CONFIG['model']}"
    cv2.putText(img, res_info, (20, h - 45), font, 0.5, (200, 200, 200), 1)
    cv2.putText(img, eng_info, (20, h - 20), font, 0.5, (255, 255, 255), 1)

def start_player():
    global running, DIVERGENCE, SWAP_EYES, thread_error, show_osd, SCREEN_W, SCREEN_H, frame_queue
    
    q_size = 1 if CONFIG["buffer"] == 1 else CONFIG["buffer"] + 5
    frame_queue = queue.Queue(maxsize=q_size)

    if HAS_NVML:
        try: 
            pynvml.nvmlInit()
        except: 
            pass

    model_type_map = {"Small": "Any_V2_S", "Base": "Any_V2_B", "Large": "Any_V2_L"}
    model_type = model_type_map[CONFIG["model"]]

    win_name = f"Realtime 3D Player ({CONFIG['capture_backend']})"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    
    t = threading.Thread(target=capture_thread_func)
    t.daemon = True
    t.start()
    
    print("[INFO] Initializing... Waiting for resolution...")
    for _ in range(50):
        if SCREEN_W > 0: break
        time.sleep(0.1)
    
    if SCREEN_W == 0: 
        SCREEN_W_SAFE, SCREEN_H_SAFE = 1920, 1080
    else: 
        SCREEN_W_SAFE, SCREEN_H_SAFE = SCREEN_W, SCREEN_H

    if CONFIG["res_mode"] == "Native":
        render_w, render_h = SCREEN_W_SAFE, SCREEN_H_SAFE
    elif CONFIG["res_mode"] == "1080p":
        render_w, render_h = 1920, 1080
    elif CONFIG["res_mode"] == "720p":
        render_w, render_h = 1280, 720
        
    cv2.resizeWindow(win_name, render_w, render_h)

    loading = np.zeros((render_h, render_w, 3), dtype=np.uint8)
    cv2.putText(loading, f"Loading {CONFIG['model']} Model...", (50, render_h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
    cv2.imshow(win_name, loading)
    cv2.waitKey(1)

    print(f"[INFO] Loading Model: {model_type}")
    
    # 动态加载
    model_wrapper = create_depth_model(model_type=model_type, load_path=get_model_path(CONFIG["model"]))
    # 如果 iw3 返回的是 wrapper，需要 load。如果 iw3 直接返回 model (取决于版本), 则不需要。
    # 你的原代码里是 model_wrapper.load(gpu=0)。
    # 这里我们为了兼容性，假设原逻辑正确。
    try:
        if hasattr(model_wrapper, "load"):
             model_wrapper.load(gpu=0)
        model = model_wrapper.model if hasattr(model_wrapper, "model") else model_wrapper
        model = model.to(DEVICE).half().eval()
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        running = False
        cv2.destroyAllWindows()
        return

    prev_depth = None
    current_focus = 0.5 
    frame_cnt = 0
    start_time = time.time()
    
    fps_val, gpu_load, cpu_val, ram_val, vram_val = 0.0, 0.0, 0.0, 0.0, 0.0

    print("[INFO] Player Started")
    
    while running:
        if thread_error: break
        try: 
            captured_data = frame_queue.get(timeout=0.01)
        except: 
            continue

        # 1. GPU 上传 (低 CPU 占用)
        if CONFIG["capture_backend"] == "DXCam":
            src_h, src_w = captured_data.shape[:2]
            img_gpu_raw = torch.from_numpy(captured_data).to(DEVICE, non_blocking=True)
            img_gpu_raw = img_gpu_raw.permute(2, 0, 1).unsqueeze(0).half() / 255.0
        else:
            raw_data = np.frombuffer(captured_data.raw, dtype=np.uint8)
            src_h, src_w = captured_data.height, captured_data.width
            img_bgra = torch.from_numpy(raw_data.copy()).view(src_h, src_w, 4)
            img_gpu_raw = img_bgra.to(DEVICE, non_blocking=True).permute(2, 0, 1).unsqueeze(0).half() / 255.0
            img_gpu_raw = img_gpu_raw[:, [2, 1, 0], :, :] 

        # 2. GPU 缩放
        if CONFIG["res_mode"] != "Native":
            if CONFIG["fill_mode"] == "Stretch":
                 img_render = torch.nn.functional.interpolate(img_gpu_raw, size=(render_h, render_w), mode='bilinear', align_corners=False)
                 final_h, final_w = render_h, render_w
            else:
                 scale = min(render_w / src_w, render_h / src_h)
                 fit_w, fit_h = int(src_w * scale), int(src_h * scale)
                 img_render = torch.nn.functional.interpolate(img_gpu_raw, size=(fit_h, fit_w), mode='bilinear', align_corners=False)
                 final_h, final_w = fit_h, fit_w
        else:
            img_render = img_gpu_raw
            final_h, final_w = render_h, render_w

        # 3. AI 推理
        ai_h = get_multiple_of_14(int(INFER_WIDTH * src_h / src_w))
        ai_w = get_multiple_of_14(INFER_WIDTH)
        img_ai = torch.nn.functional.interpolate(img_gpu_raw, size=(ai_h, ai_w), mode='bilinear', align_corners=False)

        with torch.inference_mode():
            raw_depth = model(img_ai)
            if isinstance(raw_depth, dict): raw_depth = list(raw_depth.values())[0]
            elif isinstance(raw_depth, (list, tuple)): raw_depth = raw_depth[0]
            
            d_min, d_max = raw_depth.min(), raw_depth.max()
            depth_norm = (raw_depth - d_min) / (d_max - d_min + 1e-6)
            
            h_d, w_d = depth_norm.shape[-2:]
            cy, cx = h_d // 2, w_d // 2
            rh, rw = int(h_d * CENTER_REGION), int(w_d * CENTER_REGION)
            center_crop = depth_norm[..., cy-rh:cy+rh, cx-rw:cx+rw]
            target_depth = torch.quantile(center_crop.float(), 0.8).item()
            current_focus = current_focus * (1 - FOCUS_EMA) + target_depth * FOCUS_EMA

            if prev_depth is None: prev_depth = raw_depth
            else: prev_depth = prev_depth * 0.7 + raw_depth * 0.3
            
            depth_render = torch.nn.functional.interpolate(
                prev_depth.unsqueeze(1), size=(final_h, final_w), mode='bilinear', align_corners=False
            )
            
            left, right = apply_smart_stereo_gpu(img_render, depth_render, DIVERGENCE, current_focus, SWAP_EYES)
            anaglyph = torch.cat((left[:, 0:1], right[:, 1:2], right[:, 2:3]), dim=1)
            
            if CONFIG["fill_mode"] == "Fit":
                anaglyph = add_black_borders_gpu(anaglyph, render_w, render_h)
            
            anaglyph = anaglyph.squeeze(0).permute(1, 2, 0)
            anaglyph = anaglyph[..., [2, 1, 0]]
            final_tensor = (anaglyph * 255).clamp(0, 255).to(torch.uint8)
            final_show = final_tensor.cpu().numpy()

        if show_osd:
            q_len = frame_queue.qsize()
            draw_osd_full(final_show, fps_val, current_focus, DIVERGENCE, q_len, gpu_load, ram_val, cpu_val, vram_val, (src_w, src_h), (render_w, render_h))

        cv2.imshow(win_name, final_show)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'): running = False; break
        elif key & 0xFF == ord('f'):
            is_full = cv2.getWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_FULLSCREEN
            cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL if is_full else cv2.WINDOW_FULLSCREEN)
        elif key & 0xFF == ord(']'): DIVERGENCE = min(5.0, DIVERGENCE + STEP_SIZE)
        elif key & 0xFF == ord('['): DIVERGENCE = max(0.0, DIVERGENCE - STEP_SIZE)
        elif key & 0xFF == ord(' '): SWAP_EYES = not SWAP_EYES
        elif key & 0xFF == 9: show_osd = not show_osd

        frame_cnt += 1
        if frame_cnt % 10 == 0:
            now = time.time()
            fps_val = 10 / (now - start_time)
            start_time = now
            gpu_load = get_gpu_load()
            if HAS_PSUTIL:
                cpu_val = psutil.cpu_percent()
                ram_val = psutil.virtual_memory().used / 1024**3
            vram_val = torch.cuda.memory_reserved(0) / 1024**3

    cv2.destroyAllWindows()
    if HAS_NVML: 
        try: 
            pynvml.nvmlShutdown()
        except: 
            pass