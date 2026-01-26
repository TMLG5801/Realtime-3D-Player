# Realtime 3D Player (2D to 3D Converter)

[![Python Version](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%2012.1-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![NVIDIA](https://img.shields.io/badge/Optimized%20for-NVIDIA%20RTX-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Model](https://img.shields.io/badge/Model-Depth%20Anything%20V2-FF9D00?style=flat-square&logo=huggingface&logoColor=white)](https://github.com/DepthAnything/Depth-Anything-V2)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![GitHub License](https://img.shields.io/github/license/TMLG5801/Realtime-3D-Player?style=flat-square&color=blue)](LICENSE)

Please scroll down for the English version.

## 一、安装与运行指南

本项目采用自动化脚本部署，请严格按照以下步骤操作。

### 1. 前置准备
**必须安装 Python 3.10！** (3.11 也可以，但推荐 3.10 以获得最佳兼容性)

 [点击下载 Python 3.10 (Windows 64位)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
 
 **⚠️ 重要：** 安装时务必勾选底部的 **"Add Python 3.10 to PATH"** (添加到环境变量)，否则脚本无法运行！
    (如果不确定是否安装成功，请打开 CMD 输入 `python --version` 检查)

**硬件要求：** 仅支持 NVIDIA 显卡，且需安装最新的显卡驱动。

### 2. 一键安装环境 (仅首次需要)
双击项目目录下的 **`install_env.bat`**。

*   脚本会自动创建虚拟环境 (venv) 并下载 GPU 版 PyTorch 和其他依赖库。
*   **注意**：此过程需要下载约 5GB 数据，请耐心等待直到窗口提示“环境安装完成”或自动关闭。

### 3. 启动程序
双击 **`run_app.bat`** 即可启动。

*   **自动模型下载**：首次启动时，程序会自动检测并下载 **Small / Base / Large** 全套模型（共约 1.7GB）。
    *   *请保持网络畅通，下载完成后 GUI 界面会自动弹出。*
*   **后续运行**：环境和模型准备好后，直接双击此脚本即可秒开。

### 4. 项目目录结构说明
为了方便维护，以下是项目的主要文件结构：

| 文件/文件夹 | 说明 |
| :--- | :--- |
| `install_env.bat` | 🛠️ **一键安装**：自动部署 Python 虚拟环境与 GPU 依赖 |
| `run_app.bat` | 🚀 **一键启动**：用户日常使用的启动脚本，自动激活环境 |
| `main.py` | 🏁 **程序引导**：项目入口文件，负责环境检查与模块加载 |
| `src/` | **核心源码层**：包含所有 Python 源代码 |
| ├── `player_core.py` | 🧠 **核心引擎**：集成了 GUI 设置、画面采集、AI 推理与渲染逻辑 |
| `models/` | 📦 **模型仓库**：存放自动下载的 Small/Base/Large 模型权重文件 |
| `lib/` | 📚 **本地依赖库**：包含 iw3 (核心算法)、nunif (框架) 和 dxcam (采集) |
| `venv/` | 🐍 **运行环境**：安装脚本自动生成的 Python 虚拟环境目录 |

---

## 二、项目介绍

本项目是一个基于 Python 的实时视频/桌面转 3D 播放器。它利用 **Depth Anything V2** 模型，将原本平面的 2D 画面实时推理为深度图，并渲染为 **视差3D** 格式。

**主要特性：**

*   **实时转换**：利用 TensorRT/CUDA 加速，实现低延迟的 2D 转 3D 推理。
*   **桌面/采集**：集成 DXCam（极速）和 MSS（兼容）两种采集引擎，支持实时转换画面。
*   **全自动部署**：内置 Python 脚本自动处理依赖安装与模型下载。
*   **可视化控制**：提供 GUI 界面调节分辨率、模型大小 (Small/Base/Large) 及 3D 强度。

---

## 三、环境依赖

**硬件要求**

*   **GPU**: NVIDIA GeForce RTX 系列显卡。
*   **系统**: Windows 10 / 11 (64-bit)。
*   **外设**: 至少两块屏幕，一块用于原始图像采集，一块用于显示，以及一幅色差3D眼镜。

**软件要求**

*   **Python**: 3.10+ (必需)。
*   **CUDA**: 程序会自动安装带有 CUDA 12.1 支持的 PyTorch，无需手动安装 CUDA Toolkit。

---

## 四、详细使用指南

### 1. 启动器 (GUI) 参数说明
启动程序后，你会看到配置界面，各项参数含义如下：

* **Capture Engine (采集引擎)**:
    * **DXCam**: (推荐) 仅支持 NVIDIA 显卡。速度极快，延迟极低。
    * **MSS**: 兼容性模式。如果 DXCam 无法使用（如多显卡冲突），请选择此项。
* **AI Model (模型选择)**:
    * **Small**: 速度最快，显存占用最低，立体感适中。
    * **Base**: 平衡模式，推荐大多数配置使用。
    * **Large**: 效果最好，边缘最清晰，但计算压力最大。
* **Fill Mode (填充模式)**:
    * **Fit**: 保持原始画面比例，不足部分填充黑边（适合看电影）。
    * **Stretch**: 强制拉伸画面填满窗口（适合全屏玩游戏）。
* **Resolution (分辨率)**:
    * **Native**: 使用屏幕原始分辨率进行推理，画质无损，零缩放开销。
    * **1080P / 720P**: 强制压缩分辨率，可显著降低显卡负载，适合配置较低的设备。
* **Buffer Size (缓冲区)**:
    * 设置为 **0** 或 **1** 即为 **Realtime (极速模式)**，延迟最低。
    * 调大数值可以缓解画面掉帧，但会增加延迟。

### 2. 播放控制与快捷键
程序运行并弹出 3D 画面后，焦点需在播放窗口内：

| 按键 | 功能 | 说明 |
| :--- | :--- | :--- |
| **ESC** | **返回菜单** | 停止播放并返回配置界面 (保留上次设置) |
| **Q** | **退出程序** | 直接彻底关闭程序 |
| **Space** | 交换左右眼 | 如果感觉 3D 前后颠倒，按此键修正 |
| **]** | 增加强度 | 增强 3D 景深感 (物体更突出) |
| **[** | 减小强度 | 减弱 3D 景深感 (画面更扁平) |
| **Tab** | OSD 开关 | 显示/隐藏左上角的 FPS 和参数面板 |
| **F** | 全屏切换 | 切换窗口化/全屏显示 |

---

## 五、技术原理与开发计划

### 1. 自动对焦机制
本项目目前的自动对焦采用的是 **中心加权统计方案**。

* **实现原理**：截取画面中心 **25%** 的区域，计算该区域深度图的 **80% 分位数值** 作为对焦平面，并使用 **EMA (指数移动平均)** 进行时域平滑。
* **设计权衡**：
    * ✅ **速度极快**：纯数学统计，耗时 **<0.5ms**，对 GPU 几乎无负载。
    * ✅ **实时性**：在必须保证流畅的前提下，这是目前性价比最高的方案。
    * ❌ **局限性**：无法识别画面边缘的主体（如构图偏左的人物），通过“鼠标点击对焦”可解决此问题。

*为什么不使用人脸识别/显著性检测？*
> 引入额外的检测模型（如 YOLO 或 U2Net）会增加 10-30ms 的推理延迟，这将严重破坏实时播放器的流畅度。目前的方案是“性能优先”的最优解。

### 2. 未来更新计划
欢迎社区贡献代码！以下是我们计划改进的方向：

- [ ] **交互优化**：添加 **“鼠标点击对焦”** 功能，允许用户手动指定对焦点。
- [ ] **算法优化**：实现动态对焦区域（例如根据深度直方图自动调整中心采样范围）。
- [ ] **性能监控**：更详细的逐层耗时统计面板。

---

## I. Installation and Running Guide

This project uses automated deployment scripts. Please follow the steps below precisely.

### 1. Prerequisites
**Python 3.10 must be installed!** (3.11 works too, but 3.10 is recommended).

[Click to download Python 3.10 (Windows 64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)

**⚠️ Important:** Check the **"Add Python 3.10 to PATH"** option at the bottom during installation!

**Hardware:** NVIDIA GPU only. Please ensure your graphics drivers are up to date.

### 2. Install Environment (First Time Only)
Double-click **`install_env.bat`** in the project directory.

*   The script will automatically create a virtual environment (venv) and download the GPU version of PyTorch and other dependencies.
*   **Note**: This process involves downloading 5GB of data. Please wait until the window indicates completion or closes automatically.

### 3. Start Application
Double-click **`run_app.bat`** to launch.

*   **Auto Model Download**: On the first launch, the program will automatically detect and download the **Small / Base / Large** model set (approx. 1.7GB).
    *   *The GUI will appear automatically once the download is complete.*
*   **Subsequent Runs**: Just double-click this script to run instantly.

### 4. Project Directory Structure Explanation
For ease of maintenance, the following is the main file structure of the project:

| File/Directory | Description |
| :--- | :--- |
| `install_env.bat` | 🛠️ **One-Click Install**: Auto-deploys venv and GPU dependencies |
| `run_app.bat` | 🚀 **One-Click Run**: Daily startup script, auto-activates environment |
| `main.py` | 🏁 **Entry Point**: Handles environment checks and module loading |
| `src/` | **Source Code Layer**: Contains all Python source files |
| ├── `player_core.py` | 🧠 **Core Engine**: Integrates GUI, Capture, AI Inference, and Rendering |
| `models/` | 📦 **Model Zoo**: Stores downloaded Small/Base/Large model weights |
| `lib/` | 📚 **Local Libs**: Contains modified iw3, nunif, and dxcam libraries |
| `venv/` | 🐍 **Runtime Env**: The virtual environment generated by the install script |

---

## II. Project Introduction

This project is a Python-based real-time 2D-to-3D video player. It leverages the **Depth Anything V2** model to infer depth maps from flat 2D images in real-time and renders them into **Anaglyph 3D** format.

**Key Features:**

*   **Real-time Conversion**: Uses TensorRT/CUDA acceleration for low-latency inference.
*   **Screen Capture:** Integrates two capture engines: DXCam (high-speed) and MSS (compatible), supporting real-time screen conversion.
*   **Fully Automated**: Built-in scripts handle dependency installation and model downloading automatically.
*   **GUI Control**: Easy-to-use interface to adjust resolution, model size, and 3D strength.

---

## III. Environmental Dependencies

**Hardware Requirements**

*   **GPU**: NVIDIA GeForce RTX series recommended.
*   **OS**: Windows 10 / 11 (64-bit).
*   **Peripherals**: At least two screens are required, one for original image acquisition and one for display,and a pair of Anaglyph 3D Glasses.

**Software Requirements**

*   **Python**: 3.10+ (Required).
*   **CUDA**: The program automatically installs PyTorch with CUDA 12.1 support; manual CUDA Toolkit installation is not required.

---

## IV. Detailed User Guide

### 1. Launcher (GUI) Parameter Explanation
After launching the program, you will see the configuration interface. The meaning of each parameter is as follows:

* **Capture Engine**:
* **DXCam**: (Recommended) Only supports NVIDIA graphics cards. Extremely fast speed and very low latency. 
* **MSS**: Compatibility mode. If DXCam cannot be used (e.g., due to multi-GPU conflicts), please select this option.
* **AI Model**:
* **Small**: Fastest speed, lowest VRAM usage, moderate 3D effect. 
* **Base**: Balanced mode, recommended for most configurations. 
* **Large**: Best effect, sharpest edges, but highest computational load.
* **Fill Mode**:
* **Fit**: Maintains the original aspect ratio, filling the remaining space with black bars (suitable for watching movies). 
* **Stretch**: Forces stretching the image to fill the window (suitable for full-screen gaming).
* **Resolution**:
* **Native**: (Recommended for RTX 30/40 series) Uses the screen's native resolution for inference, resulting in lossless image quality and zero scaling overhead. 
* **1080P / 720P**: Forces resolution compression, which can significantly reduce the graphics card load, suitable for lower-end devices.
* **Buffer Size**:
* Setting to **0** or **1** is **Realtime (Extreme Speed ​​Mode)**, with the lowest latency. 
* Increasing the value can alleviate frame drops, but will increase latency. ### 2. Playback Controls and Keyboard Shortcuts
After the program runs and the 3D image appears, the focus must be on the playback window:

| Key | Function | Description |
| :--- | :--- | :--- |
| **ESC** | **Return to Menu** | Stops playback and returns to the configuration interface (retains previous settings) |
| **Q** | **Exit Program** | Closes the program completely |
| **Space** | Swap Left/Right Eyes | If the 3D image appears inverted, press this key to correct it |
| **]** | Increase Intensity | Enhances the 3D depth perception (objects appear more prominent) |
| **[** | Decrease Intensity | Reduces the 3D depth perception (the image appears flatter) |
| **Tab** | OSD Toggle | Shows/hides the FPS and parameter panel in the upper left corner |
| **F** | Fullscreen Toggle | Switches between windowed and fullscreen display |

---

## V. Technical Principles & Roadmap

### 1. Autofocus Mechanism
The project currently utilizes **Center-Weighted Statistical Autofocus**.

* **How it works**: Crops the center **25%** of the depth map, calculates the **80th percentile** depth value as the focal plane, and applies **EMA (Exponential Moving Average)** for smoothing.
* **Design Trade-off**:
    * ✅ **Ultra Fast**: Pure mathematical statistics, taking **<0.5ms**, with negligible GPU load.
    * ✅ **Real-time**: Essential for maintaining high FPS.
    * ❌ **Limitation**: Cannot focus on off-center subjects automatically.

*Why not use Face Detection or Saliency Detection?*
> Adding extra detection models (like YOLO or U2Net) would introduce 10-30ms of latency, severely impacting the fluidity of a real-time player. The current approach is the optimal solution for "Performance First".

### 2. Roadmap
Contributions are welcome! Here is the plan for future updates:

- [ ] **Interaction**: Implement **"Tap to Focus"** (click on screen to set focal plane manually).
- [ ] **Algorithm**: Dynamic focus region (adjust crop size based on depth histogram).
- [ ] **Profiling**: More detailed performance statistics panel.

---

## 🤝 Credits & License

This project is based on the following amazing open-source projects:

*   **[iw3](https://github.com/nagadomi/nunif)** by nagadomi - Core 3D logic and nunif framework.
*   **[Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)** - State-of-the-art Monocular Depth Estimation.
*   **[DXCam](https://github.com/ra1nty/DXCam)** - High-performance Windows screen capture.

Licensed under the **MIT License**.
