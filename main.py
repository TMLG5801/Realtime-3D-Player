import os
import sys
import tkinter as tk
import traceback

# ==========================================
# 🔧 环境引导逻辑
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "lib")
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
os.environ["NUNIF_HOME"] = LIB_DIR

# ==========================================
# 启动逻辑 (包含 ESC 返回循环)
# ==========================================
if __name__ == "__main__":
    print(f"[INFO] Initializing...")

    try:
        # 直接导入整合好的唯一核心
        from src import player_core
        
        while True:
            # 重置启动标志
            player_core.CONFIG["started"] = False
            root = tk.Tk()
            
            # 解决 DPI 缩放模糊问题
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except: pass
            
            app = player_core.LauncherApp(root)
            root.mainloop()
            
            # 检查是否正常点击了 START
            if not player_core.CONFIG.get("started", False):
                print("[INFO] Exiting...")
                break
                
            # 获取播放器的退出状态 (True=按了ESC, False=按了Q)
            should_restart = player_core.start_player()
            
            if not should_restart:
                print("[INFO] Quit signal received. Exiting.")
                break
            else:
                print("[INFO] Returning to Main Menu...")
                
    except ImportError as e:
        print(f"\n[ERROR] Missing libraries -> {e}")
        input("\nPress Enter to exit...")
    except Exception as e:
        print("\n[CRASH] Error details:")
        traceback.print_exc()
        input("\nPress Enter to exit...")