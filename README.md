# Realtime 3D Player (基于 AI 的实时 2D 转 3D 播放器)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![Powered By](https://img.shields.io/badge/Powered%20By-IW3%20%26%20DepthAnythingV2-orange.svg)](https://github.com/nagadomi/iw3)

这是一个基于 Python 的实时视频播放器，它利用最先进的 **Depth Anything V2** 模型，将原本平面的 2D 画面实时转换为 **3D SBS (Side-by-Side)** 格式。

配合 VR 头显（如 Quest 3/Pico 4）或 3D 显示器，你可以立刻享受震撼的立体视觉体验！✨

---

## 核心功能

*   **⚡ 实时转换**：利用 GPU 加速，实现低延迟的 2D 转 3D 推理。
*   **🎮 桌面/游戏采集**：支持 DXCam（极速）和 MSS（兼容）两种采集模式，可实时转换游戏画面。
*   **🛠️ 简易 GUI**：提供图形化界面，轻松调整分辨率、模型大小和采集源。
*   **🚀 一键部署**：内置自动化脚本，小白也能轻松配置复杂的 AI 环境。

---

## 硬件要求

*   **操作系统**: Windows 10 / 11
*   **显卡 (GPU)**: 强烈推荐 **NVIDIA 显卡** (支持 CUDA 加速)。
    *   *注意：使用集显或非 N 卡可能导致帧率极低或无法运行 DXCam 模式。*
*   **内存**: 建议 8GB 以上。
*   **Python**: 需要安装 Python 3.10 或更高版本。

---

## 安装与运行

我们为您准备了全自动的安装脚本，无需手动输入复杂命令。

### 第一步：准备文件
1. 下载本项目并解压。
2. 确保你的电脑已安装 [Python](https://www.python.org/downloads/) (安装时请勾选 **Add Python to PATH**)。

### 第二步：下载模型 (重要!)
由于 GitHub 文件大小限制，请手动下载核心模型文件，并放入项目的 `models` 文件夹中。

1. **下载地址**: [HuggingFace - Depth Anything V2](https://huggingface.co/depth-anything/Depth-Anything-V2-Small/tree/main) (或 Base/Large 版本)
2. **文件名**: 
   - `depth_anything_v2_vits.pth` (Small - 速度最快)
   - `depth_anything_v2_vitb.pth` (Base - 均衡推荐)
   - `depth_anything_v2_vitl.pth` (Large - 效果最好)
3. **放置位置**: 将下载的 `.pth` 文件直接放入 `models/` 文件夹。

### 第三步：一键启动
双击运行根目录下的 **`install_and_run.bat`**。

*   **首次运行**: 脚本会自动创建虚拟环境并下载 2GB+ 的依赖库（包括 GPU 版 PyTorch），请耐心等待。
*   **后续运行**: 双击即可秒开。

---

## 操作快捷键

程序运行并弹出 3D 画面后，你可以使用以下快捷键：

| 按键 | 功能 |
| :--- | :--- |
| **Q** | 退出程序 |
| **F** | 全屏 / 退出全屏 |
| **Space (空格)** | 交换左右眼 (Swap Left/Right) |
| **]** | 增加 3D 强度 (更立体) |
| **[** | 减小 3D 强度 (更扁平) |
| **Tab** | 显示 / 隐藏 OSD 数据面板 |

---

## 常见问题 (FAQ)

**Q: 运行 `install_and_run.bat` 闪退怎么办？**
A: 请右键编辑 bat 文件，查看最后是否有报错。通常是因为未安装 Python 或者网络连接超时。

**Q: 提示 "Model file not found"？**
A: 请检查 `models` 文件夹里是否真的有 `.pth` 文件。如果没有，请参考“安装步骤”去下载。

**Q: 笔记本电脑报错 "DXCam Error"？**
A: DXCam 只能捕捉连接在独显上的屏幕。如果你是笔记本（核显输出画面），请在启动界面的 "Capture Engine" 中选择 **MSS** 模式。

**Q: 画面很卡，FPS 很低？**
A: 
1. 确保程序运行在 NVIDIA 独显上。
2. 在启动界面尝试选择 **Small** 模型。
3. 降低分辨率选项（如选择 720p）。

---

## 开发者指南 (Manual Setup)

如果你想手动配置环境，请参考以下步骤：

```bash
# 1. 创建环境
python -m venv venv
.\venv\Scripts\activate

# 2. 安装 PyTorch (GPU 版 - CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. 安装其他依赖
pip install -r requirements.txt

# 4. 运行
python main.py