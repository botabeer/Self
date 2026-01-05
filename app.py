import json
import time
import os
import re
from datetime import datetime
from collections import defaultdict
import requests

# ============ CONFIG ============

DB_FILE = "db.json"
LOG_FILE = "logs.txt"

AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5

LINK_REGEX = re.compile(r"(line\.me|chat\.line|t\.me|telegram\.me|wa\.me|whatsapp\.com)", re.I)

# الحصول على التوكن من متغيرات البيئة
LINE_TOKEN = os.environ.get("LINE_TOKEN", "")
LINE_EMAIL = os.environ.get("LINE_EMAIL", "")
LINE_PASSWORD = os.environ.get("LINE_PASSWORD", "")

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
    print(f"[{datetime.now()}] {txt}")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {txt}\n")

db = load_db()

# ============ LINE CLIENT ============

class LineClient:
    def __init__(self, token=None):
        self.authToken = token
        self.my_mid = None
        
    def _request(self, method, params=None):
        if not self.authToken:
            return {}
        
        try:
            headers = {
                "X-Line-Access": self.authToken,
                "User-Agent": "Line/13.4.1",
                "X-Line-Application": "ANDROID\t13.4.1\tAndroid OS\t12"
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
        except Exception as e:
            log(f"Request error: {e}")
            return {}
    
    def login_with_credentials(self, email, password):
        try:
            log("محاولة تسجيل الدخول...")
            
            headers = {
                "User-Agent": "Line/13.4.1",
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
            
            response = requests.post(
                "https://gd2.line.naver.jp/api/v4/TalkService.do?method=loginZ",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "authToken" in result:
                    self.authToken = result["authToken"]
                    log("تم تسجيل الدخول بنجاح")
                    return True
            
            log(f"فشل تسجيل الدخول: {response.status_code}")
            return False
            
        except Exception as e:
            log(f"خطأ في التسجيل: {e}")
            return False
    
    def get_profile(self):
        result = self._request("getProfile")
        profile = result.get("result")
        if profile:
            self.my_mid = profile.get("mid")
        return profile
    
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
    
    def get_recent_messages(self, group_id, count=30):
        result = self._request("getRecentMessagesV2", {
            "messageBoxId": group_id,
            "count": count
        })
        return result.get("result", [])

# ============ LOGIN ============

def login():
    log("بدء تسجيل الدخول...")
    
    # محاولة استخدام التوكن مباشرة
    if LINE_TOKEN:
        log("استخدام LINE_TOKEN من المتغيرات")
        cl = LineClient(LINE_TOKEN)
        profile = cl.get_profile()
        if profile:
            log(f"تم الاتصال: {profile.get('displayName')}")
            return cl
        else:
            log("فشل التوكن المحفوظ")
    
    # محاولة تسجيل الدخول بالإيميل والباسورد
    if LINE_EMAIL and LINE_PASSWORD:
        log("محاولة التسجيل بالإيميل والباسورد")
        cl = LineClient()
        if cl.login_with_credentials(LINE_EMAIL, LINE_PASSWORD):
            profile = cl.get_profile()
            if profile:
                log(f"تم التسجيل: {profile.get('displayName')}")
                log(f"احفظ هذا التوكن: {cl.authToken}")
                return cl
    
    log("ERROR: لم يتم توفير بيانات تسجيل الدخول!")
    log("اضف متغير البيئة: LINE_TOKEN أو LINE_EMAIL و LINE_PASSWORD")
    exit(1)

cl = login()
my_mid = cl.my_mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

log(f"MID: {my_mid}")
log("البوت جاهز للعمل")

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
        except Exception as e:
            log(f"Send error: {e}")

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
            log(f"طرد {u[:10]}... من {g[:10]}...")
    except Exception as e:
        log(f"Kick error: {e}")

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

    if db["protect"]["link"] and LINK_REGEX.search(text) and not is_admin(s):
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
        send(g, "help, me, ping, stats, kick, ban, warn, mute, lock, panic, ghost")
    
    elif cmd == "me":
        role = "مالك" if is_owner(s) else "أدمن" if is_admin(s) else "عضو"
        warns = db["warnings"].get(s, 0)
        send(g, f"رتبتك: {role}\nتحذيراتك: {warns}/{AUTO_WARN_LIMIT}")
    
    elif cmd == "ping":
        send(g, "البوت يعمل")
    
    elif cmd == "stats":
        send(g, f"الرسائل: {db['stats']['messages']}\nالطردات: {db['stats']['kicks']}\nالحظر: {db['stats']['bans']}")
    
    elif cmd == "panic" and is_owner(s):
        db["shield"] = True
        db["freeze"] = True
        save_db()
        send(g, "وضع الطوارئ مفعل")
    
    elif cmd == "ghost" and is_owner(s):
        db["ghost"] = not db["ghost"]
        save_db()
        if not db["ghost"]:
            send(g, "تم إلغاء الوضع الشبحي")

def main():
    log("البوت يعمل الآن...")
    
    last_check = time.time()
    processed = set()
    
    while True:
        try:
            if time.time() - last_check > 2:
                messages = cl.get_recent_messages(my_mid, 30)
                
                for msg in messages:
                    msg_id = msg.get("id")
                    if msg_id and msg_id not in processed:
                        processed.add(msg_id)
                        if msg.get("contentType") == 0:
                            handle_msg(msg)
                        
                        if len(processed) > 500:
                            processed.clear()
                
                last_check = time.time()
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            log("إيقاف البوت...")
            save_db()
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
