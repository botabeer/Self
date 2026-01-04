import json
import time
import os
import getpass
from datetime import datetime
from collections import defaultdict

print("\n" + "="*60)
print("بوت حماية LINE")
print("="*60)

try:
    from linepy import LINE, OEPoll
    print("linepy جاهز")
except ImportError:
    print("linepy غير مثبت!")
    exit(1)

DB_FILE = "db.json"
LOG_FILE = "logs.txt"
TOKEN_FILE = "token.txt"
AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5

DEFAULT_DB = {
    "owners": [],
    "admins": [],
    "vip": [],
    "banned": [],
    "muted": [],
    "warnings": {},
    "lock": {},
    "ghost_mode": False,
    "shield_mode": False,
    "stats": {"kicks": 0, "bans": 0, "messages": 0},
    "enabled": True
}

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump(DEFAULT_DB, f, indent=2)
        return DEFAULT_DB.copy()
    with open(DB_FILE) as f:
        db = json.load(f)
    for key in DEFAULT_DB:
        if key not in db:
            db[key] = DEFAULT_DB[key]
    return db

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {text}\n")

def login():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
            return LINE(token)
        except:
            os.remove(TOKEN_FILE)
    email = input("البريد: ").strip()
    password = getpass.getpass("كلمة المرور: ")
    client = LINE(email, password)
    with open(TOKEN_FILE, "w") as f:
        f.write(client.authToken)
    return client

cl = login()
op = OEPoll(cl)
my_mid = cl.profile.mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print(f"البوت جاهز: {cl.profile.displayName}\n")

def is_owner(u):
    return u in db["owners"]

def is_admin(u):
    return u in db["admins"] or is_owner(u)

def is_vip(u):
    return u in db["vip"]

def is_banned(u):
    return u in db["banned"]

def is_muted(u):
    return u in db["muted"]

user_msgs = defaultdict(list)

def is_spam(u):
    if is_vip(u):
        return False
    now = time.time()
    user_msgs[u] = [t for t in user_msgs[u] if now - t < SPAM_TIME]
    user_msgs[u].append(now)
    return len(user_msgs[u]) > SPAM_COUNT

def add_warn(u):
    if u not in db["warnings"]:
        db["warnings"][u] = 0
    db["warnings"][u] += 1
    save_db()
    return db["warnings"][u]

def clear_warn(u):
    if u in db["warnings"]:
        del db["warnings"][u]
        save_db()

def get_warns(u):
    return db["warnings"].get(u, 0)

def safe_kick(g, target):
    try:
        if target == my_mid or is_owner(target):
            return False
        cl.kickoutFromGroup(g, [target])
        db["stats"]["kicks"] += 1
        save_db()
        return True
    except:
        return False

def get_mentioned(msg):
    try:
        if msg.contentMetadata and "MENTION" in msg.contentMetadata:
            data = msg.contentMetadata["MENTION"]
            return data.split('"M":"')[1].split('"')[0]
    except:
        return None

def send(g, text):
    if not db["ghost_mode"]:
        cl.sendMessage(g, text)

