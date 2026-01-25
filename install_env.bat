@echo off
cd /d "%~dp0"
title 3D Player - Step 1: Install Environment

echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10 and check "Add to PATH".
    pause
    exit /b
)

echo [2/4] Creating Virtual Environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv. 
    pause
    exit /b
)

echo [3/4] Installing PyTorch (GPU - CUDA 12.1)...
:: 这里是关键，必须在 venv 激活状态下安装
call venv\Scripts\activate.bat
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo [4/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo ========================================================
echo SUCCESS: Environment is ready! 
echo Now you can run 'run_app.bat'.
echo ========================================================
pause