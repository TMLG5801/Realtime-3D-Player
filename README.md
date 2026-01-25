# 🚀 Realtime 3D Player (2D to 3D Converter)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10-green.svg)](https://www.python.org/)
[![Powered By](https://img.shields.io/badge/Powered%20By-DepthAnythingV2-orange.svg)](https://github.com/DepthAnything/Depth-Anything-V2)

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
*   **注意**：此过程需要下载约 2GB+ 数据，请耐心等待直到窗口提示“环境安装完成”或自动关闭。

### 3. 启动程序
双击 **`run_app.bat`** 即可启动。

*   **自动模型下载**：首次启动时，程序会自动检测并下载 **Small / Base / Large** 全套模型（共约 1.6GB）。
    *   *请保持网络畅通，下载完成后 GUI 界面会自动弹出。*
*   **后续运行**：环境和模型准备好后，直接双击此脚本即可秒开。

---

## 二、项目介绍

本项目是一个基于 Python 的实时视频/桌面转 3D 播放器。它利用 **Depth Anything V2** 模型，将原本平面的 2D 画面实时推理为深度图，并渲染为 **3D SBS (Side-by-Side)** 格式。

**主要特性：**

*   **实时转换**：利用 TensorRT/CUDA 加速，实现低延迟的 2D 转 3D 推理。
*   **桌面/游戏采集**：集成 DXCam（极速）和 MSS（兼容）两种采集引擎，支持实时转换游戏画面。
*   **全自动部署**：内置 Python 脚本自动处理依赖安装与模型下载。
*   **可视化控制**：提供 GUI 界面调节分辨率、模型大小 (Small/Base/Large) 及 3D 强度。

---

## 三、环境依赖

**硬件要求**

*   **GPU**: NVIDIA GeForce RTX 系列显卡。
*   **系统**: Windows 10 / 11 (64-bit)。

**软件要求**

*   **Python**: 3.10+ (必需)。
*   **CUDA**: 程序会自动安装带有 CUDA 12.1 支持的 PyTorch，无需手动安装 CUDA Toolkit。

---

## 四、操作快捷键

程序运行并弹出 3D 画面后，你可以使用以下快捷键进行实时调整：

| 按键 | 功能 |
| :--- | :--- |
| **Q** | 退出程序 |
| **F** | 全屏 / 退出全屏 |
| **Space (空格)** | 交换左右眼 (Swap Left/Right) |
| **]** | 增加 3D 强度 (更立体) |
| **[** | 减小 3D 强度 (更扁平) |
| **Tab** | 显示 / 隐藏 OSD 数据面板 |

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
*   **Note**: This process involves downloading 2GB+ of data. Please wait until the window indicates completion or closes automatically.

### 3. Start Application
Double-click **`run_app.bat`** to launch.

*   **Auto Model Download**: On the first launch, the program will automatically detect and download the **Small / Base / Large** model set (approx. 1.6GB).
    *   *The GUI will appear automatically once the download is complete.*
*   **Subsequent Runs**: Just double-click this script to run instantly.

---

## II. Project Introduction

This project is a Python-based real-time 2D-to-3D video player. It leverages the **Depth Anything V2** model to infer depth maps from flat 2D images in real-time and renders them into **3D SBS (Side-by-Side)** format.

**Key Features:**

*   **Real-time Conversion**: Uses TensorRT/CUDA acceleration for low-latency inference.
*   **Desktop Capture**: Integrates DXCam (High Performance) and MSS (Compatible) engines for real-time game conversion.
*   **Fully Automated**: Built-in scripts handle dependency installation and model downloading automatically.
*   **GUI Control**: Easy-to-use interface to adjust resolution, model size, and 3D strength.

---

## III. Environmental Dependencies

**Hardware Requirements**

*   **GPU**: NVIDIA GeForce RTX series recommended.
*   **OS**: Windows 10 / 11 (64-bit).

**Software Requirements**

*   **Python**: 3.10+ (Required).
*   **CUDA**: The program automatically installs PyTorch with CUDA 12.1 support; manual CUDA Toolkit installation is not required.

---

## IV. Controls

Once the 3D window is running, use the following hotkeys:

| Key | Function |
| :--- | :--- |
| **Q** | Quit Application |
| **F** | Toggle Fullscreen |
| **Space** | Swap Left/Right Eye |
| **]** | Increase 3D Strength (More Depth) |
| **[** | Decrease 3D Strength (Flatter) |
| **Tab** | Toggle OSD Info Panel |

---

## 🤝 Credits & License

This project is based on the following amazing open-source projects:

*   **[iw3](https://github.com/nagadomi/nunif)** by nagadomi - Core 3D logic and nunif framework.
*   **[Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)** - State-of-the-art Monocular Depth Estimation.
*   **[DXCam](https://github.com/ra1nty/DXCam)** - High-performance Windows screen capture.

Licensed under the **MIT License**.
