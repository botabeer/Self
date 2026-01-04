import json, time, os, getpass, threading
from datetime import datetime, timedelta
from collections import defaultdict

print("\n" + "="*60)
print("بوت حماية LINE - النسخة الاحترافية")
print("="*60)

# فحص المكتبات
try:
    from linepy import LINE, OEPoll
    print("linepy جاهز")
except ImportError:
    print("\nlinepy غير مثبت!")
    print("\nللتثبيت: pip install git+https://github.com/dyseo/linepy.git")
    exit(1)

# الإعدادات
DB_FILE = "db.json"
LOG_FILE = "logs.txt"
TOKEN_FILE = "token.txt"

# الحدود
AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5
MAX_KICK_PER_MIN = 3
PROTECT_REJOIN_DELAY = 2

# قاعدة البيانات الافتراضية
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
    "kick_history": {},
    "last_kick": "",
    "last_ban": "",
    "stats": {
        "kicks": 0,
        "bans": 0,
        "protections": 0,
        "messages": 0
    },
    "enabled": True
}

# دوال قاعدة البيانات
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

# نظام السجلات
def log(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

# تسجيل الدخول
def login():
    print("\n" + "-"*60)
    print("تسجيل الدخول إلى LINE")
    print("-"*60)
    
    if os.path.exists(TOKEN_FILE):
        try:
            print("محاولة تسجيل الدخول بالتوكن المحفوظ...")
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
            client = LINE(token)
            print("تم تسجيل الدخول بنجاح!")
            return client
        except:
            print("التوكن غير صالح، جاري الحذف...")
            os.remove(TOKEN_FILE)
    
    print("\nاستخدم حساب LINE ثانوي فقط!")
    email = input("البريد الإلكتروني: ").strip()
    password = getpass.getpass("كلمة المرور: ")
    
    try:
        print("\nجاري تسجيل الدخول...")
        client = LINE(email, password)
        
        with open(TOKEN_FILE, "w") as f:
            f.write(client.authToken)
        
        print("تم تسجيل الدخول بنجاح!")
        print(f"الحساب: {client.profile.displayName}")
        return client
    except Exception as e:
        print(f"\nفشل تسجيل الدخول: {e}")
        print("\nتحقق من:")
        print("  - البريد الإلكتروني وكلمة المرور صحيحة")
        print("  - تعطيل المصادقة الثنائية في إعدادات LINE")
        print("  - الاتصال بالإنترنت")
        exit(1)

cl = login()
op = OEPoll(cl)
my_mid = cl.profile.mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()
    log(f"تمت إضافة {my_mid} كمالك")

print("\n" + "="*60)
print(f"البوت جاهز: {cl.profile.displayName}")
print(f"المعرف: {my_mid}")
print(f"المالكون: {len(db['owners'])} | المشرفون: {len(db['admins'])}")
print("="*60 + "\n")
print("البوت يعمل الآن...")
print("اضغط Ctrl+C للإيقاف\n")
print("="*60 + "\n")

# نظام الصلاحيات
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
    return u in db["watched"]

def get_role(u):
    if is_owner(u):
        return "مالك"
    elif is_admin(u):
        return "مشرف"
    elif is_vip(u):
        return "VIP"
    else:
        return "عضو"

# نظام مكافحة السبام
user_msgs = defaultdict(list)
spammers = []

def is_spam(u):
    if is_vip(u) or not db["protect"]["spam"]:
        return False
    
    now = time.time()
    user_msgs[u] = [t for t in user_msgs[u] if now - t < SPAM_TIME]
    user_msgs[u].append(now)
    
    if len(user_msgs[u]) > SPAM_COUNT:
        if u not in spammers:
            spammers.append(u)
        return True
    
    return False

# نظام مكافحة الفلود
kick_history = defaultdict(list)

def can_kick(u, g):
    if not db["protect"]["flood"]:
        return True
    
    now = time.time()
    key = f"{u}:{g}"
    kick_history[key] = [t for t in kick_history[key] if now - t < 60]
    
    if len(kick_history[key]) >= MAX_KICK_PER_MIN:
        return False
    
    kick_history[key].append(now)
    return True

# نظام التحذيرات
def add_warn(u, silent=False):
    db["warnings"].setdefault(u, 0)
    db["warnings"][u] += 1
    save_db()
    if not silent:
        log(f"تمت إضافة تحذير لـ {u} (الإجمالي: {db['warnings'][u]})")
    return db["warnings"][u]

def clear_warn(u):
    if u in db["warnings"]:
        del db["warnings"][u]
        save_db()
        log(f"تم مسح التحذيرات لـ {u}")

def get_warns(u):
    return db["warnings"].get(u, 0)

# كشف البوتات
def is_bot(name):
    bot_keywords = ["bot", "self", "auto", "[bot]", "{bot}", "robot"]
    name_lower = name.lower()
    return any(keyword in name_lower for keyword in bot_keywords)

def is_whitelisted_bot(mid):
    return mid in db["whitelist_bots"] or mid == my_mid

# دوال الحماية
def safe_kick(g, target, reason="", silent=False):
    try:
        if target == my_mid:
            return False
        
        if is_owner(target):
            return False
        
        cl.kickoutFromGroup(g, [target])
        db["stats"]["kicks"] += 1
        db["last_kick"] = f"{target} - {reason} - {datetime.now()}"
        save_db()
        if not silent:
            log(f"تم طرد {target} من {g} - {reason}")
        return True
    except Exception as e:
        if not silent:
            log(f"فشل الطرد: {e}")
        return False

def rejoin_group(g):
    try:
        time.sleep(PROTECT_REJOIN_DELAY)
        cl.acceptGroupInvitation(g)
        log(f"تمت إعادة الانضمام للمجموعة {g}")
        return True
    except Exception as e:
        log(f"فشلت إعادة الانضمام: {e}")
        return False

# محلل المنشن
def get_mentioned_mid(msg):
    try:
        if not msg.contentMetadata or "MENTION" not in msg.contentMetadata:
            return None
        
        mention_data = msg.contentMetadata["MENTION"]
        mid = mention_data.split('"M":"')[1].split('"')[0]
        return mid
    except:
        return None

# إرسال الرسائل (وضع الشبح)
def send_msg(g, text):
    if not db["ghost_mode"]:
        cl.sendMessage(g, text)

# معالج الأوامر
def handle_message(msg):
    if not msg.text:
        return
    
    text = msg.text.strip()
    text_lower = text.lower()
    sender = msg._from
    group = msg.to
    
    db["stats"]["messages"] += 1
    
    if not db["enabled"]:
        return
    
    # طرد تلقائي للمحظورين
    if is_banned(sender):
        safe_kick(group, sender, "مستخدم محظور", True)
        return
    
    # طرد تلقائي للمكتومين
    if is_muted(sender):
        safe_kick(group, sender, "مستخدم مكتوم", True)
        return
    
    # قفل المجموعة
    if db["lock"].get(group, False) and not is_admin(sender):
        safe_kick(group, sender, "المجموعة مقفلة", True)
        return
    
    # وضع التجميد
    if db["freeze"].get(group, False) and not is_admin(sender):
        safe_kick(group, sender, "وضع التجميد", True)
        return
    
    # وضع الدرع
    if db["shield_mode"] and not is_admin(sender):
        safe_kick(group, sender, "وضع الدرع", True)
        return
    
    # وضع المراقبة
    if is_watched(sender) and not is_admin(sender):
        if is_spam(sender):
            safe_kick(group, sender, "مراقب + سبام", True)
            return
    
    # مكافحة السبام
    if is_spam(sender):
        log(f"تم اكتشاف سبام من {sender}")
        return
    
    # الأوامر السرية (مخفية)
    if text == ".":
        send_msg(group, ".")
        return
    
    if text_lower == "id":
        send_msg(group, sender)
        return
    
    if text_lower == "gid":
        send_msg(group, group)
        return
    
    if text_lower == "r" and is_admin(sender):
        global db
        db = load_db()
        send_msg(group, "تم إعادة التحميل")
        return
    
    if text_lower in ["sk", "x"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            safe_kick(group, target, "طرد صامت", True)
        return
    
    if text_lower in ["sm", "z"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["muted"]:
                db["muted"].append(target)
                save_db()
        return
    
    if text_lower == "zz" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["muted"]:
            db["muted"].remove(target)
            save_db()
        return
    
    if text_lower == "sw" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            add_warn(target, True)
        return
    
    # أوامر عامة
    if text_lower == "help":
        help_text = """=== أوامر البوت ===

أوامر عامة:
help - عرض هذه المساعدة
myid - عرض معرفك
myrole - عرض دورك
warns - عرض تحذيراتك
stats - إحصائيات البوت

أوامر المشرفين:
kick @mention - طرد عضو
ban @mention - حظر عضو
unban @mention - إلغاء حظر
mute @mention - كتم عضو
unmute @mention - إلغاء كتم
warn @mention - تحذير عضو
clearwarn @mention - مسح تحذيرات
lock - قفل المجموعة
unlock - فتح المجموعة
ghost on/off - تشغيل وضع الشبح
shield on/off - تشغيل وضع الدرع

أوامر المالك:
owner add @mention - إضافة مالك
admin add @mention - إضافة مشرف
vip add @mention - إضافة VIP
protect on/off - تشغيل الحماية
enable/disable - تفعيل البوت"""
        send_msg(group, help_text)
        return
    
    if text_lower == "myid":
        send_msg(group, f"معرفك:\n{sender}")
        return
    
    if text_lower == "myrole":
        role = get_role(sender)
        send_msg(group, f"دورك: {role}")
        return
    
    if text_lower == "warns":
        warns = get_warns(sender)
        send_msg(group, f"لديك {warns} تحذير(ات)")
        return
    
    if text_lower == "stats":
        stats_text = f"""=== إحصائيات البوت ===
الطردات: {db['stats']['kicks']}
الحظر: {db['stats']['bans']}
الحمايات: {db['stats']['protections']}
الرسائل: {db['stats']['messages']}
المالكون: {len(db['owners'])}
المشرفون: {len(db['admins'])}
VIP: {len(db['vip'])}
المحظورون: {len(db['banned'])}
المكتومون: {len(db['muted'])}"""
        send_msg(group, stats_text)
        return
    
    # أوامر المشرفين
    if text_lower == "kick" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if safe_kick(group, target, "بواسطة مشرف"):
                send_msg(group, "تم الطرد")
            else:
                send_msg(group, "فشل الطرد")
        return
    
    if text_lower == "ban" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["banned"]:
                db["banned"].append(target)
                save_db()
                safe_kick(group, target, "محظور")
                db["stats"]["bans"] += 1
                send_msg(group, "تم الحظر")
        return
    
    if text_lower == "unban" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["banned"]:
            db["banned"].remove(target)
            save_db()
            send_msg(group, "تم إلغاء الحظر")
        return
    
    if text_lower == "mute" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["muted"]:
                db["muted"].append(target)
                save_db()
                send_msg(group, "تم الكتم")
        return
    
    if text_lower == "unmute" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["muted"]:
            db["muted"].remove(target)
            save_db()
            send_msg(group, "تم إلغاء الكتم")
        return
    
    if text_lower == "warn" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            warns = add_warn(target)
            send_msg(group, f"تحذير! الإجمالي: {warns}/{AUTO_WARN_LIMIT}")
            if warns >= AUTO_WARN_LIMIT:
                safe_kick(group, target, "تحذيرات متعددة")
                clear_warn(target)
        return
    
    if text_lower == "clearwarn" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target:
            clear_warn(target)
            send_msg(group, "تم مسح التحذيرات")
        return
    
    if text_lower == "lock" and is_admin(sender):
        db["lock"][group] = True
        save_db()
        send_msg(group, "تم قفل المجموعة")
        return
    
    if text_lower == "unlock" and is_admin(sender):
        db["lock"][group] = False
        save_db()
        send_msg(group, "تم فتح المجموعة")
        return
    
    if text_lower == "ghost on" and is_admin(sender):
        db["ghost_mode"] = True
        save_db()
        return
    
    if text_lower == "ghost off" and is_admin(sender):
        db["ghost_mode"] = False
        save_db()
        send_msg(group, "تم إيقاف وضع الشبح")
        return
    
    if text_lower == "shield on" and is_admin(sender):
        db["shield_mode"] = True
        save_db()
        send_msg(group, "تم تشغيل وضع الدرع")
        return
    
    if text_lower == "shield off" and is_admin(sender):
        db["shield_mode"] = False
        save_db()
        send_msg(group, "تم إيقاف وضع الدرع")
        return
    
    # أوامر المالك
    if text_lower.startswith("owner add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["owners"]:
            db["owners"].append(target)
            save_db()
            send_msg(group, "تمت إضافة المالك")
        return
    
    if text_lower.startswith("owner remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["owners"] and target != my_mid:
            db["owners"].remove(target)
            save_db()
            send_msg(group, "تم حذف المالك")
        return
    
    if text_lower.startswith("admin add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["admins"]:
            db["admins"].append(target)
            save_db()
            send_msg(group, "تمت إضافة المشرف")
        return
    
    if text_lower.startswith("admin remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["admins"]:
            db["admins"].remove(target)
            save_db()
            send_msg(group, "تم حذف المشرف")
        return
    
    if text_lower.startswith("vip add") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target not in db["vip"]:
            db["vip"].append(target)
            save_db()
            send_msg(group, "تمت إضافة VIP")
        return
    
    if text_lower.startswith("vip remove") and is_owner(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["vip"]:
            db["vip"].remove(target)
            save_db()
            send_msg(group, "تم حذف VIP")
        return
    
    if text_lower == "protect on" and is_owner(sender):
        for key in db["protect"]:
            db["protect"][key] = True
        save_db()
        send_msg(group, "تم تشغيل جميع الحمايات")
        return
    
    if text_lower == "protect off" and is_owner(sender):
        for key in db["protect"]:
            db["protect"][key] = False
        save_db()
        send_msg(group, "تم إيقاف جميع الحمايات")
        return
    
    if text_lower == "enable" and is_owner(sender):
        db["enabled"] = True
        save_db()
        send_msg(group, "تم تفعيل البوت")
        return
    
    if text_lower == "disable" and is_owner(sender):
        db["enabled"] = False
        save_db()
        send_msg(group, "تم تعطيل البوت")
        return

# معالج الأحداث
def handle_operation(op_obj):
    try:
        op_type = op_obj.type
        
        # إضافة عضو جديد
        if op_type == 13:
            group = op_obj.param1
            inviter = op_obj.param2
            invitee = op_obj.param3
            
            # حماية من البوتات
            if db["protect"]["bots"]:
                try:
                    contact = cl.getContact(invitee)
                    if is_bot(contact.displayName) and not is_whitelisted_bot(invitee):
                        safe_kick(group, invitee, "بوت غير مصرح", True)
                        db["stats"]["protections"] += 1
                except:
                    pass
            
            # فحص المحظورين
            if is_banned(invitee):
                safe_kick(group, invitee, "محظور", True)
                db["stats"]["protections"] += 1
        
        # طرد البوت
        elif op_type == 19:
            group = op_obj.param1
            kicker = op_obj.param2
            kicked = op_obj.param3
            
            if kicked == my_mid and db["protect"]["kick"]:
                if not is_owner(kicker):
                    rejoin_group(group)
                    safe_kick(group, kicker, "طرد البوت")
                    db["stats"]["protections"] += 1
        
        # دعوة عبر QR
        elif op_type == 17:
            if db["protect"]["qr"]:
                group = op_obj.param1
                joiner = op_obj.param2
                
                if not is_admin(joiner):
                    safe_kick(group, joiner, "انضم عبر QR", True)
                    db["stats"]["protections"] += 1
    
    except Exception as e:
        log(f"خطأ في معالجة العملية: {e}")

# الحلقة الرئيسية
def main():
    while True:
        try:
            ops = op.singleTrace(count=50)
            
            if ops:
                for op_obj in ops:
                    try:
                        # معالجة الرسائل
                        if op_obj.type == 26:
                            msg = op_obj.message
                            handle_message(msg)
                        
                        # معالجة الأحداث
                        else:
                            handle_operation(op_obj)
                    
                    except Exception as e:
                        log(f"خطأ في معالجة العملية: {e}")
        
        except KeyboardInterrupt:
            print("\n\nجاري إيقاف البوت...")
            save_db()
            print("تم الإيقاف بنجاح!")
            break
        
        except Exception as e:
            log(f"خطأ في الحلقة الرئيسية: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
