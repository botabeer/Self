# =========================================
# LINE Protection Bot - app.py (Stable)
# Arabic messages | English commands
# =========================================

import json
import time
import os
import getpass
import re
import hashlib
from datetime import datetime
from collections import defaultdict

# ===== Safe import linepy =====
try:
    from linepy import LINE, OEPoll
except ImportError:
    print("❌ مكتبة linepy غير مثبتة")
    print("📌 ثبتها بالأمر:")
    print("pip install git+https://github.com/dyseo/linepy.git")
    exit(1)

# ============ CONFIG ============

DB_FILE = "db.json"
TOKEN_FILE = "token.txt"
LOG_FILE = "logs.txt"

AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5

MASSKICK_BATCH = 4
MASSKICK_DELAY = 2

LINK_REGEX = re.compile(r"(line\.me|chat\.line)", re.I)

# كلمة سر الأوامر السرية (غيرها)
SECRET_KEY = "CHANGE_ME_NOW"

# ============ DEFAULT DB ============

DEFAULT_DB = {
    "owners": [],
    "admins": [],
    "vip": [],
    "banned": [],
    "warnings": {},
    "muted": {},          # mid: unmute_time
    "lock": {},
    "watch": {},          # mid: strikes
    "whitelist_bots": [],
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

# ============ LOGIN ============

def login():
    if os.path.exists(TOKEN_FILE):
        try:
            return LINE(open(TOKEN_FILE).read().strip())
        except:
            os.remove(TOKEN_FILE)

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    cl = LINE(email, password)
    with open(TOKEN_FILE, "w") as f:
        f.write(cl.authToken)
    return cl

cl = login()
op = OEPoll(cl)
my_mid = cl.profile.mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print("✅ تم تشغيل البوت بنجاح")

# ============ HELPERS ============

def is_owner(u): return u in db["owners"]
def is_admin(u): return u in db["admins"] or is_owner(u)
def is_vip(u): return u in db["vip"]
def is_banned(u): return u in db["banned"]

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
        cl.sendMessage(g, txt)

def mentions(msg):
    try:
        data = json.loads(msg.contentMetadata["MENTION"])
        return [m["M"] for m in data["MENTIONEES"]]
    except:
        return []

def add_warn(u):
    db["warnings"][u] = db["warnings"].get(u, 0) + 1
    save_db()
    return db["warnings"][u]

def safe_kick(g, u, silent=False):
    try:
        if u != my_mid and not is_owner(u):
            cl.kickoutFromGroup(g, [u])
            db["stats"]["kicks"] += 1
            save_db()
            log(f"KICK {u} in {g}")
            if not silent:
                send(g, "تم طرد العضو")
    except:
        pass

# ============ SPAM SYSTEM ============

user_msgs = defaultdict(list)

def is_spam(u):
    if is_vip(u):
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
                cl.kickoutFromGroup(group, batch)
            except:
                pass
            time.sleep(MASSKICK_DELAY)
            batch = []
    if batch:
        try:
            cl.kickoutFromGroup(group, batch)
        except:
            pass

# ============ MESSAGE HANDLER ============

def handle_msg(msg):
    if not msg.text:
        return

    s = msg._from
    g = msg.to
    text = msg.text.strip()
    cmd = text.lower()

    db["stats"]["messages"] += 1
    save_db()

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
        if add_warn(s) >= AUTO_WARN_LIMIT:
            db["banned"].append(s)
            safe_kick(g, s, True)
        return

    if is_spam(s):
        if add_warn(s) >= AUTO_WARN_LIMIT:
            safe_kick(g, s, True)
        return

    # ===== Watch System =====
    if s in db["watch"] and not is_admin(s):
        db["watch"][s] += 1
        if db["watch"][s] >= 2:
            db["banned"].append(s)
            safe_kick(g, s, True)
        save_db()
        return

    m = mentions(msg)

    # ===== GENERAL =====

    if cmd == "help":
        send(g,
"""📋 الأوامر العامة
help - عرض الأوامر
me - معلوماتك
time - الوقت
ping - فحص البوت
stats - الإحصائيات

👮 أوامر الأدمن
kick / mute / unmute
warn / clearwarn
lock / unlock
watch / unwatch

👑 أوامر المالك
addadmin / deladmin
ban / unban
masskick
panic
ghost / unghost
""")

    elif cmd == "me":
        role = "مالك" if is_owner(s) else "أدمن" if is_admin(s) else "عضو"
        send(g, f"رتبتك: {role}\nتحذيراتك: {db['warnings'].get(s,0)}")

    elif cmd == "time":
        send(g, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    elif cmd == "ping":
        start = time.time()
        send(g, f"Pong {round(time.time()-start,3)}s")

    elif cmd == "stats":
        send(g, json.dumps(db["stats"], ensure_ascii=False))

    # ===== ADMIN =====

    elif cmd == "kick" and is_admin(s):
        for u in m:
            safe_kick(g, u)

    elif cmd == "warn" and is_admin(s):
        for u in m:
            w = add_warn(u)
            send(g, f"تحذير {w}/{AUTO_WARN_LIMIT}")

    elif cmd == "clearwarn" and is_admin(s):
        for u in m:
            db["warnings"].pop(u, None)
        save_db()

    elif cmd == "mute" and is_admin(s):
        for u in m:
            db["muted"][u] = time.time() + 600
        save_db()

    elif cmd == "unmute" and is_admin(s):
        for u in m:
            db["muted"].pop(u, None)
        save_db()

    elif cmd == "lock" and is_admin(s):
        db["lock"][g] = True
        save_db()

    elif cmd == "unlock" and is_admin(s):
        db["lock"][g] = False
        save_db()

    elif cmd == "watch" and is_admin(s):
        for u in m:
            db["watch"][u] = 0
        save_db()
        send(g, "تمت إضافة العضو للمراقبة")

    elif cmd == "unwatch" and is_admin(s):
        for u in m:
            db["watch"].pop(u, None)
        save_db()
        send(g, "تم إيقاف المراقبة")

    # ===== OWNER =====

    elif cmd == "addadmin" and is_owner(s):
        for u in m:
            if u not in db["admins"]:
                db["admins"].append(u)
        save_db()

    elif cmd == "deladmin" and is_owner(s):
        for u in m:
            if u in db["admins"]:
                db["admins"].remove(u)
        save_db()

    elif cmd == "ban" and is_owner(s):
        for u in m:
            if u not in db["banned"]:
                db["banned"].append(u)
                safe_kick(g, u)
        save_db()

    elif cmd == "unban" and is_owner(s):
        for u in m:
            if u in db["banned"]:
                db["banned"].remove(u)
        save_db()

    elif cmd == "masskick" and is_owner(s):
        group = cl.getGroup(g)
        members = [m.mid for m in group.members]
        masskick(g, members)

    elif cmd == "panic" and is_owner(s):
        db["shield"] = True
        db["freeze"] = True
        save_db()
        send(g, "تم تفعيل وضع الطوارئ")

    elif cmd == "ghost" and is_owner(s):
        db["ghost"] = True
        save_db()

    elif cmd == "unghost" and is_owner(s):
        db["ghost"] = False
        save_db()
        send(g, "تم إلغاء الوضع الشبحي")

# ============ OPS HANDLER ============

def handle_op(o):
    try:
        # Anti-kick protection
        if o.type == 19 and db["protect"]["kick"]:
            kicker = o.param2
            target = o.param3
            group = o.param1

            if target == my_mid:
                cl.acceptGroupInvitation(group)
                safe_kick(group, kicker, True)
                db["stats"]["protections"] += 1
                save_db()
    except:
        pass

# ============ MAIN LOOP ============

def main():
    while True:
        try:
            for o in op.singleTrace(50):
                if o.type == 26:
                    handle_msg(o.message)
                else:
                    handle_op(o)
        except:
            time.sleep(1)

main()
