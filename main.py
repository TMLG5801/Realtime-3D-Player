import os
import sys
import tkinter as tk
from tkinter import messagebox

# ==========================================
# 🔧 环境引导与自动下载逻辑
# ==========================================
def setup_environment():
    # 1. 获取项目根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 挂载 lib 目录
    lib_dir = os.path.join(base_dir, "lib")
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    
    # 3. 检查模型文件夹
    models_dir = os.path.join(base_dir, "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    # === 定义模型清单 (名字, 文件名, HuggingFace仓库ID) ===
    model_list = [
        {
            "name": "Small (快速版)",
            "filename": "depth_anything_v2_vits.pth",
            "repo_id": "depth-anything/Depth-Anything-V2-Small"
        },
        {
            "name": "Base (均衡版)",
            "filename": "depth_anything_v2_vitb.pth",
            "repo_id": "depth-anything/Depth-Anything-V2-Base"
        },
        {
            "name": "Large (画质版)",
            "filename": "depth_anything_v2_vitl.pth",
            "repo_id": "depth-anything/Depth-Anything-V2-Large"
        }
    ]

    print("\n" + "="*60)
    print("[INFO] 正在检查 AI 模型完整性...")
    print("="*60)

    # 4. 循环检查并下载
    try:
        # 预先检查是否有 huggingface_hub
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            print("📦 正在安装下载工具 (huggingface_hub)...")
            os.system(f"{sys.executable} -m pip install huggingface_hub")
            from huggingface_hub import hf_hub_download

        for model in model_list:
            file_path = os.path.join(models_dir, model['filename'])
            
            if not os.path.exists(file_path):
                print(f"\n⬇️  正在下载: {model['name']}")
                print(f"    文件名: {model['filename']}")
                print("    (第一次下载可能需要几分钟，请不要关闭窗口...)")
                
                hf_hub_download(
                    repo_id=model['repo_id'],
                    filename=model['filename'],
                    local_dir=models_dir,
                    local_dir_use_symlinks=False # 下载实体文件
                )
                print(f"✅ {model['name']} 下载完成！")
            else:
                print(f"✅ 已存在: {model['name']}")

    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        msg = (
            f"❌ 自动下载模型失败！\n\n错误信息: {e}\n\n"
            "可能原因：网络连接不稳定或磁盘空间不足。\n"
            "请检查网络后重试。"
        )
        messagebox.showerror("下载错误", msg)
        sys.exit(1)

    print("\n" + "="*60)
    print("[INFO] 所有模型准备就绪！")
    print("="*60 + "\n")
    
    return base_dir

# ==========================================
# 🚀 启动入口
# ==========================================
if __name__ == "__main__":
    print("[INFO] 正在初始化运行环境...")
    
    try:
        base_dir = setup_environment()
        
        print("[INFO] 环境完整，正在启动播放器 GUI...")
        
        # 这里的 import 必须在 setup 之后
        from src import player_core
        
        # 启动 GUI
        root = tk.Tk()
        app = player_core.LauncherApp(root)
        root.mainloop()
        
        # GUI 关闭后，如果用户点了 Start，则启动循环
        if player_core.running and player_core.CONFIG.get("started", False):
            player_core.start_player()
            
    except ImportError as e:
        print(f"❌ 启动失败: 缺少依赖库 -> {e}")
        input("按回车键退出...")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ 发生未知错误 -> {e}")
        input("按回车键退出...")