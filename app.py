import json
import time
import os
import re
import getpass
import hashlib
import hmac
import struct
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

MASSKICK_BATCH = 3
MASSKICK_DELAY = 2

LINK_REGEX = re.compile(r"(line\.me|chat\.line|t\.me|telegram\.me|wa\.me|whatsapp\.com)", re.I)

LINE_HOST = "https://gd2.line.naver.jp"
LINE_API = f"{LINE_HOST}/api/v4/TalkService.do"

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
    "whitelist_bots": [],
    "ghost": False,
    "shield": False,
    "freeze": False,
    "protect": {
        "kick": True,
        "link": True,
        "spam": True,
        "bots": True,
        "invite": True,
        "qr": True,
        "cancel": True
    },
    "stats": {
        "messages": 0,
        "kicks": 0,
        "bans": 0,
        "protections": 0
    },
    "enabled": True,
    "auto_join": True
}

# ============ DB FUNCTIONS ============

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
    print(f"[LOG] {txt}")

db = load_db()

# ============ LINE CLIENT ============

class LineClient:
    def __init__(self):
        self.authToken = None
        self.certificate = None
        self.my_mid = None
        self.headers = {
            "User-Agent": "Line/13.4.1",
            "X-Line-Application": "ANDROID\t13.4.1\tAndroid OS\t12",
            "X-Line-Carrier": "51089, 1-0"
        }
    
    def _request(self, method, params=None):
        try:
            headers = self.headers.copy()
            if self.authToken:
                headers["X-Line-Access"] = self.authToken
            
            payload = {"method": method}
            if params:
                payload["params"] = params
            
            response = requests.post(LINE_API, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                log(f"API Error {response.status_code}: {method}")
                return {}
        except Exception as e:
            log(f"Request error in {method}: {e}")
            return {}
    
    def login_with_email(self, email, password):
        try:
            print("جاري تسجيل الدخول...")
            
            # محاولة تسجيل الدخول البسيط
            result = self._request("loginWithIdentityCredentialForCertificate", {
                "identityProvider": 1,
                "identifier": email,
                "password": password,
                "keepLoggedIn": True,
                "systemName": "LineBot"
            })
            
            if "authToken" in result:
                self.authToken = result["authToken"]
                self.certificate = result.get("certificate")
                
                # حفظ الجلسة
                session_data = {
                    "authToken": self.authToken,
                    "certificate": self.certificate
                }
                with open(SESSION_FILE, "w") as f:
                    json.dump(session_data, f)
                
                # الحصول على المعلومات
                profile = self.get_profile()
                if profile:
                    self.my_mid = profile.get("mid")
                    print(f"تم تسجيل الدخول بنجاح: {profile.get('displayName', 'User')}")
                    return True
            
            print("فشل تسجيل الدخول - تحقق من الإيميل والباسورد")
            return False
            
        except Exception as e:
            log(f"Login error: {e}")
            print(f"خطأ في تسجيل الدخول: {e}")
            return False
    
    def load_session(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    session = json.load(f)
                
                self.authToken = session.get("authToken")
                self.certificate = session.get("certificate")
                
                profile = self.get_profile()
                if profile:
                    self.my_mid = profile.get("mid")
                    print(f"تم استعادة الجلسة: {profile.get('displayName', 'User')}")
                    return True
                else:
                    os.remove(SESSION_FILE)
                    return False
            except:
                return False
        return False
    
    def get_profile(self):
        result = self._request("getProfile")
        return result.get("result")
    
    def send_message(self, to, text):
        return self._request("sendMessage", {
            "to": to,
            "text": str(text)
        })
    
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
    
    def accept_group_invitation(self, group_id):
        return self._request("acceptGroupInvitation", {"groupId": group_id})
    
    def get_recent_messages(self, group_id, count=50):
        result = self._request("getRecentMessagesV2", {
            "messageBoxId": group_id,
            "count": count
        })
        return result.get("result", [])

# ============ LOGIN ============

def login():
    cl = LineClient()
    
    # محاولة تحميل جلسة محفوظة
    if cl.load_session():
        return cl
    
    print("\n" + "="*50)
    print("تسجيل الدخول إلى LINE")
    print("="*50)
    
    email = input("الإيميل: ").strip()
    password = getpass.getpass("الباسورد: ")
    
    if cl.login_with_email(email, password):
        return cl
    else:
        print("\nفشل تسجيل الدخول!")
        print("تأكد من:")
        print("1. الإيميل والباسورد صحيحين")
        print("2. حسابك مربوط بإيميل (Settings > Account > Email)")
        exit(1)

cl = login()
my_mid = cl.my_mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print(f"\nMID: {my_mid}")
print("البوت يعمل الآن...\n")

# ============ HELPERS ============

def is_owner(u): 
    return u in db["owners"]

def is_admin(u): 
    return u in db["admins"] or is_owner(u)

def is_vip(u): 
    return u in db["vip"]

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

def get_mentions(text):
    mentions = []
    try:
        parts = text.split("@")
        for part in parts[1:]:
            words = part.split()
            if words and len(words[0]) == 33:
                mentions.append(words[0])
    except:
        pass
    return mentions

def add_warn(u):
    db["warnings"][u] = db["warnings"].get(u, 0) + 1
    save_db()
    return db["warnings"][u]

def safe_kick(g, u, silent=False):
    try:
        if u != my_mid and not is_owner(u):
            cl.kick_user(g, u)
            db["stats"]["kicks"] += 1
            save_db()
            log(f"KICK {u} in {g}")
            if not silent and not db["ghost"]:
                send(g, "تم طرد العضو")
    except Exception as e:
        log(f"Failed to kick {u}: {e}")

# ============ SPAM SYSTEM ============

user_msgs = defaultdict(list)

def is_spam(u):
    if is_vip(u) or is_admin(u):
        return False
    now = time.time()
    user_msgs[u] = [t for t in user_msgs[u] if now - t < SPAM_TIME]
    user_msgs[u].append(now)
    return len(user_msgs[u]) > SPAM_COUNT

# ============ MASSKICK ============

def masskick(group, members):
    batch = []
    for u in members:
        if u == my_mid or is_owner(u) or is_admin(u):
            continue
        batch.append(u)
        if len(batch) >= MASSKICK_BATCH:
            try:
                cl.kick_user(group, batch)
            except:
                pass
            time.sleep(MASSKICK_DELAY)
            batch = []
    if batch:
        try:
            cl.kick_user(group, batch)
        except:
            pass

# ============ MESSAGE HANDLER ============

def handle_msg(msg):
    if not isinstance(msg, dict) or "text" not in msg:
        return

    s = msg.get("_from", msg.get("from", ""))
    g = msg.get("to", "")
    text = msg.get("text", "").strip()
    cmd = text.lower()

    db["stats"]["messages"] += 1

    # Protections
    if is_banned(s):
        safe_kick(g, s, True)
        return

    if db["freeze"] and not is_admin(s):
        safe_kick(g, s, True)
        return

    if db["shield"] and not is_admin(s):
        safe_kick(g, s, True)
        return

    if db["lock"].get(g) and not is_admin(s):
        return

    if is_muted(s):
        return

    if db["protect"]["link"] and LINK_REGEX.search(text) and not is_admin(s):
        w = add_warn(s)
        if w >= AUTO_WARN_LIMIT:
            db["banned"].append(s)
            save_db()
            safe_kick(g, s, True)
        else:
            send(g, f"ممنوع الروابط - تحذير {w}/{AUTO_WARN_LIMIT}")
        return

    if db["protect"]["spam"] and is_spam(s):
        w = add_warn(s)
        if w >= AUTO_WARN_LIMIT:
            db["banned"].append(s)
            save_db()
            safe_kick(g, s, True)
        return

    if s in db["watch"] and not is_admin(s):
        db["watch"][s] += 1
        if db["watch"][s] >= 2:
            db["banned"].append(s)
            save_db()
            safe_kick(g, s, True)
        save_db()
        return

    m = get_mentions(text)

    # Commands
    if cmd == "help":
        send(g,
"""الأوامر المتاحة:

العامة:
help - الأوامر
me - معلوماتك
ping - فحص البوت
stats - الإحصائيات
time - الوقت

الأدمن:
kick - طرد عضو
warn - تحذير
clearwarn - حذف تحذيرات
mute - كتم (10 دقائق)
unmute - فك كتم
lock - قفل الشات
unlock - فتح الشات
watch - مراقبة عضو
unwatch - إلغاء المراقبة

المالك:
addadmin - إضافة أدمن
deladmin - حذف أدمن
ban - حظر نهائي
unban - فك حظر
masskick - طرد الجميع
panic - وضع طوارئ
ghost - وضع شبحي
unghost - إلغاء شبحي
shield - تفعيل الدرع
unshield - إلغاء الدرع
freeze - تجميد
unfreeze - فك تجميد""")

    elif cmd == "me":
        role = "مالك" if is_owner(s) else "أدمن" if is_admin(s) else "VIP" if is_vip(s) else "عضو"
        warns = db["warnings"].get(s, 0)
        send(g, f"رتبتك: {role}\nتحذيراتك: {warns}/{AUTO_WARN_LIMIT}")

    elif cmd == "time":
        send(g, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    elif cmd == "ping":
        send(g, "البوت يعمل بشكل طبيعي")

    elif cmd == "stats":
        send(g, f"""الإحصائيات:
الرسائل: {db['stats']['messages']}
الطردات: {db['stats']['kicks']}
الحظر: {db['stats']['bans']}
الحمايات: {db['stats']['protections']}""")

    # Admin commands
    elif cmd == "kick" and is_admin(s):
        if m:
            for u in m:
                safe_kick(g, u)
        else:
            send(g, "منشن العضو")

    elif cmd == "warn" and is_admin(s):
        if m:
            for u in m:
                w = add_warn(u)
                send(g, f"تحذير {w}/{AUTO_WARN_LIMIT}")
        else:
            send(g, "منشن العضو")

    elif cmd == "clearwarn" and is_admin(s):
        if m:
            for u in m:
                db["warnings"].pop(u, None)
            save_db()
            send(g, "تم حذف التحذيرات")

    elif cmd == "mute" and is_admin(s):
        if m:
            for u in m:
                db["muted"][u] = time.time() + 600
            save_db()
            send(g, "تم الكتم لمدة 10 دقائق")

    elif cmd == "unmute" and is_admin(s):
        if m:
            for u in m:
                db["muted"].pop(u, None)
            save_db()
            send(g, "تم فك الكتم")

    elif cmd == "lock" and is_admin(s):
        db["lock"][g] = True
        save_db()
        send(g, "تم قفل الشات")

    elif cmd == "unlock" and is_admin(s):
        db["lock"][g] = False
        save_db()
        send(g, "تم فتح الشات")

    elif cmd == "watch" and is_admin(s):
        if m:
            for u in m:
                db["watch"][u] = 0
            save_db()
            send(g, "تمت إضافة للمراقبة")

    elif cmd == "unwatch" and is_admin(s):
        if m:
            for u in m:
                db["watch"].pop(u, None)
            save_db()
            send(g, "تم إلغاء المراقبة")

    # Owner commands
    elif cmd == "addadmin" and is_owner(s):
        if m:
            for u in m:
                if u not in db["admins"]:
                    db["admins"].append(u)
            save_db()
            send(g, "تم إضافة الأدمن")

    elif cmd == "deladmin" and is_owner(s):
        if m:
            for u in m:
                if u in db["admins"]:
                    db["admins"].remove(u)
            save_db()
            send(g, "تم حذف الأدمن")

    elif cmd == "ban" and is_owner(s):
        if m:
            for u in m:
                if u not in db["banned"]:
                    db["banned"].append(u)
                    db["stats"]["bans"] += 1
                    safe_kick(g, u, True)
            save_db()
            send(g, "تم الحظر نهائيا")

    elif cmd == "unban" and is_owner(s):
        if m:
            for u in m:
                if u in db["banned"]:
                    db["banned"].remove(u)
            save_db()
            send(g, "تم فك الحظر")

    elif cmd == "masskick" and is_owner(s):
        try:
            group = cl.get_group(g)
            members = [mem.get("mid") for mem in group.get("members", [])]
            masskick(g, members)
            send(g, "تم طرد جميع الأعضاء")
        except Exception as e:
            log(f"Masskick error: {e}")

    elif cmd == "panic" and is_owner(s):
        db["shield"] = True
        db["freeze"] = True
        save_db()
        send(g, "وضع الطوارئ مفعل")

    elif cmd == "ghost" and is_owner(s):
        db["ghost"] = True
        save_db()

    elif cmd == "unghost" and is_owner(s):
        db["ghost"] = False
        save_db()
        send(g, "تم إلغاء الوضع الشبحي")

    elif cmd == "shield" and is_owner(s):
        db["shield"] = True
        save_db()
        send(g, "تم تفعيل الدرع")

    elif cmd == "unshield" and is_owner(s):
        db["shield"] = False
        save_db()
        send(g, "تم إلغاء الدرع")

    elif cmd == "freeze" and is_owner(s):
        db["freeze"] = True
        save_db()
        send(g, "تم التجميد")

    elif cmd == "unfreeze" and is_owner(s):
        db["freeze"] = False
        save_db()
        send(g, "تم فك التجميد")

# ============ MAIN LOOP ============

def main():
    print("البوت شغال ويستقبل الرسائل...")
    print("اكتب CTRL+C للإيقاف\n")
    
    last_check = time.time()
    processed = set()
    
    while True:
        try:
            if time.time() - last_check > 1:
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
            print("\nإيقاف البوت...")
            save_db()
            print("تم حفظ البيانات. وداعا!")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
