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
# 启动逻辑 (修复 ESC 返回菜单问题)
# ==========================================
if __name__ == "__main__":
    print(f"[INFO] 初始化环境...")
    
    try:
        from src import player_core
        
        # === 循环逻辑：GUI -> Player -> GUI ===
        while True:
            # 1. 重置启动标志位 (防止上一次的状态残留)
            player_core.CONFIG["started"] = False
            
            # 2. 启动 GUI 配置器
            root = tk.Tk()
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except: pass
            
            app = player_core.LauncherApp(root)
            root.mainloop() # 等待用户关闭窗口或点击开始

            # 3. 检查用户行为
            if not player_core.CONFIG.get("started", False):
                print("[INFO] 用户关闭了配置窗口，程序退出。")
                break # 用户直接点了 X，退出程序

            # 4. 启动播放器 (获取返回值)
            # start_player 返回 True 代表按了 ESC (重启)，返回 False 代表按了 Q (退出)
            should_restart = player_core.start_player()
            
            if not should_restart:
                print("[INFO] 收到退出信号，程序结束。")
                break
            else:
                print("[INFO] 正在返回主菜单...")
            
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        input("按回车键退出...")
    except Exception as e:
        print("\n❌ 程序崩溃：")
        traceback.print_exc()
        input("按回车键退出...")