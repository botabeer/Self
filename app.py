import json
import time
import os
import re
from datetime import datetime
from collections import defaultdict

try:
    from linepy import LINE
except ImportError:
    print("❌ خطأ: مكتبة linepy غير مثبتة!")
    print("\nشغّل: pip install linepy")
    exit(1)

# ============ CONFIG ============

DB_FILE = "db.json"
LOG_FILE = "logs.txt"

AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5
MASSKICK_BATCH = 3
MASSKICK_DELAY = 1

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
        "invite": True
    },
    "stats": {
        "messages": 0,
        "kicks": 0,
        "bans": 0,
        "protections": 0
    }
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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {txt}\n")
    print(f"[{timestamp}] {txt}")

db = load_db()

# ============ LOGIN ============

print("\n" + "="*60)
print("🤖 LINE Protection Bot")
print("="*60 + "\n")

email = input("📧 الإيميل: ").strip()
password = input("🔑 الباسورد: ").strip()

print("\n⏳ جاري تسجيل الدخول...")

try:
    cl = LINE(email, password)
    profile = cl.getProfile()
    
    print(f"\n✅ تم تسجيل الدخول بنجاح!")
    print(f"👤 الحساب: {profile.displayName}")
    print(f"🆔 MID: {profile.mid}")
    
    my_mid = profile.mid
    
    if my_mid not in db["owners"]:
        db["owners"].append(my_mid)
        save_db()
    
    print("\n" + "="*60)
    print("✅ البوت جاهز ويستقبل الرسائل")
    print("="*60)
    print("⌨️  اضغط CTRL+C للإيقاف\n")
    
except Exception as e:
    print(f"\n❌ فشل تسجيل الدخول: {e}")
    print("\nتأكد من:")
    print("1. الإيميل والباسورد صحيحين")
    print("2. حسابك مربوط بإيميل")
    print("3. اتصال الإنترنت شغال")
    exit(1)

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
            cl.sendMessage(g, str(txt))
        except Exception as e:
            log(f"Send error: {e}")

def get_mentions(msg):
    mentions = []
    try:
        if hasattr(msg, 'contentMetadata') and msg.contentMetadata:
            if 'MENTION' in msg.contentMetadata:
                mention_data = json.loads(msg.contentMetadata['MENTION'])
                for mention in mention_data.get('MENTIONEES', []):
                    mentions.append(mention.get('M'))
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
            cl.kickoutFromGroup(g, [u])
            db["stats"]["kicks"] += 1
            save_db()
            log(f"KICK {u} from {g}")
            if not silent:
                send(g, "✅ تم طرد العضو")
    except Exception as e:
        log(f"Kick failed for {u}: {e}")

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
    kicked = 0
    batch = []
    for u in members:
        if u == my_mid or is_owner(u) or is_admin(u):
            continue
        batch.append(u)
        if len(batch) >= MASSKICK_BATCH:
            try:
                cl.kickoutFromGroup(group, batch)
                kicked += len(batch)
                log(f"Kicked batch of {len(batch)} members")
                time.sleep(MASSKICK_DELAY)
                batch = []
            except Exception as e:
                log(f"Batch kick error: {e}")
                batch = []
    
    if batch:
        try:
            cl.kickoutFromGroup(group, batch)
            kicked += len(batch)
        except:
            pass
    
    return kicked

# ============ MESSAGE HANDLER ============

