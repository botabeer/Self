import json
import time
import os
import re
import getpass
from datetime import datetime
from collections import defaultdict
import requests

# ============ CONFIG ============

DB_FILE = "db.json"
SESSION_FILE = "session.json"
LOG_FILE = "logs.txt"

AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5

LINK_REGEX = re.compile(r"(line\.me|chat\.line|t\.me|telegram\.me|wa\.me|whatsapp\.com)", re.I)

# ============ DEFAULT DB ============

DEFAULT_DB = {
    "owners": [],
    "admins": [],
    "vip": [],
    "banned": [],
    "warnings": {},
    "muted": {},
    "lock": {},
    "watch": {},
    "ghost": False,
    "shield": False,
    "freeze": False,
    "protect": {
        "kick": True,
        "link": True,
        "spam": True,
        "bots": True
    },
    "stats": {
        "messages": 0,
        "kicks": 0,
        "bans": 0,
        "protections": 0
    },
    "enabled": True
}

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, indent=2, ensure_ascii=False)
        return DEFAULT_DB.copy()
    with open(DB_FILE, encoding="utf-8") as f:
        db = json.load(f)
    for k in DEFAULT_DB:
        db.setdefault(k, DEFAULT_DB[k])
    return db

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def log(txt):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {txt}\n")

db = load_db()

# ============ LINE CLIENT ============

