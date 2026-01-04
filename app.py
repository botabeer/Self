import json
import time
import os
import re
from datetime import datetime
from collections import defaultdict
import requests

# ============ الإعدادات ============

DB_FILE = "db.json"
TOKEN_FILE = "token.txt"
LOG_FILE = "logs.txt"

# حد التحذيرات قبل الطرد التلقائي
AUTO_WARN_LIMIT = 3

# إعدادات كشف السبام (5 رسائل في 2 ثانية)
SPAM_TIME = 2
SPAM_COUNT = 5

# إعدادات الطرد الجماعي (لتجنب الحظر من LINE)
MASSKICK_BATCH = 3
MASSKICK_DELAY = 2

# الروابط الممنوعة
LINK_REGEX = re.compile(
    r"(line\.me|chat\.line|t\.me|telegram\.me|wa\.me|whatsapp\.com|discord\.gg|discord\.com)",
    re.IGNORECASE
)

# LINE API URLs
LINE_API = "https://gd2.line.naver.jp"

# ============ قاعدة البيانات الافتراضية ============

DEFAULT_DB = {
    "owners": [],           # أصحاب البوت (صلاحيات كاملة)
    "admins": [],           # المشرفين
    "vip": [],              # VIP (معفيين من القيود)
    "banned": [],           # المحظورين
    "warnings": {},         # التحذيرات {user_id: count}
    "muted": {},            # المكتومين {user_id: timestamp}
    "locked_groups": {},    # المجموعات المقفلة {group_id: True}
    "watch": {},            # المراقبة {user_id: count}
    "whitelist_bots": [],   # البوتات المسموحة
    
    # أوضاع الحماية
    "ghost": False,         # وضع شبحي (لا يرد)
    "shield": False,        # درع (يطرد أي داخل جديد)
    "freeze": False,        # تجميد (يطرد أي شخص يكتب)
    
    # الحمايات المفعلة
    "protect": {
        "kick": True,       # السماح بالطرد
        "link": True,       # حماية من الروابط
        "spam": True,       # حماية من السبام
        "bots": True,       # حماية من البوتات
        "invite": True,     # حماية من الدعوات
        "qr": True,         # حماية من QR
        "cancel": True      # حماية من الإلغاء
    },
    
    # الإحصائيات
    "stats": {
        "messages": 0,
        "kicks": 0,
        "bans": 0,
        "protections": 0,
        "warnings": 0
    },
    
    "enabled": True,
    "auto_join": True
}

# ============ وظائف قاعدة البيانات ============

def load_db():
    """تحميل قاعدة البيانات من الملف"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, indent=2, ensure_ascii=False)
        print("✅ تم إنشاء قاعدة بيانات جديدة")
        return DEFAULT_DB.copy()
    
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            db = json.load(f)
        
        # إضافة أي مفاتيح جديدة من DEFAULT_DB
        for k in DEFAULT_DB:
            if k not in db:
                db[k] = DEFAULT_DB[k]
        
        print("✅ تم تحميل قاعدة البيانات")
        return db
    except Exception as e:
        print(f"❌ خطأ في تحميل DB: {e}")
        return DEFAULT_DB.copy()

def save_db():
    """حفظ قاعدة البيانات"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Error saving DB: {e}")

