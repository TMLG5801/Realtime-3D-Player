@echo off
setlocal
cd /d "%~dp0"
title Realtime 3D Player - Auto Installer

:: ==============================================================
:: 配置区
:: ==============================================================
set VENV_DIR=venv
set PYTHON_EXE=python

:: ==============================================================
:: 1. 检查用户是否安装了 Python
:: ==============================================================
"%PYTHON_EXE%" --version >nul 2>&1
if %errorlevel% neq 0 (
    cls
    echo [ERROR] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.10 或 3.11 (记得勾选 Add to PATH)
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: ==============================================================
:: 2. 检查虚拟环境是否存在
:: ==============================================================
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] 检测到虚拟环境，正在启动...
    goto StartApp
)

:: ==============================================================
:: 3. 初次安装逻辑 (只有第一次运行会执行)
:: ==============================================================
cls
echo ========================================================
echo  正在为您初始化环境，这可能需要几分钟...
echo  请保持网络畅通 (正在下载 PyTorch GPU版)
echo ========================================================
echo.

echo [1/4] 创建虚拟环境 (venv)...
"%PYTHON_EXE%" -m venv %VENV_DIR%
if %errorlevel% neq 0 (
    echo [ERROR] 创建虚拟环境失败。
    pause
    exit /b
)

echo [2/4] 激活环境并更新 pip...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip

echo [3/4] 安装 GPU 版 PyTorch (CUDA 12.1)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo [4/4] 安装其他依赖库...
pip install -r requirements.txt

echo.
echo [SUCCESS] 环境安装完成！下次启动将直接运行。
echo.

:: ==============================================================
:: 4. 启动程序
:: ==============================================================
:StartApp
if not defined VIRTUAL_ENV call "%VENV_DIR%\Scripts\activate.bat"

echo [INFO] 正在启动 3D 播放器...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 程序异常退出。
    pause
)

 致谢与许可 (Credits)
本项目是基于以下优秀的开源项目修改而来：
iw3 by nagadomi - 核心 3D 转换逻辑与 nunif 框架。
Depth Anything V2 - 强大的单目深度估计模型。
DXCam - Windows 高性能屏幕采集库。