def handle_msg(msg):
    if not msg.text:
        return
    text = msg.text.strip()
    cmd = text.lower()
    sender = msg._from
    group = msg.to
    db["stats"]["messages"] += 1
    if not db["enabled"]:
        return
    if is_banned(sender):
        safe_kick(group, sender)
        return
    if is_muted(sender):
        safe_kick(group, sender)
        return
    if db["lock"].get(group) and not is_admin(sender):
        safe_kick(group, sender)
        return
    if db["shield_mode"] and not is_admin(sender):
        safe_kick(group, sender)
        return
    if is_spam(sender):
        return
    if text == ".":
        send(group, ".")
    elif cmd == "id":
        send(group, sender)
    elif cmd == "gid":
        send(group, group)
    elif cmd == "r" and is_admin(sender):
        global db
        db = load_db()
        send(group, "تم")
    elif cmd in ["sk", "x"] and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t):
            safe_kick(group, t)
    elif cmd in ["sm", "z"] and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t) and t not in db["muted"]:
            db["muted"].append(t)
            save_db()
    elif cmd == "zz" and is_admin(sender):
        t = get_mentioned(msg)
        if t and t in db["muted"]:
            db["muted"].remove(t)
            save_db()
    elif cmd == "sw" and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t):
            add_warn(t)
    elif cmd == "help":
        send(group, "أوامر البوت:\nhelp, myid, warns, stats\nkick, ban, mute, warn, lock\nadmin add, vip add")
    elif cmd == "myid":
        send(group, sender)
    elif cmd == "warns":
        send(group, f"تحذيرات: {get_warns(sender)}")
    elif cmd == "stats":
        send(group, f"طردات: {db['stats']['kicks']}\nحظر: {db['stats']['bans']}")
    elif cmd == "kick" and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t):
            safe_kick(group, t)
            send(group, "تم")
    elif cmd == "ban" and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t) and t not in db["banned"]:
            db["banned"].append(t)
            save_db()
            safe_kick(group, t)
            db["stats"]["bans"] += 1
            send(group, "تم")
    elif cmd == "unban" and is_admin(sender):
        t = get_mentioned(msg)
        if t and t in db["banned"]:
            db["banned"].remove(t)
            save_db()
            send(group, "تم")
    elif cmd == "mute" and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t) and t not in db["muted"]:
            db["muted"].append(t)
            save_db()
            send(group, "تم")
    elif cmd == "unmute" and is_admin(sender):
        t = get_mentioned(msg)
        if t and t in db["muted"]:
            db["muted"].remove(t)
            save_db()
            send(group, "تم")
    elif cmd == "warn" and is_admin(sender):
        t = get_mentioned(msg)
        if t and not is_owner(t):
            w = add_warn(t)
            send(group, f"تحذير: {w}/{AUTO_WARN_LIMIT}")
            if w >= AUTO_WARN_LIMIT:
                safe_kick(group, t)
                clear_warn(t)
    elif cmd == "clearwarn" and is_admin(sender):
        t = get_mentioned(msg)
        if t:
            clear_warn(t)
            send(group, "تم")
    elif cmd == "lock" and is_admin(sender):
        db["lock"][group] = True
        save_db()
        send(group, "تم")
    elif cmd == "unlock" and is_admin(sender):
        db["lock"][group] = False
        save_db()
        send(group, "تم")
    elif cmd == "ghost on" and is_admin(sender):
        db["ghost_mode"] = True
        save_db()
    elif cmd == "ghost off" and is_admin(sender):
        db["ghost_mode"] = False
        save_db()
        send(group, "تم")
    elif cmd == "shield on" and is_admin(sender):
        db["shield_mode"] = True
        save_db()
        send(group, "تم")
    elif cmd == "shield off" and is_admin(sender):
        db["shield_mode"] = False
        save_db()
        send(group, "تم")
    elif cmd.startswith("admin add") and is_owner(sender):
        t = get_mentioned(msg)
        if t and t not in db["admins"]:
            db["admins"].append(t)
            save_db()
            send(group, "تم")
    elif cmd.startswith("admin remove") and is_owner(sender):
        t = get_mentioned(msg)
        if t and t in db["admins"]:
            db["admins"].remove(t)
            save_db()
            send(group, "تم")
    elif cmd.startswith("vip add") and is_owner(sender):
        t = get_mentioned(msg)
        if t and t not in db["vip"]:
            db["vip"].append(t)
            save_db()
            send(group, "تم")
    elif cmd.startswith("vip remove") and is_owner(sender):
        t = get_mentioned(msg)
        if t and t in db["vip"]:
            db["vip"].remove(t)
            save_db()
            send(group, "تم")
    elif cmd == "enable" and is_owner(sender):
        db["enabled"] = True
        save_db()
        send(group, "تم")
    elif cmd == "disable" and is_owner(sender):
        db["enabled"] = False
        save_db()
        send(group, "تم")

def handle_op(op_obj):
    try:
        if op_obj.type == 13:
            if is_banned(op_obj.param3):
                safe_kick(op_obj.param1, op_obj.param3)
        elif op_obj.type == 19:
            if op_obj.param3 == my_mid and not is_owner(op_obj.param2):
                time.sleep(2)
                try:
                    cl.acceptGroupInvitation(op_obj.param1)
                    safe_kick(op_obj.param1, op_obj.param2)
                except:
                    pass
    except:
        pass

def main():
    while True:
        try:
            ops = op.singleTrace(count=50)
            if ops:
                for o in ops:
                    try:
                        if o.type == 26:
                            handle_msg(o.message)
                        else:
                            handle_op(o)
                    except:
                        pass
        except KeyboardInterrupt:
            save_db()
            break
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()
