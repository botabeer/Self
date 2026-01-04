import json
import time
import os
import re
from datetime import datetime
from collections import defaultdict
import requests
import base64

# ============ CONFIG ============

DB_FILE = "db.json"
TOKEN_FILE = "token.txt"
LOG_FILE = "logs.txt"

AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5

MASSKICK_BATCH = 4
MASSKICK_DELAY = 2

LINK_REGEX = re.compile(r"(line\.me|chat\.line|t\.me|telegram\.me|wa\.me|whatsapp\.com)", re.I)

LINE_API = "https://gd2.line.naver.jp"
LINE_API_QUERY = "https://gd2.line.naver.jp/api/v4/TalkService.do"

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

db = load_db()

# ============ LINE API CLASS ============

class LineClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "X-Line-Access": token,
            "User-Agent": "Line/10.0.0",
            "X-Line-Application": "DESKTOPMAC 10.0.0 MAC 10.0.0"
        }
        self.my_mid = self.get_profile()["mid"]
        
    def _post(self, path, data):
        try:
            r = requests.post(f"{LINE_API}{path}", headers=self.headers, json=data)
            return r.json()
        except:
            return {}
    
    def get_profile(self):
        return self._post("/api/v4/TalkService.do", {
            "method": "getProfile"
        }).get("result", {})
    
    def send_message(self, to, text):
        return self._post("/api/v4/TalkService.do", {
            "method": "sendMessage",
            "params": {
                "to": to,
                "text": text
            }
        })
    
    def kick_user(self, group_id, user_ids):
        return self._post("/api/v4/TalkService.do", {
            "method": "kickoutFromGroup",
            "params": {
                "groupId": group_id,
                "contactIds": user_ids if isinstance(user_ids, list) else [user_ids]
            }
        })
    
    def get_group(self, group_id):
        return self._post("/api/v4/TalkService.do", {
            "method": "getGroup",
            "params": {
                "groupId": group_id
            }
        }).get("result", {})
    
    def accept_group_invitation(self, group_id):
        return self._post("/api/v4/TalkService.do", {
            "method": "acceptGroupInvitation",
            "params": {
                "groupId": group_id
            }
        })
    
    def get_recent_messages(self, limit=50):
        return self._post("/api/v4/TalkService.do", {
            "method": "getRecentMessages",
            "params": {
                "count": limit
            }
        }).get("result", [])

# ============ LOGIN ============

def login():
    if os.path.exists(TOKEN_FILE):
        try:
            token = open(TOKEN_FILE).read().strip()
            print("جاري تسجيل الدخول...")
            client = LineClient(token)
            print("تم تسجيل الدخول بنجاح")
            return client
        except Exception as e:
            print(f"فشل التوكن: {e}")
            os.remove(TOKEN_FILE)
    
    print("\nللحصول على التوكن:")
    print("1. افتح LINE على الكمبيوتر")
    print("2. اضغط F12 > Network")
    print("3. ابحث عن X-Line-Access في الهيدرز")
    print("4. انسخه والصقه هنا\n")
    
    token = input("التوكن: ").strip()
    
    try:
        client = LineClient(token)
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        print("تم حفظ التوكن بنجاح")
        return client
    except Exception as e:
        print(f"خطأ في التوكن: {e}")
        exit(1)

cl = login()
my_mid = cl.my_mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print(f"MID: {my_mid}")
print("البوت يعمل الان...")

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
            mid = part.split()[0] if part else None
            if mid and len(mid) == 33:
                mentions.append(mid)
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

# ============ MASSKICK SAFE ============

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
    if not msg.get("text"):
        return

    s = msg.get("from")
    g = msg.get("to")
    text = msg.get("text", "").strip()
    cmd = text.lower()

    db["stats"]["messages"] += 1

    # ===== Protections =====

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

    # ===== Watch System =====
    if s in db["watch"] and not is_admin(s):
        db["watch"][s] += 1
        if db["watch"][s] >= 2:
            db["banned"].append(s)
            save_db()
            safe_kick(g, s, True)
        save_db()
        return

    m = get_mentions(text)

    # ===== COMMANDS =====

    if cmd == "help":
        send(g,
"""الأوامر العامة:
help - عرض الأوامر
me - معلوماتك
time - الوقت
ping - فحص البوت
stats - الإحصائيات

أوامر الأدمن:
kick - طرد عضو
mute - كتم عضو
unmute - فك كتم
warn - تحذير
clearwarn - حذف تحذيرات
lock - قفل الشات
unlock - فتح الشات

أوامر المالك:
addadmin - إضافة أدمن
ban - حظر
unban - فك حظر
masskick - طرد الجميع
panic - وضع الطوارئ
ghost - وضع شبحي""")

    elif cmd == "me":
        role = "مالك" if is_owner(s) else "أدمن" if is_admin(s) else "عضو"
        warns = db["warnings"].get(s, 0)
        send(g, f"رتبتك: {role}\nتحذيراتك: {warns}/{AUTO_WARN_LIMIT}")

    elif cmd == "time":
        send(g, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    elif cmd == "ping":
        send(g, "Pong - البوت يعمل")

    elif cmd == "stats":
        stats_text = f"""إحصائيات البوت:
الرسائل: {db['stats']['messages']}
الطردات: {db['stats']['kicks']}
الحظر: {db['stats']['bans']}
الحمايات: {db['stats']['protections']}"""
        send(g, stats_text)

    # ===== ADMIN =====

    elif cmd == "kick" and is_admin(s):
        if not m:
            send(g, "منشن العضو المراد طرده")
            return
        for u in m:
            safe_kick(g, u)

    elif cmd == "warn" and is_admin(s):
        if not m:
            send(g, "منشن العضو")
            return
        for u in m:
            w = add_warn(u)
            send(g, f"تحذير {w}/{AUTO_WARN_LIMIT}")

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

    # ===== OWNER =====

    elif cmd == "addadmin" and is_owner(s):
        if m:
            for u in m:
                if u not in db["admins"]:
                    db["admins"].append(u)
            save_db()
            send(g, "تم إضافة الأدمن")

    elif cmd == "ban" and is_owner(s):
        if m:
            for u in m:
                if u not in db["banned"]:
                    db["banned"].append(u)
                    db["stats"]["bans"] += 1
                    safe_kick(g, u, True)
            save_db()
            send(g, "تم الحظر")

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
            members = [mem["mid"] for mem in group.get("members", [])]
            masskick(g, members)
            send(g, "تم طرد الجميع")
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

# ============ MAIN LOOP ============

def main():
    last_check = time.time()
    
    while True:
        try:
            if time.time() - last_check > 1:
                messages = cl.get_recent_messages(20)
                
                for msg in messages:
                    if msg.get("type") == 1:  # Text message
                        handle_msg(msg)
                
                last_check = time.time()
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("تم إيقاف البوت")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
