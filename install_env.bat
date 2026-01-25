@echo off
cd /d "%~dp0"
title 3D Player - Environment Installer

:: --- CONFIGURATION ---
set PIP_MIRROR=-i https://pypi.tuna.tsinghua.edu.cn/simple

echo ========================================================
echo [1/5] Checking Python Environment...
echo ========================================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! 
    echo Please install Python 3.10 and check "Add to PATH".
    pause
    exit /b
)

echo.
echo ========================================================
echo [2/5] Creating Virtual Environment (venv)...
echo ========================================================
if exist venv (
    echo [INFO] 'venv' folder already exists. Skipping creation...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv.
        echo Please check folder permissions or delete the 'venv' folder manually.
        pause
        exit /b
    )
)

echo.
echo ========================================================
echo [3/5] Upgrading pip...
echo ========================================================
call venv\Scripts\activate.bat
python -m pip install --upgrade pip %PIP_MIRROR%

echo.
echo ========================================================
echo [4/5] Installing PyTorch (GPU - CUDA 12.1)...
echo This may take a few minutes...
echo ========================================================
:: Using explicit timeout to prevent connection drops
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --timeout 1000
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyTorch installation failed!
    echo Possible reasons: Network timeout or VPN issues.
    pause
    exit /b
)

echo.
echo ========================================================
echo [5/5] Installing dependencies from requirements.txt...
echo ========================================================
if not exist requirements.txt (
    echo [ERROR] 'requirements.txt' not found!
    echo Please make sure you extracted all files from the zip.
    pause
    exit /b
)

pip install -r requirements.txt %PIP_MIRROR%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo.
echo ========================================================
echo SUCCESS: Environment is ready! 
echo Now you can run 'run_app.bat'.
echo ========================================================
pause