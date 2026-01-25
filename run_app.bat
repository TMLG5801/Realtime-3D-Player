@echo off
cd /d "%~dp0"
title 3D Player - Step 2: Run

if not exist venv\Scripts\activate.bat (
    echo [ERROR] Environment not found! Please run 'install_env.bat' first.
    pause
    exit /b
)

echo [INFO] Activating Environment...
call venv\Scripts\activate.bat

echo [INFO] Launching Main Program...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [CRASH] Program exited with error.
    pause
)