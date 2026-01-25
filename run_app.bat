@echo off
setlocal

:: ==============================================================
:: 用户配置区 (发布前请修改这里)
:: ==============================================================

:: 如果你想强制指定某个 Python (比如你现在的 Conda 环境)，请把下一行的 set 改为你的绝对路径
:: 例如: set PYTHON_EXE=E:\Miniconda\envs\iw3_env\python.exe
set PYTHON_EXE=python

:: ==============================================================
:: 启动逻辑
:: ==============================================================
title Realtime 3D Player Launcher

echo [INFO] Checking environment...
echo.

:: 1. 尝试运行一下 Python 看看是否存在
"%PYTHON_EXE%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please ensure Python is installed and added to PATH.
    echo Or edit this run.bat to point to your python.exe.
    echo.
    pause
    exit /b
)

:: 2. 启动主程序
echo [INFO] Starting Player...
"%PYTHON_EXE%" main.py

:: 3. 如果程序异常退出 (exit code != 0)，暂停显示报错
if %errorlevel% neq 0 (
    echo.
    echo [CRASH] The application crashed or closed with an error.
    echo Common fixes:
    echo  - Missing libraries? Run: pip install -r requirements.txt
    echo  - Missing models? Check 'models' folder.
    echo.
    pause
)