def handle_msg(msg):
    try:
        s = msg._from
        g = msg.to
        text = msg.text.strip() if msg.text else ""
        cmd = text.lower()

        db["stats"]["messages"] += 1

        # حماية من المحظورين
        if is_banned(s):
            safe_kick(g, s, True)
            db["stats"]["protections"] += 1
            return

        # وضع التجميد
        if db["freeze"] and not is_admin(s):
            safe_kick(g, s, True)
            db["stats"]["protections"] += 1
            return

        # وضع الدرع
        if db["shield"] and not is_admin(s):
            safe_kick(g, s, True)
            db["stats"]["protections"] += 1
            return

        # قفل المجموعة
        if db["lock"].get(g) and not is_admin(s):
            return

        # المكتومين
        if is_muted(s):
            return

        # حماية من الروابط
        if db["protect"]["link"] and LINK_REGEX.search(text) and not is_admin(s):
            w = add_warn(s)
            db["stats"]["protections"] += 1
            if w >= AUTO_WARN_LIMIT:
                db["banned"].append(s)
                save_db()
                safe_kick(g, s, True)
            else:
                send(g, f"⚠️ ممنوع الروابط - تحذير {w}/{AUTO_WARN_LIMIT}")
            return

        # حماية من السبام
        if db["protect"]["spam"] and is_spam(s):
            w = add_warn(s)
            db["stats"]["protections"] += 1
            if w >= AUTO_WARN_LIMIT:
                db["banned"].append(s)
                save_db()
                safe_kick(g, s, True)
            return

        # نظام المراقبة
        if s in db["watch"] and not is_admin(s):
            db["watch"][s] += 1
            if db["watch"][s] >= 2:
                db["banned"].append(s)
                save_db()
                safe_kick(g, s, True)
                db["stats"]["protections"] += 1
            save_db()
            return

        m = get_mentions(msg)

        # الأوامر
        if cmd == "help" or cmd == ".help":
            send(g, """🤖 أوامر البوت الحماية

📋 للجميع:
help - قائمة الأوامر
me - معلوماتك
ping - فحص البوت
stats - الإحصائيات
time - الوقت

👮 الأدمن:
kick @user - طرد
warn @user - تحذير
clearwarn @user - حذف تحذيرات
mute @user - كتم 10 دقائق
unmute @user - فك كتم
lock - قفل الشات
unlock - فتح الشات
watch @user - مراقبة
unwatch @user - إلغاء مراقبة

👑 المالك:
addadmin @user - إضافة أدمن
deladmin @user - حذف أدمن
ban @user - حظر نهائي
unban @user - فك حظر
masskick - طرد الجميع
panic - وضع الطوارئ
ghost - وضع شبحي
unghost - إلغاء شبحي
shield - تفعيل الدرع
unshield - إلغاء الدرع
freeze - تجميد
unfreeze - فك تجميد

💡 يمكنك استخدام . قبل الأوامر""")

        elif cmd == "me" or cmd == ".me":
            role = "👑 مالك" if is_owner(s) else "👮 أدمن" if is_admin(s) else "⭐ VIP" if is_vip(s) else "👤 عضو"
            warns = db["warnings"].get(s, 0)
            send(g, f"""معلوماتك:
{role}
⚠️ تحذيرات: {warns}/{AUTO_WARN_LIMIT}
🆔 MID: {s}""")

        elif cmd == "time" or cmd == ".time":
            send(g, f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif cmd == "ping" or cmd == ".ping":
            send(g, "✅ البوت شغال ويستجيب بشكل طبيعي")

        elif cmd == "stats" or cmd == ".stats":
            send(g, f"""📊 إحصائيات البوت:

📨 الرسائل: {db['stats']['messages']}
🚫 الطردات: {db['stats']['kicks']}
⛔ الحظر: {db['stats']['bans']}
🛡️ الحمايات: {db['stats']['protections']}

👮 الأدمن: {len(db['admins'])}
⭐ VIP: {len(db['vip'])}
🚷 المحظورين: {len(db['banned'])}""")

        # أوامر الأدمن
        elif (cmd == "kick" or cmd == ".kick") and is_admin(s):
            if m:
                for u in m:
                    safe_kick(g, u)
            else:
                send(g, "❌ منشن العضو الي تبي تطرده")

        elif (cmd == "warn" or cmd == ".warn") and is_admin(s):
            if m:
                for u in m:
                    w = add_warn(u)
                    send(g, f"⚠️ تحذير {w}/{AUTO_WARN_LIMIT}")
                    if w >= AUTO_WARN_LIMIT:
                        db["banned"].append(u)
                        save_db()
                        safe_kick(g, u, True)
                        send(g, "⛔ تم الحظر بسبب التحذيرات")
            else:
                send(g, "❌ منشن العضو")

        elif (cmd == "clearwarn" or cmd == ".clearwarn") and is_admin(s):
            if m:
                for u in m:
                    db["warnings"].pop(u, None)
                save_db()
                send(g, "✅ تم حذف التحذيرات")

        elif (cmd == "mute" or cmd == ".mute") and is_admin(s):
            if m:
                for u in m:
                    db["muted"][u] = time.time() + 600
                save_db()
                send(g, "🔇 تم الكتم لمدة 10 دقائق")

        elif (cmd == "unmute" or cmd == ".unmute") and is_admin(s):
            if m:
                for u in m:
                    db["muted"].pop(u, None)
                save_db()
                send(g, "🔊 تم فك الكتم")

        elif (cmd == "lock" or cmd == ".lock") and is_admin(s):
            db["lock"][g] = True
            save_db()
            send(g, "🔒 تم قفل الشات - فقط الأدمن يقدرون يتكلمون")

        elif (cmd == "unlock" or cmd == ".unlock") and is_admin(s):
            db["lock"][g] = False
            save_db()
            send(g, "🔓 تم فتح الشات")

        elif (cmd == "watch" or cmd == ".watch") and is_admin(s):
            if m:
                for u in m:
                    db["watch"][u] = 0
                save_db()
                send(g, "👁️ تمت إضافة للمراقبة - أول رسالة = طرد")

        elif (cmd == "unwatch" or cmd == ".unwatch") and is_admin(s):
            if m:
                for u in m:
                    db["watch"].pop(u, None)
                save_db()
                send(g, "✅ تم إلغاء المراقبة")

        # أوامر المالك
        elif (cmd == "addadmin" or cmd == ".addadmin") and is_owner(s):
            if m:
                for u in m:
                    if u not in db["admins"]:
                        db["admins"].append(u)
                save_db()
                send(g, "✅ تم إضافة الأدمن")

        elif (cmd == "deladmin" or cmd == ".deladmin") and is_owner(s):
            if m:
                for u in m:
                    if u in db["admins"]:
                        db["admins"].remove(u)
                save_db()
                send(g, "✅ تم حذف الأدمن")

        elif (cmd == "ban" or cmd == ".ban") and is_owner(s):
            if m:
                for u in m:
                    if u not in db["banned"]:
                        db["banned"].append(u)
                        db["stats"]["bans"] += 1
                        safe_kick(g, u, True)
                save_db()
                send(g, "⛔ تم الحظر نهائياً")

        elif (cmd == "unban" or cmd == ".unban") and is_owner(s):
            if m:
                for u in m:
                    if u in db["banned"]:
                        db["banned"].remove(u)
                save_db()
                send(g, "✅ تم فك الحظر")

        elif (cmd == "masskick" or cmd == ".masskick") and is_owner(s):
            try:
                send(g, "⏳ جاري طرد جميع الأعضاء...")
                group = cl.getGroup(g)
                members = [mem.mid for mem in group.members]
                kicked = masskick(g, members)
                send(g, f"✅ تم طرد {kicked} عضو")
            except Exception as e:
                log(f"Masskick error: {e}")
                send(g, "❌ حدث خطأ في الطرد الجماعي")

        elif (cmd == "panic" or cmd == ".panic") and is_owner(s):
            db["shield"] = True
            db["freeze"] = True
            save_db()
            send(g, "🚨 وضع الطوارئ مفعل - كل الأعضاء سيطردون")

        elif (cmd == "ghost" or cmd == ".ghost") and is_owner(s):
            db["ghost"] = True
            save_db()

        elif (cmd == "unghost" or cmd == ".unghost") and is_owner(s):
            db["ghost"] = False
            save_db()
            send(g, "👻 تم إلغاء الوضع الشبحي")

        elif (cmd == "shield" or cmd == ".shield") and is_owner(s):
            db["shield"] = True
            save_db()
            send(g, "🛡️ تم تفعيل الدرع - كل عضو جديد يطرد")

        elif (cmd == "unshield" or cmd == ".unshield") and is_owner(s):
            db["shield"] = False
            save_db()
            send(g, "✅ تم إلغاء الدرع")

        elif (cmd == "freeze" or cmd == ".freeze") and is_owner(s):
            db["freeze"] = True
            save_db()
            send(g, "❄️ تم التجميد - لا أحد يقدر يتكلم")

        elif (cmd == "unfreeze" or cmd == ".unfreeze") and is_owner(s):
            db["freeze"] = False
            save_db()
            send(g, "✅ تم فك التجميد")

    except Exception as e:
        log(f"Handler error: {e}")

# ============ OPERATIONS HANDLER ============

def handle_operation(op):
    try:
        if db["protect"]["invite"]:
            if op.type == 13:
                if not is_admin(op.param1):
                    try:
                        cl.kickoutFromGroup(op.param2, [op.param1])
                        db["stats"]["protections"] += 1
                        log(f"Kicked inviter {op.param1}")
                    except:
                        pass
            
            elif op.type == 17:
                if db["shield"] and not is_admin(op.param1):
                    try:
                        cl.kickoutFromGroup(op.param2, [op.param1])
                        db["stats"]["protections"] += 1
                        log(f"Shield kicked {op.param1}")
                    except:
                        pass
    except Exception as e:
        log(f"Operation handler error: {e}")

# ============ MAIN LOOP ============

def main():
    log("Bot started successfully")
    
    ops_history = []
    
    while True:
        try:
            ops = cl.fetchOps(cl.getLastOpRevision(), 50)
            
            for op in ops:
                if op.revision not in ops_history:
                    ops_history.append(op.revision)
                    
                    if op.type == 26:
                        if op.message:
                            handle_msg(op.message)
                    else:
                        handle_operation(op)
                    
                    if len(ops_history) > 500:
                        ops_history = ops_history[-100:]
            
            save_db()
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  إيقاف البوت...")
            save_db()
            log("Bot stopped by user")
            print("✅ تم حفظ البيانات. وداعاً!")
            break
            
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {e}")
        print(f"\n❌ خطأ كبير: {e}")
