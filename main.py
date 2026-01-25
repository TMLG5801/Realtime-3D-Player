import os
import sys
import tkinter as tk
from tkinter import messagebox

# ==========================================
# 🔧 环境引导逻辑 
# ==========================================
def setup_environment():
    # 1. 获取当前项目根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 将 'lib' 文件夹加入 Python 搜索路径
    # 这样代码里的 "import iw3" 就能直接找到 lib/iw3
    lib_dir = os.path.join(base_dir, "lib")
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    
    # 3. 检查模型是否存在
    models_dir = os.path.join(base_dir, "models")
    required_model = "depth_anything_v2_vitb.pth" # 默认至少要有一个 Base 模型
    model_path = os.path.join(models_dir, required_model)
    
    if not os.path.exists(model_path):
        root = tk.Tk()
        root.withdraw()
        msg = (
            "⚠️ 未检测到核心模型文件！\n\n"
            f"请确保 '{required_model}' 已放入 models 文件夹。\n"
            "如果你是从 GitHub 下载的项目，请查看 README 获取下载链接。"
        )
        messagebox.showerror("模型缺失", msg)
        sys.exit(1)

    return base_dir

# ==========================================
# 🚀 启动入口
# ==========================================
if __name__ == "__main__":
    print("[INFO] 正在初始化运行环境...")
    base_dir = setup_environment()
    
    print("[INFO] 环境加载成功，正在启动播放器核心...")
    
    # 这里的 import 必须在 setup_environment 之后
    # 因为 player_core 可能会引用 lib 里的 iw3
    try:
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