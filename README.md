# Realtime 3D Player (2D to 3D Converter)

[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python Version](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%2012.1-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![NVIDIA](https://img.shields.io/badge/Optimized%20for-NVIDIA%20RTX-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Model](https://img.shields.io/badge/Model-Depth%20Anything%20V2-FF9D00?style=flat-square&logo=huggingface&logoColor=white)](https://github.com/DepthAnything/Depth-Anything-V2)

Please scroll down for the English version.

<p align="center">
  <img width="5120" height="1600" alt="540458626-313537f7-faa2-4802-b0d2-8c65dc7fb617" src="https://github.com/user-attachments/assets/9fcb4703-b4b7-484e-9c8a-1e47a21b7895" />
  <br>
  <sub>👆 实机演示截图 (Real-time Demo) | ⚡ 测试环境: RTX 3080 | Model: Large | Res: 1080P</sub>
</div>
</p>

[演示视频(Demo video)](https://www.bilibili.com/video/BV1uSP2zgEW5/)

## 一、安装与运行指南

本项目采用自动化脚本部署，请严格按照以下步骤操作。

### 1. 前置准备
**必须安装 Python 3.10！** (3.11 也可以，但推荐 3.10 以获得最佳兼容性)

 [点击下载 Python 3.10 (Windows 64位)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
 
 **⚠️ 重要：** 安装时务必勾选底部的 **"Add Python 3.10 to PATH"** (添加到环境变量)，否则脚本无法运行！
    (如果不确定是否安装成功，请打开 CMD 输入 `python --version` 检查)

**选择安装OBS**

[点击下载 OBS (Windows)](https://cdn-fastly.obsproject.com/downloads/OBS-Studio-32.0.4-Windows-x64-Installer.exe)

**硬件要求：** 一幅红蓝3D眼镜！！！必须使用 NVIDIA RTX系列显卡，且需安装最新的显卡驱动。

### 2. 一键安装环境 (仅首次需要)
双击项目目录下的 **`install_env.bat`**。

* 脚本会自动创建虚拟环境 (venv) 并下载 GPU 版 PyTorch 和其他依赖库。
* **注意**：此过程需要下载约 5GB 数据，请耐心等待直到窗口提示“环境安装完成”或自动关闭。

### 3. 启动程序
双击 **`run_app.bat`** 即可启动。

* **自动模型下载**：首次启动时，程序会自动检测并下载 **Small / Base / Large** 全套模型（共约 1.7GB）。
    * *请保持网络畅通，下载完成后 GUI 界面会自动弹出。*
* **后续运行**：环境和模型准备好后，直接双击此脚本即可秒开。

### 4. 项目目录结构说明
为了方便维护，以下是项目的主要文件结构：

| 文件/文件夹 | 说明 |
| :--- | :--- |
| `install_env.bat` | 🛠️ **一键安装**：自动部署 Python 虚拟环境与 GPU 依赖 |
| `run_app.bat` | 🚀 **一键启动**：用户日常使用的启动脚本，自动激活环境 |
| `main.py` | 🏁 **程序引导**：项目入口文件，负责环境检查与模块加载 |
| `src/` | **核心源码层**：包含所有 Python 源代码 |
| ├── `player_core.py` | 🧠 **核心引擎**：集成了 GUI、OBS采集、AI 推理与 3D 渲染逻辑 |
| `models/` | 📦 **模型仓库**：存放自动下载的 Small/Base/Large 模型权重文件 |
| `lib/` | 📚 **本地依赖库**：包含 iw3 (核心算法)、nunif (框架) 和 dxcam (采集) |
| `venv/` | 🐍 **运行环境**：安装脚本自动生成的 Python 虚拟环境目录 |

---

## 二、项目介绍

本项目是一个基于 Python 的实时视频/桌面转 3D 播放器。它利用 **Depth Anything V2** 模型，将原本平面的 2D 画面实时推理为深度图，并渲染为 **色差式3D** 格式。

**主要特性：**

* **实时转换**：利用 TensorRT/CUDA 加速，实现低延迟的 2D 转 3D 推理。
* **多重采集引擎**：集成 OBS 虚拟摄像机（支持后台窗口抓取）、DXCam（桌面极速）和 MSS。
* **全自动部署**：内置 Python 脚本自动处理依赖安装与模型下载。
* **可视化控制**：提供 GUI 界面调节分辨率、模型大小及 3D 强度。

---

## 三、环境依赖

**硬件要求**

* **GPU**: NVIDIA GeForce RTX 系列显卡。
* **系统**: Windows 10 / 11 (64-bit)。
* **外设**: 建议配备双屏或配合 OBS 使用后台采集。

**软件要求**

* **Python**: 3.10+ (必需)。
* **CUDA**: 程序会自动安装带有 CUDA 12.1 支持的 PyTorch，无需手动安装 CUDA Toolkit。

---

## 四、详细使用指南

### 1. 启动器 (GUI) 参数说明
启动程序后，你会看到配置界面，各项参数含义如下：

* **Capture Engine (采集引擎)**:
    * **Camera (OBS)**: (新增/推荐) 通过配合 OBS 虚拟摄像机，可完美抓取被遮挡的后台窗口，或接入 PS5/Switch 视频采集卡。
    * **DXCam**: 仅支持 NVIDIA 显卡。桌面捕获速度极快，延迟极低。
    * **MSS**: 兼容性桌面捕获模式。
* **AI Model (模型选择)**:
    * **Small**: 速度最快，显存占用最低，立体感适中。
    * **Base**: 平衡模式，推荐大多数配置使用。
    * **Large**: 效果最好，边缘最清晰，但计算压力最大。
* **Fill Mode (填充模式)**:
    * **Fit**: 保持原始画面比例，不足部分填充黑边（适合看电影）。
    * **Stretch**: 强制拉伸画面填满窗口（适合全屏玩游戏）。
* **Target Resolution (目标分辨率)**:
    * 支持从 **4K (3840x2160)** 到 **480p** 的主流下拉选项。程序会自动向 OBS 请求对应画质，并点对点输出精准大小的渲染窗口。
* **Buffer Size (缓冲区)**:
    * 设置为 **0** 即为 **Realtime (极速模式)**，延迟最低。
 
### 2. OBS 虚拟摄像机使用指南
本项目的 `Camera` 引擎支持读取 OBS 虚拟摄像机。通过此工作流，你可以**将播放着电影的浏览器放在后台或副屏，甚至被其他窗口遮挡**，程序依然能渲染 3D 画面。

**OBS 配置步骤：**
1. **添加采集源**：在 OBS 左下角的“来源”面板点击 `+`，选择 **窗口采集 (Window Capture)**，选中你的浏览器或播放器窗口。
2. **解决硬件加速白屏**：在采集属性中，务必将 **采集方法 (Capture Method)** 更改为 **Windows 10 (1903 及更高版本)**。这能穿透浏览器的硬件加速强制抓取画面。
3. **解决标题变化失效**：在采集属性中，将 **窗口匹配优先级 (Window Match Priority)** 更改为 **匹配标题，否则查找相同可执行程序的窗口**。这样即使视频名字变了，OBS 也能记住浏览器进程。
4. **统一分辨率**：进入 OBS **设置 -> 视频**，将 **基础(画布)分辨率** 和 **输出(缩放)分辨率** 都统一设置为你期望的画质（建议 `1920x1080`）。
5. **画面铺满**：在 OBS 预览区画面上右键 -> **变换 -> 比例适配屏幕** (快捷键 Ctrl+F)。
6. **启动**：点击 OBS 右下角的 **启动虚拟摄像机 (Start Virtual Camera)**。最后在 3D Player 的 GUI 中选择 `Camera` 引擎即可。

### 3. 播放控制与快捷键
程序运行并弹出 3D 画面后，焦点需在播放窗口内：

| 按键 | 功能 | 说明 |
| :--- | :--- | :--- |
| **ESC** | **返回菜单** | 关闭当前播放器，并重新呼出 GUI 配置界面 |
| **Q** | **退出程序** | 直接彻底关闭整个程序 |
| **Space** | 交换左右眼 | 如果感觉 3D 前后颠倒，按此键修正 |
| **]** | 增加强度 | 增强 3D 景深感 (物体更突出) |
| **[** | 减小强度 | 减弱 3D 景深感 (画面更扁平) |
| **Tab** | OSD 开关 | 显示/隐藏左上角的 FPS 和硬件参数面板 |
| **F** | 全屏切换 | 进入无边框全屏模式 (完美铺满屏幕) |

---

## 五、技术原理与开发计划

### 1. 技术核心解读
* **AI Depth Vision (单目深度估算)**：采用 Depth Anything V2 模型与 CUDA 加速，毫秒级解析画面空间透视，实时生成高精度深度图，为 2D 转 3D 提供底层视觉基础。
* **Dynamic Pixel Shifting (智能立体渲染)**：提取中心深度构建虚拟对焦面，利用网格采样算法进行动态像素偏移。根据深度精确重映射左右眼图像，实时合成符合双目视差且无眩晕感的 3D 画面。
* **Zero-Copy Pipeline (零拷贝高性能流水线)**：极致优化显存带宽，缩放与色彩转换全封装于 GPU 完成。底层将浮点张量直接压缩为字节数据，使总线回传压力骤降 75%，保障流畅实时转换。

### 2. 未来更新计划 (Roadmap)
欢迎社区参与贡献代码！以下是我计划改进的方向：
- [ ] **交互优化**：添加 **“鼠标点击对焦 (Tap to Focus)”** 功能，允许用户手动指定对焦点。
- [ ] **算法优化**：实现动态对焦区域（例如根据深度直方图自动调整中心采样范围）。
- [ ] **VR 支持**：接入 SteamVR 接口，直接输出到 VR 头显。
- [ ] **性能监控**：更详细的逐层耗时统计面板。

---

## 六、数据流

<img width="2877" height="8191" alt="GPU VRAM Processing Pipeline-2026-03-05-195040" src="https://github.com/user-attachments/assets/cdb38e52-3e3d-4cb6-80e6-02405926e5c6" />

---
## I. Installation and Running Guide

This project uses automated deployment scripts. Please follow the steps below precisely.

### 1. Prerequisites
**Python 3.10 must be installed!** (3.11 works too, but 3.10 is recommended).

[Click to download Python 3.10 (Windows 64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)

**⚠️ Important:** Check the **"Add Python 3.10 to PATH"** option at the bottom during installation!

**Optional OBS Installation**

[Click to download OBS (Windows)](https://cdn-fastly.obsproject.com/downloads/OBS-Studio-32.0.4-Windows-x64-Installer.exe)

**Hardware:** A pair of Red-Blue 3D Glasses!!!NVIDIA RTX series graphics cards are required, and the latest graphics card drivers must be installed.

### 2. Install Environment (First Time Only)
Double-click **`install_env.bat`** in the project directory.

* The script will automatically create a virtual environment (venv) and download the GPU version of PyTorch and other dependencies.
* **Note**: This process involves downloading 5GB+ of data. Please wait until the window indicates completion or closes automatically.

### 3. Start Application
Double-click **`run_app.bat`** to launch.

* **Auto Model Download**: On the first launch, the program will automatically detect and download the **Small / Base / Large** model set.
* **Subsequent Runs**: Just double-click this script to run instantly.

### 4. Project Directory Structure
| File/Directory | Description |
| :--- | :--- |
| `install_env.bat` | 🛠️ **One-Click Install**: Auto-deploys venv and GPU dependencies |
| `run_app.bat` | 🚀 **One-Click Run**: Daily startup script, auto-activates environment |
| `main.py` | 🏁 **Entry Point**: Handles environment checks and module loading |
| `src/` | **Source Code Layer**: Contains all Python source files |
| ├── `player_core.py` | 🧠 **Core Engine**: Integrates GUI, OBS Capture, AI Inference, and Rendering |
| `models/` | 📦 **Model Zoo**: Stores downloaded Small/Base/Large model weights |
| `lib/` | 📚 **Local Libs**: Contains modified iw3, nunif, and dxcam libraries |
| `venv/` | 🐍 **Runtime Env**: The virtual environment generated by the install script |

---

## II. Project Introduction

This project is a Python-based real-time 2D-to-3D video player. It leverages the **Depth Anything V2** model to infer depth maps from flat 2D images in real-time and renders them into **Anaglyphic 3D** format.

**Key Features:**

* **Real-time Conversion**: Uses TensorRT/CUDA acceleration for low-latency inference.
* **Multi-Capture Engine:** Integrates OBS Virtual Camera (for background window capture), DXCam, and MSS.
* **Fully Automated**: Built-in scripts handle dependency installation and model downloading automatically.
* **GUI Control**: Easy-to-use interface to adjust resolution, model size, and 3D strength.

---

## III. Environmental Dependencies

**Hardware Requirements**
* **GPU**: NVIDIA GeForce RTX series graphics cards are required.
* **OS**: Windows 10 / 11 (64-bit).

**Software Requirements**
* **Python**: 3.10+ (Required).
* **CUDA**: The program automatically installs PyTorch with CUDA 12.1 support.

---

## IV. Detailed User Guide

### 1. Launcher (GUI) Parameters
* **Capture Engine**:
  * **Camera (OBS)**: (New/Recommended) Captures background/occluded browser windows flawlessly via OBS Virtual Camera, or connects to capture cards (PS5/Switch).
  * **DXCam**: Extremely fast desktop capture. NVIDIA only.
  * **MSS**: Compatibility desktop capture mode.
* **AI Model**:
  * **Small**: Fastest speed, lowest VRAM usage.
  * **Base**: Balanced mode, recommended.
  * **Large**: Best effect, sharpest edges, but highest load.
* **Fill Mode**:
  * **Fit**: Maintains aspect ratio, adds black bars (for movies).
  * **Stretch**: Forces stretching to fill the window (for games).
* **Target Resolution**:
  * Dropdown menu supporting resolutions from **4K** to **480p**. Automatically requests the matching quality from OBS.
* **Buffer Size**:
  * **0** is **Realtime Mode**, offering the lowest latency.

### 3. OBS Virtual Camera Guide
The `Camera` engine in this project supports OBS Virtual Camera. With this workflow, you can **put your browser/movie player in the background or on a secondary monitor**, and still render a 3D view on your main monitor.

**OBS Setup Steps (One-time setup):**
1. **Add Source**: Click `+` in the OBS "Sources" panel, select **Window Capture**, and choose your browser/player window.
2. **Fix Hardware Acceleration Blackscreen**: In the properties, you MUST change the **Capture Method** to **Windows 10 (1903 and up)**. This forces the capture of hardware-accelerated windows.
3. **Fix Changing Titles**: Change the **Window Match Priority** to **Match title, otherwise find window of same executable**. This ensures OBS keeps tracking the browser even if the video title changes .
4. **Sync Resolution**: Go to OBS **Settings -> Video**, and set both **Base (Canvas) Resolution** and **Output (Scaled) Resolution** to your desired quality (e.g., `1920x1080`).
5. **Fit Screen**: Right-click the video feed in the preview area -> **Transform -> Fit to screen** (Ctrl+F).
6. **Start**: Click **Start Virtual Camera** in the bottom right corner of OBS. Finally, select the `Camera` engine in the 3D Player GUI.

### 2. Controls and Shortcuts
| Key | Function | Description |
| :--- | :--- | :--- |
| **ESC** | **Menu** | Returns to the GUI configuration interface |
| **Q** | **Quit** | Closes the program completely |
| **Space** | Swap Eyes | Corrects inverted 3D depth perception |
| **]** | Increase | Enhances the 3D depth perception |
| **[** | Decrease | Reduces the 3D depth perception |
| **Tab** | OSD Toggle | Shows/hides the FPS and parameter panel |
| **F** | Fullscreen | Enters borderless fullscreen mode |

---

## V. Technical Principles & Roadmap

### 1. Core Technologies
* **AI Depth Vision**: Powered by Depth Anything V2 and CUDA, generating high-precision relative depth maps in milliseconds.
* **Dynamic Pixel Shifting**: Calculates the 80th percentile of the center crop to build a dynamic focal plane, applying EMA smoothing and Grid Sample for comfortable 3D rendering.
* **Zero-Copy Pipeline**: Highly optimized VRAM workflow. Converts Float16 tensors directly to Uint8 bytes on the GPU before downloading to RAM, reducing PCIe bandwidth pressure by 75%.

### 2. Roadmap
- [ ] **Interaction**: Implement **"Tap to Focus"** (click on screen to set focal plane manually).
- [ ] **Algorithm**: Dynamic focus region (adjust crop size based on depth histogram).
- [ ] **VR Support**: SteamVR integration for direct HMD output.
- [ ] **Profiling**: More detailed performance statistics panel.

---

## 🤝 Credits & License

This project is based on the following amazing open-source projects:

* **[iw3](https://github.com/nagadomi/nunif)** by nagadomi - Core 3D logic and nunif framework.
* **[Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)** - State-of-the-art Monocular Depth Estimation.
* **[DXCam](https://github.com/ra1nty/DXCam)** - High-performance Windows screen capture.

Licensed under the **MIT License**.
