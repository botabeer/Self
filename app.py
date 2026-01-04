import json
import time
import os
import getpass
from datetime import datetime
from collections import defaultdict

print("\n" + "="*60)
print("بوت حماية LINE - النسخة الاحترافية")
print("="*60)

try:
    from linepy import LINE, OEPoll
    print("linepy جاهز")
except ImportError:
    print("\nlinepy غير مثبت!")
    print("\nللتثبيت: pip install git+https://github.com/dyseo/linepy.git")
    exit(1)

DB_FILE = "db.json"
LOG_FILE = "logs.txt"
TOKEN_FILE = "token.txt"
AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5
MAX_KICK_PER_MIN = 3
PROTECT_REJOIN_DELAY = 2

DEFAULT_DB = {
    "owners": [],
    "admins": [],
    "vip": [],
    "banned": [],
    "muted": [],
    "warnings": {},
    "lock": {},
    "freeze": {},
    "watched": {},
    "ghost_mode": False,
    "shield_mode": False,
    "protect": {
        "kick": True,
        "invite": True,
        "qr": True,
        "bots": True,
        "spam": True,
        "flood": True
    },
    "whitelist_bots": [],
    "stats": {
        "kicks": 0,
        "bans": 0,
        "protections": 0,
        "messages": 0
    },
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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def login():
    print("\n" + "-"*60)
    print("تسجيل الدخول إلى LINE")
    print("-"*60)
    if os.path.exists(TOKEN_FILE):
        try:
            print("محاولة تسجيل الدخول بالتوكن...")
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
            client = LINE(token)
            print("تم تسجيل الدخول!")
            return client
        except:
            print("التوكن غير صالح")
            os.remove(TOKEN_FILE)
    print("\nاستخدم حساب LINE ثانوي!")
    email = input("البريد: ").strip()
    password = getpass.getpass("كلمة المرور: ")
    try:
        print("\nجاري تسجيل الدخول...")
        client = LINE(email, password)
        with open(TOKEN_FILE, "w") as f:
            f.write(client.authToken)
        print("تم تسجيل الدخول!")
        print(f"الحساب: {client.profile.displayName}")
        return client
    except Exception as e:
        print(f"\nفشل تسجيل الدخول: {e}")
        exit(1)

cl = login()
op = OEPoll(cl)
my_mid = cl.profile.mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()

print("\n" + "="*60)
print(f"البوت جاهز: {cl.profile.displayName}")
print(f"المعرف: {my_mid}")
print("="*60 + "\n")

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

def is_watched(u):
    return u in db.get("watched", {})

user_msgs = defaultdict(list)

def is_spam(u):
    if is_vip(u) or not db["protect"]["spam"]:
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

def is_bot(name):
    keywords = ["bot", "self", "auto"]
    return any(k in name.lower() for k in keywords)

def safe_kick(g, target, reason=""):
    try:
        if target == my_mid or is_owner(target):
            return False
        cl.kickoutFromGroup(g, [target])
        db["stats"]["kicks"] += 1
        save_db()
        log(f"طرد {target} - {reason}")
        return True
    except:
        return False

def get_mentioned_mid(msg):
    try:
        if msg.contentMetadata and "MENTION" in msg.contentMetadata:
            data = msg.contentMetadata["MENTION"]
            return data.split('"M":"')[1].split('"')[0]
    except:
        pass
    return None

def send_msg(g, text):
    if not db["ghost_mode"]:
        cl.sendMessage(g, text)

def handle_message(msg):
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
        safe_kick(group, sender, "محظور")
        return
    
    if is_muted(sender):
        safe_kick(group, sender, "مكتوم")
        return
    
    if db["lock"].get(group) and not is_admin(sender):
        safe_kick(group, sender, "مقفل")
        return
    
    if db["shield_mode"] and not is_admin(sender):
        safe_kick(group, sender, "درع")
        return
    
    if is_spam(sender):
        log(f"سبام من {sender}")
        return
    
    if text == ".":
        send_msg(group, ".")
        return
    
    if cmd == "id":
        send_msg(group, sender)
        return
    
    if cmd == "gid":
        send_msg(group, group)
        return
    
    if cmd == "r" and is_admin(sender):
        global db
        db = load_db()
        send_msg(group, "تم إعادة التحميل")
        return
    
    if cmd in ["sk", "x"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            safe_kick(group, target, "طرد صامت")
        return
    
    if cmd in ["sm", "z"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["muted"]:
                db["muted"].append(target)
                save_db()
        return
    
    if cmd == "zz" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["muted"]:
            db["muted"].remove(target)
            save_db()
        return
    
    if cmd == "sw" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            add_warn(target)
        return
    
    if cmd == "help":
        help_txt = """=== أوامر البوت ===

عامة:
help, myid, myrole, warns, stats

مشرفين:
kick, ban, unban, mute, unmute
warn, clearwarn, lock, unlock
ghost on/off, shield on/off

مالك:
owner add/remove
admin add/remove
vip add/remove
protect on/off
enable/disable"""
        send_msg(group, help_txt)
        return
    
    if cmd == "myid":
        send_msg(group, f"معرفك:\n{sender}")
        return
    
    if cmd == "myrole":
        if is_owner(sender):
            role = "مالك"
        elif is_admin(sender):
            role = "مشرف"
        elif is_vip(sender):
            role = "VIP"
        else:
            role = "عضو"
        send_msg(group, f"دورك: {role}")
        return
    
    if cmd == "warns":
        w = get_warns(sender)
        send_msg(group, f"لديك {w} تحذير")
        return
    
    if cmd == "stats":
        txt = f"""=== إحصائيات ===
الطردات: {db['stats']['kicks']}
الحظر: {db['stats']['bans']}
الحمايات: {db['stats']['protections']}
الرسائل: {db['stats']['messages']}"""
        send_msg(group, txt)
        return
    
    if cmd == "kick" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if safe_kick(group, target, "مشرف"):
                send_msg(group, "تم الطرد")
        return
    
    if cmd == "ban" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["banned"]:
                db["banned"].append(target)
                save_db()
                safe_kick(group, target, "محظور")
                db["stats"]["bans"] += 1
                send_msg(group, "تم الحظر")
        return
    
    if cmd == "unban" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["banned"]:
            db["banned"].remove(target)
            save_db()
            send_msg(group, "تم إلغاء الحظر")
        return
    
    if cmd == "mute" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["muted"]:
                db["muted"].append(target)
                save_db()
                send_msg(group, "تم الكتم")
        return
    
    if cmd == "unmute" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["muted"]:
            db["muted"].remove(target)
            save_db()
            send_msg(group, "تم إلغاء الكتم")
        return
    
    if cmd == "warn" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            w = add_warn(target)
            send_msg(group, f"تحذير! الإجمالي: {w}/{AUTO_WARN_LIMIT}")
            if w >= AUTO_WARN_LIMIT:
                safe_kick(group, target, "تحذيرات")
                clear_warn(target)
        return
    
    if cmd == "clearwarn" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target:
            clear_warn(target)
            send_msg(group, "تم مسح التحذيرات")
        return
    
    if cmd == "lock" and is_admin(sender):
        db["lock"][group] = True
        save_db()
        send_msg(group, "تم قفل المجموعة")
        return
    
    if cmd == "unlock" and is_admin(sender):
        db["lock"][group] = False
        save_db()
        send_msg(group, "تم فتح المجموعة")
        return
    
    if cmd == "ghost on" and is_admin(sender):
        db["ghost_mode"] = True
        save_db()
        return
    
    if cmd == "ghost off" and is_admin(sender):
        db["ghost_mode"] = False
        save_db()
        send_msg(group, "تم إيقاف الشبح")
        return
    
    if cmd == "shield on" and is_admin(sender):
        db["shield_mode"] = True
        save_db()
        send_msg(group, "تم تشغيل الدرع")
        return
    
    if cmd == "shield off" and is_admin(sender):
        db["shield_mode"] = False
        save_db()
        send_msg(group, "تم إيقاف الدرع")
        return
    
    if cmd.startswith("owner add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["owners"]:
            db["owners"].append(target)
            save_db()
            send_msg(group, "تمت إضافة المالك")
        return
    
    if cmd.startswith("owner remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["owners"] and target != my_mid:
            db["owners"].remove(target)
            save_db()
            send_msg(group, "تم حذف المالك")
        return
    
    if cmd.startswith("admin add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["admins"]:
            db["admins"].append(target)
            save_db()
            send_msg(group, "تمت إضافة المشرف")
        return
    
    if cmd.startswith("admin remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["admins"]:
            db["admins"].remove(target)
            save_db()
            send_msg(group, "تم حذف المشرف")
        return
    
    if cmd.startswith("vip add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["vip"]:
            db["vip"].append(target)
            save_db()
            send_msg(group, "تمت إضافة VIP")
        return
    
    if cmd.startswith("vip remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["vip"]:
            db["vip"].remove(target)
            save_db()
            send_msg(group, "تم حذف VIP")
        return
    
    if cmd == "protect on" and is_owner(sender):
        for key in db["protect"]:
            db["protect"][key] = True
        save_db()
        send_msg(group, "تم تشغيل الحماية")
        return
    
    if cmd == "protect off" and is_owner(sender):
        for key in db["protect"]:
            db["protect"][key] = False
        save_db()
        send_msg(group, "تم إيقاف الحماية")
        return
    
    if cmd == "enable" and is_owner(sender):
        db["enabled"] = True
        save_db()
        send_msg(group, "تم تفعيل البوت")
        return
    
    if cmd == "disable" and is_owner(sender):
        db["enabled"] = False
        save_db()
        send_msg(group, "تم تعطيل البوت")
        return

def handle_operation(op_obj):
    try:
        op_type = op_obj.type
        if op_type == 13:
            group = op_obj.param1
            invitee = op_obj.param3
            if db["protect"]["bots"]:
                try:
                    contact = cl.getContact(invitee)
                    if is_bot(contact.displayName):
                        safe_kick(group, invitee, "بوت")
                        db["stats"]["protections"] += 1
                except:
                    pass
            if is_banned(invitee):
                safe_kick(group, invitee, "محظور")
                db["stats"]["protections"] += 1
        elif op_type == 19:
            group = op_obj.param1
            kicker = op_obj.param2
            kicked = op_obj.param3
            if kicked == my_mid and db["protect"]["kick"]:
                if not is_owner(kicker):
                    time.sleep(PROTECT_REJOIN_DELAY)
                    try:
                        cl.acceptGroupInvitation(group)
                        safe_kick(group, kicker, "طرد البوت")
                        db["stats"]["protections"] += 1
                    except:
                        pass
    except:
        pass

def main():
    while True:
        try:
            ops = op.singleTrace(count=50)
            if ops:
                for op_obj in ops:
                    try:
                        if op_obj.type == 26:
                            handle_message(op_obj.message)
                        else:
                            handle_operation(op_obj)
                    except:
                        pass
        except KeyboardInterrupt:
            print("\nإيقاف البوت...")
            save_db()
            break
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()