def log(txt):
    """تسجيل الأحداث"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {txt}\n")
        print(f"[LOG] {txt}")
    except:
        pass

# تحميل قاعدة البيانات
db = load_db()

# ============ LINE API Class ============

class LineClient:
    """كلاس للتعامل مع LINE API"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            "X-Line-Access": token,
            "User-Agent": "Line/13.0.1",
            "X-Line-Application": "ANDROID\t13.0.1\tAndroid OS\t12.0.0"
        }
        
        # الحصول على معلومات البوت
        profile = self.get_profile()
        if not profile:
            raise Exception("فشل في الحصول على البروفايل - تأكد من التوكن")
        
        self.my_mid = profile.get("mid")
        self.display_name = profile.get("displayName", "Bot")
        
    def _post(self, method, params=None):
        """إرسال طلب إلى LINE API"""
        try:
            payload = {
                "method": method,
                "params": params or {}
            }
            
            response = requests.post(
                f"{LINE_API}/api/v4/TalkService.do",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                log(f"API Error {response.status_code}: {method}")
                return {}
                
        except requests.exceptions.Timeout:
            log(f"Timeout: {method}")
            return {}
        except Exception as e:
            log(f"Error in {method}: {str(e)}")
            return {}
    
    def get_profile(self):
        """الحصول على بروفايل البوت"""
        result = self._post("getProfile")
        return result.get("result", {})
    
    def send_message(self, to, text):
        """إرسال رسالة"""
        return self._post("sendMessage", {
            "to": to,
            "text": str(text)
        })
    
    def kick_user(self, group_id, user_ids):
        """طرد مستخدم أو عدة مستخدمين"""
        if isinstance(user_ids, str):
            user_ids = [user_ids]
        
        return self._post("kickoutFromGroup", {
            "reqSeq": 0,
            "groupId": group_id,
            "contactIds": user_ids
        })
    
    def get_group(self, group_id):
        """الحصول على معلومات المجموعة"""
        result = self._post("getGroup", {
            "groupId": group_id
        })
        return result.get("result", {})
    
    def accept_group_invitation(self, group_id):
        """قبول دعوة مجموعة"""
        return self._post("acceptGroupInvitation", {
            "reqSeq": 0,
            "groupId": group_id
        })
    
    def get_recent_messages(self, group_id, count=50):
        """الحصول على آخر الرسائل"""
        result = self._post("getRecentMessagesV2", {
            "messageBoxId": group_id,
            "count": count
        })
        return result.get("result", [])
    
    def delete_self_messages(self, group_id):
        """حذف جميع رسائل البوت في المجموعة"""
        try:
            messages = self.get_recent_messages(group_id, 100)
            deleted = 0
            
            for msg in messages:
                if msg.get("_from") == self.my_mid:
                    msg_id = msg.get("id")
                    if msg_id:
                        self._post("removeMessage", {
                            "messageId": msg_id
                        })
                        deleted += 1
                        time.sleep(0.5)
            
            return deleted
        except Exception as e:
            log(f"Error deleting messages: {e}")
            return 0

# ============ تسجيل الدخول ============

def login():
    """تسجيل الدخول إلى LINE"""
    
    # محاولة استخدام توكن محفوظ
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
            
            print("🔄 جاري تسجيل الدخول...")
            client = LineClient(token)
            print(f"✅ تم تسجيل الدخول بنجاح كـ: {client.display_name}")
            return client
            
        except Exception as e:
            print(f"❌ فشل التوكن المحفوظ: {e}")
            os.remove(TOKEN_FILE)
    
    # طلب توكن جديد
    print("\n" + "="*50)
    print("📱 للحصول على التوكن:")
    print("="*50)
    print("1. افتح LINE على الكمبيوتر (Windows/Mac)")
    print("2. اضغط F12 لفتح Developer Tools")
    print("3. اذهب إلى تبويب Network")
    print("4. أرسل أي رسالة في LINE")
    print("5. ابحث عن طلب يحتوي على 'TalkService'")
    print("6. في Headers، ابحث عن 'X-Line-Access'")
    print("7. انسخ القيمة (سيكون طويل جداً)")
    print("="*50 + "\n")
    
    token = input("📝 الصق التوكن هنا: ").strip()
    
    if not token:
        print("❌ لم تدخل توكن!")
        exit(1)
    
    try:
        client = LineClient(token)
        
        # حفظ التوكن
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        
        print(f"✅ تم حفظ التوكن بنجاح!")
        return client
        
    except Exception as e:
        print(f"❌ خطأ في التوكن: {e}")
        exit(1)

# تسجيل الدخول
print("\n🤖 بوت حماية LINE")
print("="*50)
cl = login()
my_mid = cl.my_mid

# إضافة المستخدم كمالك إذا لم يكن موجود
if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()
    print(f"✅ تمت إضافتك كمالك: {my_mid}")

print(f"\n📊 معلومات البوت:")
print(f"   • الاسم: {cl.display_name}")
print(f"   • ID: {my_mid}")
print(f"   • المالكين: {len(db['owners'])}")
print(f"   • الأدمنز: {len(db['admins'])}")
print("="*50)
print("✅ البوت يعمل الآن...\n")

# ============ وظائف مساعدة ============

def is_owner(user_id):
    """التحقق من المالك"""
    return user_id in db["owners"]

def is_admin(user_id):
    """التحقق من المشرف"""
    return user_id in db["admins"] or is_owner(user_id)

def is_vip(user_id):
    """التحقق من VIP"""
    return user_id in db["vip"]

def is_banned(user_id):
    """التحقق من الحظر"""
    return user_id in db["banned"]

def is_muted(user_id):
    """التحقق من الكتم"""
    if user_id not in db["muted"]:
        return False
    
    # إذا انتهى وقت الكتم
    if time.time() > db["muted"][user_id]:
        del db["muted"][user_id]
        save_db()
        return False
    
    return True

def send(group_id, text):
    """إرسال رسالة (إلا إذا كان الوضع الشبحي مفعل)"""
    if not db["ghost"]:
        try:
            cl.send_message(group_id, text)
        except Exception as e:
            log(f"Failed to send message: {e}")

def get_mentions(text):
    """استخراج المنشنز من الرسالة"""
    mentions = []
    try:
        # البحث عن @mention patterns
        parts = text.split("@")
        for part in parts[1:]:
            # MID في LINE يكون 33 حرف
            words = part.split()
            if words and len(words[0]) == 33:
                mentions.append(words[0])
    except:
        pass
    return mentions

def add_warn(user_id):
    """إضافة تحذير"""
    db["warnings"][user_id] = db["warnings"].get(user_id, 0) + 1
    db["stats"]["warnings"] += 1
    save_db()
    return db["warnings"][user_id]

def safe_kick(group_id, user_id, silent=False):
    """طرد آمن مع تسجيل"""
    try:
        # عدم طرد البوت نفسه أو المالكين
        if user_id == my_mid or is_owner(user_id):
            return False
        
        cl.kick_user(group_id, user_id)
        db["stats"]["kicks"] += 1
        save_db()
        
        log(f"KICK: {user_id[:8]}... from {group_id[:8]}...")
        
        if not silent and not db["ghost"]:
            send(group_id, "✅ تم طرد العضو المخالف")
        
        return True
        
    except Exception as e:
        log(f"Failed to kick {user_id}: {e}")
        return False

# ============ نظام كشف السبام ============

user_messages = defaultdict(list)

def is_spam(user_id):
    """كشف السبام"""
    # VIP والأدمنز معفيين
    if is_vip(user_id) or is_admin(user_id):
        return False
    
    now = time.time()
    
    # حذف الرسائل القديمة
    user_messages[user_id] = [
        t for t in user_messages[user_id] 
        if now - t < SPAM_TIME
    ]
    
    # إضافة الرسالة الحالية
    user_messages[user_id].append(now)
    
    # إذا تجاوز العدد المسموح
    return len(user_messages[user_id]) > SPAM_COUNT

# ============ الطرد الجماعي الآمن ============

def masskick(group_id, members):
    """طرد جماعي آمن"""
    kicked = 0
    batch = []
    
    for user_id in members:
        # تجاهل البوت والمالكين والأدمنز
        if user_id == my_mid or is_owner(user_id) or is_admin(user_id):
            continue
        
        batch.append(user_id)
        
        # عند الوصول لحجم الدفعة
        if len(batch) >= MASSKICK_BATCH:
            try:
                cl.kick_user(group_id, batch)
                kicked += len(batch)
                log(f"Masskick batch: {len(batch)} users")
            except Exception as e:
                log(f"Masskick error: {e}")
            
            batch = []
            time.sleep(MASSKICK_DELAY)
    
    # طرد الباقي
    if batch:
        try:
            cl.kick_user(group_id, batch)
            kicked += len(batch)
        except Exception as e:
            log(f"Masskick error: {e}")
    
    return kicked

# ============ معالج الرسائل ============

def handle_message(msg):
    """معالجة الرسالة"""
    
    # التحقق من وجود نص
    if not msg.get("text"):
        return
    
    sender = msg.get("_from")  # المرسل
    group = msg.get("to")       # المجموعة
    text = msg.get("text", "").strip()
    cmd = text.lower().split()[0] if text else ""
    
    # تحديث الإحصائيات
    db["stats"]["messages"] += 1
    
    # ===== الحمايات التلقائية =====
    
    # 1. المحظورين
    if is_banned(sender):
        safe_kick(group, sender, True)
        db["stats"]["protections"] += 1
        save_db()
        return
    
    # 2. وضع التجميد
    if db["freeze"] and not is_admin(sender):
        safe_kick(group, sender, True)
        db["stats"]["protections"] += 1
        save_db()
        return
    
    # 3. وضع الدرع
    if db["shield"] and not is_admin(sender):
        safe_kick(group, sender, True)
        db["stats"]["protections"] += 1
        save_db()
        return
    
    # 4. القفل
    if db["locked_groups"].get(group) and not is_admin(sender):
        return
    
    # 5. الكتم
    if is_muted(sender):
        return
    
    # 6. حماية من الروابط
    if db["protect"]["link"] and LINK_REGEX.search(text) and not is_admin(sender):
        warns = add_warn(sender)
        db["stats"]["protections"] += 1
        
        if warns >= AUTO_WARN_LIMIT:
            db["banned"].append(sender)
            db["stats"]["bans"] += 1
            save_db()
            safe_kick(group, sender, True)
        else:
            send(group, f"⚠️ ممنوع إرسال الروابط!\n🔴 التحذير: {warns}/{AUTO_WARN_LIMIT}")
        return
    
    # 7. حماية من السبام
    if db["protect"]["spam"] and is_spam(sender):
        warns = add_warn(sender)
        db["stats"]["protections"] += 1
        
        if warns >= AUTO_WARN_LIMIT:
            db["banned"].append(sender)
            db["stats"]["bans"] += 1
            save_db()
            safe_kick(group, sender, True)
            send(group, "⛔ تم طرد المزعج")
        return
    
    # 8. نظام المراقبة
    if sender in db["watch"] and not is_admin(sender):
        db["watch"][sender] += 1
        
        if db["watch"][sender] >= 2:
            db["banned"].append(sender)
            db["stats"]["bans"] += 1
            save_db()
            safe_kick(group, sender, True)
            send(group, "🚨 تم طرد العضو المراقب")
        
        save_db()
        return
    
    # استخراج المنشنز
    mentions = get_mentions(text)
    
    # ===== الأوامر =====
    
    # ----- أوامر عامة -----
    
    if cmd == "help":
        help_text = """╔═══════════════════╗
║   📚 قائمة الأوامر   ║
╚═══════════════════╝

🔹 عامة:
  • help - عرض هذه القائمة
  • me - معلوماتك
  • time - الوقت الحالي
  • ping - فحص البوت
  • stats - إحصائيات البوت

👮 أدمن فقط:
  • kick - طرد عضو
  • warn - تحذير عضو
  • clearwarn - حذف تحذيرات
  • mute - كتم عضو (10 دقائق)
  • unmute - فك كتم
  • lock - قفل الشات
  • unlock - فتح الشات
  • addvip - إضافة VIP
  • watch - مراقبة عضو

👑 مالك فقط:
  • addadmin - إضافة أدمن
  • removeadmin - حذف أدمن
  • ban - حظر عضو
  • unban - فك حظر
  • masskick - طرد الجميع
  • clear - مسح رسائل البوت
  • panic - وضع طوارئ
  • ghost - وضع شبحي
  • shield - تفعيل الدرع
  • freeze - تجميد المجموعة

✨ استخدم @ لمنشن الأعضاء"""
        send(group, help_text)
    
    elif cmd == "me":
        role = "👑 مالك" if is_owner(sender) else "👮 أدمن" if is_admin(sender) else "⭐ VIP" if is_vip(sender) else "👤 عضو"
        warns = db["warnings"].get(sender, 0)
        is_muted_status = "🔇 نعم" if is_muted(sender) else "🔊 لا"
        
        info = f"""╔═══════════════════╗
║   معلوماتك   ║
╚═══════════════════╝

الرتبة: {role}
التحذيرات: {warns}/{AUTO_WARN_LIMIT}
مكتوم: {is_muted_status}
ID: {sender[:10]}..."""
        send(group, info)
    
    elif cmd == "time":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send(group, f"🕐 الوقت الحالي:\n{now}")
    
    elif cmd == "ping":
        send(group, "✅ Pong! البوت يعمل بشكل طبيعي")
    
    elif cmd == "stats":
        stats = f"""╔═══════════════════╗
║   📊 الإحصائيات   ║
╚═══════════════════╝

💬 الرسائل: {db['stats']['messages']:,}
👢 الطردات: {db['stats']['kicks']:,}
🚫 الحظر: {db['stats']['bans']:,}
🛡️ الحمايات: {db['stats']['protections']:,}
⚠️ التحذيرات: {db['stats']['warnings']:,}

👥 المستخدمين:
  • مالكين: {len(db['owners'])}
  • أدمنز: {len(db['admins'])}
  • VIP: {len(db['vip'])}
  • محظورين: {len(db['banned'])}"""
        send(group, stats)
    
    # ----- أوامر الأدمن -----
    
    elif cmd == "kick" and is_admin(sender):
        if not mentions:
            send(group, "❌ استخدم: kick @mention")
            return
        
        kicked = 0
        for user in mentions:
            if safe_kick(group, user):
                kicked += 1
        
        if kicked > 0:
            send(group, f"✅ تم طرد {kicked} عضو")
    
    elif cmd == "warn" and is_admin(sender):
        if not mentions:
            send(group, "❌ استخدم: warn @mention")
            return
        
        for user in mentions:
            if is_admin(user):
                continue
            warns = add_warn(user)
            send(group, f"⚠️ تحذير: {warns}/{AUTO_WARN_LIMIT}")
    
    elif cmd == "clearwarn" and is_admin(sender):
        if mentions:
            for user in mentions:
                db["warnings"].pop(user, None)
            save_db()
            send(group, "✅ تم حذف التحذيرات")
        else:
            send(group, "❌ استخدم: clearwarn @mention")
    
    elif cmd == "mute" and is_admin(sender):
        if mentions:
            for user in mentions:
                if not is_admin(user):
                    db["muted"][user] = time.time() + 600  # 10 دقائق
            save_db()
            send(group, "🔇 تم الكتم لمدة 10 دقائق")
        else:
            send(group, "❌ استخدم: mute @mention")
    
    elif cmd == "unmute" and is_admin(sender):
        if mentions:
            for user in mentions:
                db["muted"].pop(user, None)
            save_db()
            send(group, "🔊 تم فك الكتم")
        else:
            send(group, "❌ استخدم: unmute @mention")
    
    elif cmd == "lock" and is_admin(sender):
        db["locked_groups"][group] = True
        save_db()
        send(group, "🔒 تم قفل الشات - الأدمنز فقط يمكنهم الكتابة")
    
    elif cmd == "unlock" and is_admin(sender):
        db["locked_groups"][group] = False
        save_db()
        send(group, "🔓 تم فتح الشات")
    
    elif cmd == "addvip" and is_admin(sender):
        if mentions:
            for user in mentions:
                if user not in db["vip"]:
                    db["vip"].append(user)
            save_db()
            send(group, "⭐ تمت إضافة VIP")
        else:
            send(group, "❌ استخدم: addvip @mention")
    
    elif cmd == "watch" and is_admin(sender):
        if mentions:
            for user in mentions:
                if not is_admin(user):
                    db["watch"][user] = 0
            save_db()
            send(group, "👁️ تمت إضافة العضو للمراقبة")
        else:
            send(group, "❌ استخدم: watch @mention")
    
    # ----- أوامر المالك -----
    
    elif cmd == "addadmin" and is_owner(sender):
        if mentions:
            for user in mentions:
                if user not in db["admins"]:
                    db["admins"].append(user)
            save_db()
            send(group, "👮 تمت إضافة المشرف")
        else:
            send(group, "❌ استخدم: addadmin @mention")
    
    elif cmd == "removeadmin" and is_owner(sender):
        if mentions:
            for user in mentions:
                if user in db["admins"]:
                    db["admins"].remove(user)
            save_db()
            send(group, "✅ تم حذف المشرف")
        else:
            send(group, "❌ استخدم: removeadmin @mention")
    
    elif cmd == "ban" and is_owner(sender):
        if mentions:
            for user in mentions:
                if user not in db["banned"] and not is_owner(user):
                    db["banned"].append(user)
                    db["stats"]["bans"] += 1
                    safe_kick(group, user, True)
            save_db()
            send(group, "🚫 تم حظر العضو نهائياً")
        else:
            send(group, "❌ استخدم: ban @mention")
    
    elif cmd == "unban" and is_owner(sender):
        if mentions:
            for user in mentions:
                if user in db["banned"]:
                    db["banned"].remove(user)
            save_db()
            send(group, "✅ تم فك الحظر")
        else:
            send(group, "❌ استخدم: unban @mention")
    
    elif cmd == "masskick" and is_owner(sender):
        try:
            send(group, "⚠️ جاري طرد جميع الأعضاء...")
            group_info = cl.get_group(group)
            members = [mem["mid"] for mem in group_info.get("members", [])]
            
            kicked = masskick(group, members)
            send(group, f"✅ تم طرد {kicked} عضو")
            
        except Exception as e:
            log(f"Masskick error: {e}")
            send(group, "❌ حدث خطأ أثناء الطرد الجماعي")
    
    elif cmd == "clear" and is_owner(sender):
        send(group, "🗑️ جاري مسح رسائل البوت...")
        deleted = cl.delete_self_messages(group)
        if deleted > 0:
            send(group, f"✅ تم حذف {deleted} رسالة")
        else:
            send(group, "ℹ️ لا توجد رسائل للحذف")
    
    elif cmd == "panic" and is_owner(sender):
        db["shield"] = True
        db["freeze"] = True
        db["protect"]["link"] = True
        db["protect"]["spam"] = True
        save_db()
        send(group, "🚨 وضع الطوارئ مفعل!\n🛡️ جميع الحمايات نشطة")
    
    elif cmd == "ghost" and is_owner(sender):
        db["ghost"] = not db["ghost"]
        save_db()
        if not db["ghost"]:
            send(group, "👻 تم إلغاء الوضع الشبحي")
    
    elif cmd == "shield" and is_owner(sender):
        db["shield"] = not db["shield"]
        save_db()
        status = "مفعل 🛡️" if db["shield"] else "معطل ❌"
        send(group, f"الدرع: {status}")
    
    elif cmd == "freeze" and is_owner(sender):
        db["freeze"] = not db["freeze"]
        save_db()
        status = "مفعل 🧊" if db["freeze"] else "معطل ❌"
        send(group, f"التجميد: {status}")
    
    elif cmd == "status" and is_owner(sender):
        status_msg = f"""╔═══════════════════╗
║   ⚙️ حالة البوت   ║
╚═══════════════════╝

الوضع الشبحي: {"🟢 مفعل" if db["ghost"] else "🔴 معطل"}
الدرع: {"🟢 مفعل" if db["shield"] else "🔴 معطل"}
التجميد: {"🟢 مفعل" if db["freeze"] else "🔴 معطل"}

الحمايات:
  • الروابط: {"🟢" if db["protect"]["link"] else "🔴"}
  • السبام: {"🟢" if db["protect"]["spam"] else "🔴"}
  • البوتات: {"🟢" if db["protect"]["bots"] else "🔴"}"""
        send(group, status_msg)

# ============ الحلقة الرئيسية ============

def main():
    """الحلقة الرئيسية للبوت"""
    
    print("🔄 بدء مراقبة الرسائل...\n")
    
    last_check = time.time()
    processed_ids = set()
    
    while True:
        try:
            # فحص كل ثانية
            if time.time() - last_check > 1:
                
                # الحصول على آخر 30 رسالة
                messages = cl.get_recent_messages(cl.my_mid, 30)
                
                for msg in messages:
                    msg_id = msg.get("id")
                    msg_type = msg.get("contentType")
                    
                    # تجاهل الرسائل المعالجة
                    if msg_id in processed_ids:
                        continue
                    
                    # إضافة للمعالجة
                    processed_ids.add(msg_id)
                    
                    # معالجة رسائل نصية فقط
                    if msg_type == 0:  # نص
                        handle_message(msg)
                    
                    # تنظيف الذاكرة
                    if len(processed_ids) > 1000:
                        processed_ids.clear()
                
                last_check = time.time()
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⚠️ إيقاف البوت...")
            save_db()
            print("✅ تم حفظ قاعدة البيانات")
            print("👋 وداعاً!")
            break
            
        except Exception as e:
            log(f"Main loop error: {e}")
            print(f"❌ خطأ: {e}")
            time.sleep(3)

# ============ نقطة البداية ============

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {e}")
        print(f"❌ خطأ فادح: {e}")