class LineClient:
    def __init__(self):
        self.session = requests.Session()
        self.authToken = None
        self.my_mid = None
        
    def login(self, email, password):
        print("\nجاري تسجيل الدخول...")
        
        try:
            # محاولة تسجيل دخول بسيطة
            headers = {
                "User-Agent": "Line/13.4.1 Android",
                "X-Line-Application": "ANDROID\t13.4.1\tAndroid OS\t12"
            }
            
            data = {
                "loginRequest": {
                    "type": 0,
                    "identityProvider": 1,
                    "identifier": email,
                    "password": password,
                    "keepLoggedIn": True,
                    "systemName": "LineBot"
                }
            }
            
            response = self.session.post(
                "https://gd2.line.naver.jp/api/v4/TalkService.do?method=loginZ",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "authToken" in result:
                    self.authToken = result["authToken"]
                    
                    # حفظ الجلسة
                    with open(SESSION_FILE, "w") as f:
                        json.dump({"token": self.authToken}, f)
                    
                    # الحصول على المعلومات
                    profile = self.get_profile()
                    if profile:
                        self.my_mid = profile.get("mid")
                        print(f"تم تسجيل الدخول: {profile.get('displayName', 'مستخدم')}")
                        return True
                
                elif "verifier" in result:
                    print("\nتحتاج تأكيد برمز!")
                    print("افتح LINE على الجوال وأدخل الرمز")
                    pin = input("أدخل الرمز من LINE: ")
                    
                    # محاولة التأكيد
                    verify_data = {
                        "verifier": result["verifier"],
                        "pinCode": pin
                    }
                    
                    verify_response = self.session.post(
                        "https://gd2.line.naver.jp/api/v4/TalkService.do?method=loginWithVerifier",
                        headers=headers,
                        json=verify_data,
                        timeout=30
                    )
                    
                    if verify_response.status_code == 200:
                        verify_result = verify_response.json()
                        if "authToken" in verify_result:
                            self.authToken = verify_result["authToken"]
                            
                            with open(SESSION_FILE, "w") as f:
                                json.dump({"token": self.authToken}, f)
                            
                            profile = self.get_profile()
                            if profile:
                                self.my_mid = profile.get("mid")
                                print(f"تم تسجيل الدخول: {profile.get('displayName')}")
                                return True
            
            print("فشل تسجيل الدخول")
            print("تأكد من:")
            print("1. الإيميل والباسورد صحيحين")
            print("2. حسابك مربوط بإيميل في: Settings > Account > Email")
            return False
            
        except Exception as e:
            print(f"خطأ: {e}")
            return False
    
    def load_session(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                
                self.authToken = data.get("token")
                profile = self.get_profile()
                
                if profile:
                    self.my_mid = profile.get("mid")
                    print(f"تم استعادة الجلسة: {profile.get('displayName')}")
                    return True
                else:
                    os.remove(SESSION_FILE)
            except:
                pass
        return False
    
    def _request(self, method, params=None):
        if not self.authToken:
            return {}
        
        try:
            headers = {
                "X-Line-Access": self.authToken,
                "User-Agent": "Line/13.4.1"
            }
            
            payload = {"method": method}
            if params:
                payload["params"] = params
            
            response = requests.post(
                "https://gd2.line.naver.jp/api/v4/TalkService.do",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def get_profile(self):
        result = self._request("getProfile")
        return result.get("result")
    
    def send_message(self, to, text):
        return self._request("sendMessage", {"to": to, "text": str(text)})
    
    def kick_user(self, group_id, user_ids):
        if isinstance(user_ids, str):
            user_ids = [user_ids]
        return self._request("kickoutFromGroup", {
            "groupId": group_id,
            "contactIds": user_ids
        })
    
    def get_group(self, group_id):
        result = self._request("getGroup", {"groupId": group_id})
        return result.get("result", {})

# ============ LOGIN ============

def login():
    cl = LineClient()
    
    if cl.load_session():
        return cl
    
    print("\n" + "="*50)
    print("تسجيل الدخول إلى LINE")
    print("="*50)
    print("\nملاحظة: حسابك لازم يكون مربوط بإيميل")
    print("Settings > Account > Email\n")
    
    email = input("الإيميل: ").strip()
    password = getpass.getpass("الباسورد: ")
    
    if cl.login(email, password):
        return cl
    else:
        exit(1)

cl = login()
my_mid = cl.my_mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print(f"\nMID: {my_mid}")
print("البوت يعمل الآن!\n")

# ============ HELPERS ============

def is_owner(u): 
    return u in db["owners"]

def is_admin(u): 
    return u in db["admins"] or is_owner(u)

def is_banned(u): 
    return u in db["banned"]

def is_muted(u):
    if u not in db["muted"]:
        return False
    if time.time() > db["muted"][u]:
        del db["muted"][u]
        save_db()
        return False
    return True

def send(g, txt):
    if not db["ghost"]:
        try:
            cl.send_message(g, txt)
        except:
            pass

def add_warn(u):
    db["warnings"][u] = db["warnings"].get(u, 0) + 1
    save_db()
    return db["warnings"][u]

def safe_kick(g, u):
    try:
        if u != my_mid and not is_owner(u):
            cl.kick_user(g, u)
            db["stats"]["kicks"] += 1
            save_db()
    except:
        pass

user_msgs = defaultdict(list)

def is_spam(u):
    if is_admin(u):
        return False
    now = time.time()
    user_msgs[u] = [t for t in user_msgs[u] if now - t < SPAM_TIME]
    user_msgs[u].append(now)
    return len(user_msgs[u]) > SPAM_COUNT

def handle_msg(msg):
    if not isinstance(msg, dict) or "text" not in msg:
        return

    s = msg.get("_from", msg.get("from", ""))
    g = msg.get("to", "")
    text = msg.get("text", "").strip()
    cmd = text.lower()

    db["stats"]["messages"] += 1

    if is_banned(s):
        safe_kick(g, s)
        return

    if db["freeze"] and not is_admin(s):
        safe_kick(g, s)
        return

    if db["shield"] and not is_admin(s):
        safe_kick(g, s)
        return

    if is_muted(s):
        return

    if db["protect"]["link"] and re.search(LINK_REGEX, text) and not is_admin(s):
        w = add_warn(s)
        if w >= AUTO_WARN_LIMIT:
            db["banned"].append(s)
            save_db()
            safe_kick(g, s)
        else:
            send(g, f"ممنوع الروابط - تحذير {w}/{AUTO_WARN_LIMIT}")
        return

    if db["protect"]["spam"] and is_spam(s):
        w = add_warn(s)
        if w >= AUTO_WARN_LIMIT:
            safe_kick(g, s)
        return

    if cmd == "help":
        send(g, "الأوامر: help, me, ping, stats, kick, ban, warn, mute, lock")
    
    elif cmd == "me":
        role = "مالك" if is_owner(s) else "أدمن" if is_admin(s) else "عضو"
        send(g, f"رتبتك: {role}")
    
    elif cmd == "ping":
        send(g, "البوت يعمل")
    
    elif cmd == "stats":
        send(g, f"الرسائل: {db['stats']['messages']}\nالطردات: {db['stats']['kicks']}")

def main():
    print("البوت شغال...\n")
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nإيقاف البوت...")
            save_db()
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
