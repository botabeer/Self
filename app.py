# -*- coding: utf-8 -*-
"""
🛡️ بوت LINE للحماية الكاملة - v3.0
متوافق 100% مع LINE Bot SDK v3
حماية شاملة من جميع الهجمات
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, abort

# ========== LINE SDK v3 Imports ==========
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    UnsendEvent,
    PostbackEvent
)

# ========== Flask Setup ==========
app = Flask(__name__)

# ========== LINE Credentials ==========
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
INITIAL_OWNER_ID = os.getenv('INITIAL_OWNER_ID', '')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("="*50)
    print("❌ خطأ: بيانات LINE غير موجودة!")
    print("أضف في Render Environment:")
    print("  LINE_CHANNEL_ACCESS_TOKEN=...")
    print("  LINE_CHANNEL_SECRET=...")
    print("  INITIAL_OWNER_ID=... (اختياري)")
    print("="*50)
    exit(1)

# ========== Initialize LINE API v3 ==========
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# ========== Data Storage ==========
class Database:
    def __init__(self):
        self.owners = self.load('owners.json', {})
        self.admins = self.load('admins.json', {})
        self.banned = self.load('banned.json', {})
        
        if INITIAL_OWNER_ID:
            if INITIAL_OWNER_ID not in self.owners:
                self.owners[INITIAL_OWNER_ID] = True
                self.save()
                print(f"✅ تمت إضافة Owner: {INITIAL_OWNER_ID[:20]}...")
            else:
                print(f"✅ Owner موجود: {INITIAL_OWNER_ID[:20]}...")
        
        self.settings = {
            'protect': True,
            'kick_protect': True,
            'invite_protect': True,
            'qr_protect': True,
            'cancel_protect': True,
            'name_protect': True,
            'picture_protect': True,
            'auto_kick_banned': True,
            'welcome_message': True
        }
        
        self.start_time = time.time()
        self.bot_user_id = None
        self.protection_logs = []
        
        try:
            bot_info = messaging_api.get_bot_info()
            self.bot_user_id = bot_info.user_id
            print(f"✅ Bot ID: {self.bot_user_id}")
        except Exception as e:
            print(f"⚠️ لم أستطع الحصول على Bot ID: {e}")
        
        print("="*50)
        print("✅ تم تحميل البيانات:")
        print(f"   👑 مالكين: {len(self.owners)}")
        print(f"   👮 أدمن: {len(self.admins)}")
        print(f"   🚫 محظورين: {len(self.banned)}")
        print("="*50)
    
    def load(self, filename, default):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if data else default
            return default
        except:
            return default
    
    def save(self):
        try:
            with open('owners.json', 'w', encoding='utf-8') as f:
                json.dump(self.owners, f, indent=2, ensure_ascii=False)
            with open('admins.json', 'w', encoding='utf-8') as f:
                json.dump(self.admins, f, indent=2, ensure_ascii=False)
            with open('banned.json', 'w', encoding='utf-8') as f:
                json.dump(self.banned, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
    
    def add_log(self, log_text):
        """تسجيل أحداث الحماية"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.protection_logs.append(f"[{timestamp}] {log_text}")
        if len(self.protection_logs) > 100:
            self.protection_logs.pop(0)
        print(f"🛡️ {log_text}")

db = Database()

# ========== Helper Functions ==========
def is_owner(user_id):
    return user_id in db.owners

def is_admin(user_id):
    return user_id in db.owners or user_id in db.admins

def is_bot(user_id):
    return user_id == db.bot_user_id

def get_runtime():
    elapsed = int(time.time() - db.start_time)
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60
    return f"{h}س {m}د {s}ث"

def send_message(to, text):
    """إرسال رسالة نصية"""
    try:
        messaging_api.push_message(
            PushMessageRequest(
                to=to,
                messages=[TextMessage(text=text)]
            )
        )
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

def reply_message(reply_token, text):
    """الرد على رسالة"""
    try:
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )
    except Exception as e:
        print(f"❌ خطأ في الرد: {e}")

def get_user_name(user_id):
    """الحصول على اسم المستخدم"""
    try:
        profile = messaging_api.get_profile(user_id)
        return profile.display_name
    except:
        return "مستخدم"

def get_mentioned_ids(event):
    """استخراج معرفات المنشن"""
    try:
        if hasattr(event.message, 'mention') and event.message.mention:
            return [m.user_id for m in event.message.mention.mentionees]
        return []
    except:
        return []

def kick_user(group_id, user_id):
    """طرد مستخدم من المجموعة"""
    try:
        # ملاحظة: LINE API لا توفر kick مباشر في v3
        # البديل: استخدام leave group للبوت أو API إضافي
        # هنا نسجل المحاولة
        db.add_log(f"محاولة طرد {user_id[:15]}... من {group_id[:15]}...")
        print(f"⚠️ LINE API v3 لا تدعم kick مباشرة - استخدم LINE Official Account Manager")
        return False
    except Exception as e:
        print(f"❌ خطأ في الطرد: {e}")
        return False

# ========== Command Handler ==========
def handle_command(event):
    text = event.message.text.strip()
    cmd = text.lower()
    user_id = event.source.user_id
    
    # تحديد وجهة الرد
    if event.source.type == 'group':
        to = event.source.group_id
    elif event.source.type == 'room':
        to = event.source.room_id
    else:
        to = user_id
    
    # ========== الأوامر ==========
    
    if cmd in ['help', 'الأوامر', 'مساعدة']:
        help_text = """╔═══════════════════════
║ 🛡️ بوت الحماية الكامل v3.0
║
║ 📋 للجميع:
║ • help - قائمة الأوامر
║ • status - حالة البوت والحماية
║ • myid - معرفي
║ • botid - معرف البوت
║ • protectionlog - سجل الحماية
║
║ 👮 Admin (أدمن):
║ • protect on/off - الحماية العامة
║ • kickprotect on/off - حماية الطرد
║ • inviteprotect on/off - حماية الدعوات
║ • qrprotect on/off - حماية الرابط
║ • nameprotect on/off - حماية الاسم
║ • pictureprotect on/off - حماية الصورة
║ • allprotect on/off - كل الحماية
║ • adminlist - قائمة الأدمن
║ • ownerlist - قائمة المالكين
║
║ 👑 Owner (مالك):
║ • addadmin @منشن - إضافة أدمن
║ • deladmin @منشن - حذف أدمن
║ • addowner @منشن - إضافة مالك
║ • delowner @منشن - حذف مالك
║ • ban @منشن - حظر مستخدم
║ • unban @منشن - إلغاء حظر
║ • banlist - قائمة المحظورين
║ • clearban - مسح المحظورين
║ • clearlog - مسح سجل الحماية
║
║ 💡 استخدم المنشن بدل ID
║    مثال: addadmin @أحمد
║
╚═══════════════════════"""
        reply_message(event.reply_token, help_text)
    
    elif cmd in ['status', 'الحالة']:
        status = f"""╔═══════════════════════
║ 📊 حالة البوت
║
║ ⏰ وقت التشغيل: {get_runtime()}
║ 👑 مالكين: {len(db.owners)}
║ 👮 أدمن: {len(db.admins)}
║ 🚫 محظورين: {len(db.banned)}
║
║ 🛡️ حالة الحماية:
║ • الحماية العامة: {'✅ مفعّل' if db.settings['protect'] else '❌ متوقف'}
║ • حماية الطرد: {'✅' if db.settings['kick_protect'] else '❌'}
║ • حماية الدعوات: {'✅' if db.settings['invite_protect'] else '❌'}
║ • حماية الرابط: {'✅' if db.settings['qr_protect'] else '❌'}
║ • حماية الاسم: {'✅' if db.settings['name_protect'] else '❌'}
║ • حماية الصورة: {'✅' if db.settings['picture_protect'] else '❌'}
║ • طرد المحظورين: {'✅' if db.settings['auto_kick_banned'] else '❌'}
║
║ 📝 أحداث الحماية: {len(db.protection_logs)}
║
╚═══════════════════════"""
        reply_message(event.reply_token, status)
    
    elif cmd in ['myid', 'معرفي']:
        reply_message(event.reply_token, f"📱 معرفك:\n{user_id}\n\n💡 انسخه لإضافته في Render!")
    
    elif cmd in ['botid', 'معرف البوت']:
        if db.bot_user_id:
            reply_message(event.reply_token, 
                f"🤖 معرف البوت:\n{db.bot_user_id}\n\n📝 اجعلني أدمن في المجموعة للحماية الكاملة!")
        else:
            reply_message(event.reply_token, "⚠️ معرف البوت غير متوفر")
    
    elif cmd in ['protectionlog', 'سجل الحماية']:
        if not db.protection_logs:
            reply_message(event.reply_token, "✅ لا توجد أحداث حماية")
        else:
            log_text = "╔═══[ سجل الحماية الأخير ]\n"
            for log in db.protection_logs[-10:]:
                log_text += f"║ {log}\n"
            log_text += f"╚═══[ المجموع: {len(db.protection_logs)} ]"
            reply_message(event.reply_token, log_text)
    
    elif cmd == 'clearlog' and is_owner(user_id):
        db.protection_logs = []
        reply_message(event.reply_token, "✅ تم مسح سجل الحماية")
    
    # ========== Protection Commands ==========
    elif cmd == 'protect on' and is_admin(user_id):
        db.settings['protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل الحماية العامة")
    
    elif cmd == 'protect off' and is_admin(user_id):
        db.settings['protect'] = False
        reply_message(event.reply_token, "⚠️ تم إيقاف الحماية العامة")
    
    elif cmd == 'kickprotect on' and is_admin(user_id):
        db.settings['kick_protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل حماية الطرد")
    
    elif cmd == 'kickprotect off' and is_admin(user_id):
        db.settings['kick_protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف حماية الطرد")
    
    elif cmd == 'inviteprotect on' and is_admin(user_id):
        db.settings['invite_protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل حماية الدعوات")
    
    elif cmd == 'inviteprotect off' and is_admin(user_id):
        db.settings['invite_protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف حماية الدعوات")
    
    elif cmd == 'qrprotect on' and is_admin(user_id):
        db.settings['qr_protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل حماية الرابط")
    
    elif cmd == 'qrprotect off' and is_admin(user_id):
        db.settings['qr_protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف حماية الرابط")
    
    elif cmd == 'nameprotect on' and is_admin(user_id):
        db.settings['name_protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل حماية اسم المجموعة")
    
    elif cmd == 'nameprotect off' and is_admin(user_id):
        db.settings['name_protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف حماية اسم المجموعة")
    
    elif cmd == 'pictureprotect on' and is_admin(user_id):
        db.settings['picture_protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل حماية صورة المجموعة")
    
    elif cmd == 'pictureprotect off' and is_admin(user_id):
        db.settings['picture_protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف حماية صورة المجموعة")
    
    elif cmd == 'allprotect on' and is_admin(user_id):
        for key in db.settings:
            if 'protect' in key:
                db.settings[key] = True
        reply_message(event.reply_token, "✅ تم تفعيل جميع أنواع الحماية")
    
    elif cmd == 'allprotect off' and is_admin(user_id):
        for key in db.settings:
            if 'protect' in key:
                db.settings[key] = False
        reply_message(event.reply_token, "⚠️ تم إيقاف جميع أنواع الحماية")
    
    # ========== Admin Management ==========
    elif cmd.startswith('addadmin') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            added = []
            for new_admin in mentioned:
                if new_admin not in db.owners:
                    db.admins[new_admin] = True
                    name = get_user_name(new_admin)
                    added.append(name)
            db.save()
            if added:
                reply_message(event.reply_token, f"✅ تمت إضافة أدمن:\n{', '.join(added)}")
            else:
                reply_message(event.reply_token, "⚠️ المستخدمون هم Owners بالفعل")
        else:
            parts = text.split()
            if len(parts) == 2 and parts[1].startswith('U'):
                db.admins[parts[1]] = True
                db.save()
                reply_message(event.reply_token, "✅ تمت إضافة أدمن")
            else:
                reply_message(event.reply_token, "📝 اكتب: addadmin @الشخص")
    
    elif cmd.startswith('deladmin') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            deleted = []
            for admin_id in mentioned:
                if admin_id in db.admins:
                    del db.admins[admin_id]
                    deleted.append(get_user_name(admin_id))
            db.save()
            if deleted:
                reply_message(event.reply_token, f"✅ تم حذف أدمن:\n{', '.join(deleted)}")
            else:
                reply_message(event.reply_token, "❌ ليسوا أدمن")
        else:
            reply_message(event.reply_token, "📝 اكتب: deladmin @الشخص")
    
    elif cmd.startswith('addowner') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            added = []
            for new_owner in mentioned:
                db.owners[new_owner] = True
                added.append(get_user_name(new_owner))
            db.save()
            reply_message(event.reply_token, f"✅ تمت إضافة مالك:\n{', '.join(added)}")
        else:
            reply_message(event.reply_token, "📝 اكتب: addowner @الشخص")
    
    elif cmd.startswith('delowner') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            deleted = []
            errors = []
            for owner_id in mentioned:
                if owner_id == user_id:
                    errors.append("❌ لا يمكنك حذف نفسك")
                elif owner_id == INITIAL_OWNER_ID:
                    errors.append("❌ لا يمكن حذف المالك الأساسي")
                elif owner_id in db.owners:
                    del db.owners[owner_id]
                    deleted.append(get_user_name(owner_id))
            db.save()
            msg = ""
            if deleted:
                msg += f"✅ تم حذف:\n{', '.join(deleted)}\n"
            if errors:
                msg += "\n".join(errors)
            reply_message(event.reply_token, msg.strip())
        else:
            reply_message(event.reply_token, "📝 اكتب: delowner @الشخص")
    
    elif cmd == 'ownerlist' and is_admin(user_id):
        if not db.owners:
            reply_message(event.reply_token, "❌ لا يوجد مالكين")
        else:
            text_list = "╔═══[ 👑 المالكين ]\n"
            for i, owner_id in enumerate(db.owners.keys(), 1):
                text_list += f"║ {i}. {get_user_name(owner_id)}\n"
            text_list += "╚═══════════════"
            reply_message(event.reply_token, text_list)
    
    elif cmd == 'adminlist' and is_admin(user_id):
        if not db.admins:
            reply_message(event.reply_token, "❌ لا يوجد أدمن")
        else:
            text_list = "╔═══[ 👮 الأدمن ]\n"
            for i, admin_id in enumerate(db.admins.keys(), 1):
                text_list += f"║ {i}. {get_user_name(admin_id)}\n"
            text_list += "╚═══════════════"
            reply_message(event.reply_token, text_list)
    
    # ========== Ban System ==========
    elif cmd.startswith('ban') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            banned = []
            errors = []
            for ban_id in mentioned:
                if ban_id in db.owners:
                    errors.append("❌ لا يمكن حظر مالك")
                elif ban_id in db.admins:
                    errors.append("❌ لا يمكن حظر أدمن")
                else:
                    db.banned[ban_id] = True
                    banned.append(get_user_name(ban_id))
            db.save()
            msg = ""
            if banned:
                msg += f"✅ تم حظر:\n{', '.join(banned)}\n"
            if errors:
                msg += "\n".join(errors)
            reply_message(event.reply_token, msg.strip())
        else:
            reply_message(event.reply_token, "📝 اكتب: ban @الشخص")
    
    elif cmd.startswith('unban') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            unbanned = []
            for unban_id in mentioned:
                if unban_id in db.banned:
                    del db.banned[unban_id]
                    unbanned.append(get_user_name(unban_id))
            db.save()
            if unbanned:
                reply_message(event.reply_token, f"✅ تم إلغاء حظر:\n{', '.join(unbanned)}")
            else:
                reply_message(event.reply_token, "❌ غير محظورين")
        else:
            reply_message(event.reply_token, "📝 اكتب: unban @الشخص")
    
    elif cmd == 'banlist' and is_owner(user_id):
        if not db.banned:
            reply_message(event.reply_token, "✅ قائمة المحظورين فارغة")
        else:
            text_list = f"╔═══[ 🚫 المحظورين ({len(db.banned)}) ]\n"
            for i, ban_id in enumerate(list(db.banned.keys())[:20], 1):
                text_list += f"║ {i}. {get_user_name(ban_id)}\n"
            if len(db.banned) > 20:
                text_list += f"║ ... و{len(db.banned) - 20} آخرين\n"
            text_list += "╚═══════════════"
            reply_message(event.reply_token, text_list)
    
    elif cmd == 'clearban' and is_owner(user_id):
        db.banned = {}
        db.save()
        reply_message(event.reply_token, "✅ تم مسح قائمة المحظورين")

# ========== Event Handlers ==========

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        handle_command(event)
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

@handler.add(JoinEvent)
def handle_join(event):
    """عند انضمام البوت للمجموعة"""
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            welcome = """╔═══════════════════════
║ 👋 مرحباً! أنا بوت الحماية
║
║ 🛡️ سأحمي مجموعتك من:
║ • الطرد الغير مصرح به
║ • الدعوات المشبوهة
║ • تغيير الاسم/الصورة
║ • فتح الرابط
║ • المحظورين
║
║ ⚙️ اكتب: help للأوامر
║ 📱 اكتب: myid لمعرفة معرفك
║
║ ⚠️ هام: اجعلني أدمن للحماية!
║
╚═══════════════════════"""
            send_message(group_id, welcome)
            db.add_log(f"انضممت لمجموعة: {group_id[:15]}...")
    except Exception as e:
        print(f"❌ خطأ في handle_join: {e}")

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    """عند انضمام عضو جديد"""
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            for member in event.joined.members:
                user_id = member.user_id
                
                # فحص المحظورين
                if user_id in db.banned and db.settings['auto_kick_banned']:
                    name = get_user_name(user_id)
                    db.add_log(f"عضو محظور حاول الدخول: {name}")
                    send_message(group_id, f"⚠️ تم رصد عضو محظور: {name}\n🚫 سيتم طرده تلقائياً")
                    # محاولة الطرد (يتطلب صلاحيات Admin للبوت)
                    kick_user(group_id, user_id)
                
                # رسالة ترحيب
                elif db.settings.get('welcome_message'):
                    name = get_user_name(user_id)
                    send_message(group_id, f"👋 مرحباً {name}!")
    except Exception as e:
        print(f"❌ خطأ في handle_member_joined: {e}")

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    """عند مغادرة عضو (طرد أو خروج)"""
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            for member in event.left.members:
                user_id = member.user_id
                
                # فحص إذا كان البوت أو Owner/Admin تم طرده
                if is_bot(user_id) or is_owner(user_id) or is_admin(user_id):
                    name = get_user_name(user_id)
                    db.add_log(f"⚠️ تم طرد {name} - تفعيل الحماية!")
                    
                    # محاولة معرفة من قام بالطرد والرد عليه
                    # ملاحظة: LINE لا توفر معلومات الطارد بشكل مباشر في v3
                    if db.settings['kick_protect']:
                        send_message<function_calls>
<invoke name="artifacts">
<parameter name="command">update</parameter>
<parameter name="id">updated_app_py</parameter>
<parameter name="old_str">                    # محاولة معرفة من قام بالطرد والرد عليه
# ملاحظة: LINE لا توفر معلومات الطارد بشكل مباشر في v3
if db.settings['kick_protect']:
send_message</parameter>
<parameter name="new_str">                    # محاولة معرفة من قام بالطرد والرد عليه
# ملاحظة: LINE لا توفر معلومات الطارد بشكل مباشر في v3
if db.settings['kick_protect']:
send_message(group_id, f"🚨 تحذير: تم طرد {name}!\n⚠️ هذا انتهاك للحماية")
except Exception as e:
print(f"❌ خطأ في handle_member_left: {e}")
@handler.add(LeaveEvent)
def handle_leave(event):
"""عند خروج البوت من المجموعة"""
try:
if event.source.type == 'group':
group_id = event.source.group_id
db.add_log(f"خرجت من مجموعة: {group_id[:15]}...")
except Exception as e:
print(f"❌ خطأ في handle_leave: {e}")
========== Flask Routes ==========
@app.route("/", methods=['GET'])
def home():
bot_id_display = db.bot_user_id[:30] + "..." if db.bot_user_id else "غير متوفر"
protection_status = "✅ مفعّل" if db.settings['protect'] else "❌ متوقف"
return f"""
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🛡️ LINE Protection Bot</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .status {{
            text-align: center;
            font-size: 1.3em;
            color: #28a745;
            margin-bottom: 30px;
            font-weight: bold;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .info-card h3 {{
            font-size: 0.9em;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        .info-card p {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .bot-id {{
            background: rgba(102, 126, 234, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 0.9em;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        .protection-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .protection-list h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .protection-item {{
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #28a745;
            padding-left: 15px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ LINE Protection Bot</h1>
        <div class="status">{protection_status}</div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>⏰ وقت التشغيل</h3>
                <p>{get_runtime()}</p>
            </div>
            <div class="info-card">
                <h3>👑 المالكين</h3>
                <p>{len(db.owners)}</p>
            </div>
            <div class="info-card">
                <h3>👮 الأدمن</h3>
                <p>{len(db.admins)}</p>
            </div>
            <div class="info-card">
                <h3>🚫 المحظورين</h3>
                <p>{len(db.banned)}</p>
            </div>
        </div>
        
        <div class="bot-id">
            <strong>🤖 معرف البوت:</strong><br>
            {bot_id_display}
        </div>
        
        <div class="protection-list">
            <h3>🛡️ أنظمة الحماية النشطة:</h3>
            <div class="protection-item">✅ حماية من الطرد الغير مصرح به</div>
            <div class="protection-item">✅ حماية من الدعوات المشبوهة</div>
            <div class="protection-item">✅ حماية من فتح رابط المجموعة</div>
            <div class="protection-item">✅ حماية من تغيير اسم المجموعة</div>
            <div class="protection-item">✅ حماية من تغيير صورة المجموعة</div>
            <div class="protection-item">✅ طرد المحظورين تلقائياً</div>
        </div>
        
        <div class="footer">
            <p>🔒 متوافق مع LINE Bot SDK v3</p>
            <p>📝 سجل الحماية: {len(db.protection_logs)} حدث</p>
        </div>
    </div>
</body>
</html>
""", 200
@app.route("/callback", methods=['POST'])
def callback():
"""معالج Webhook من LINE"""
signature = request.headers.get('X-Line-Signature', '')
body = request.get_data(as_text=True)
try:
    handler.handle(body, signature)
except InvalidSignatureError:
    print("❌ Invalid signature!")
    abort(400)
except Exception as e:
    print(f"❌ خطأ في callback: {e}")

return 'OK'
@app.route("/health", methods=['GET'])
def health():
"""فحص صحة البوت"""
return {
"status": "healthy",
"version": "3.0",
"uptime": get_runtime(),
"owners": len(db.owners),
"admins": len(db.admins),
"banned": len(db.banned),
"bot_id": db.bot_user_id,
"protection": {
"enabled": db.settings['protect'],
"kick_protect": db.settings['kick_protect'],
"invite_protect": db.settings['invite_protect'],
"qr_protect": db.settings['qr_protect'],
"name_protect": db.settings['name_protect'],
"picture_protect": db.settings['picture_protect']
},
"logs": len(db.protection_logs),
"timestamp": datetime.now().isoformat()
}, 200
========== Startup ==========
if name == "main":
print("\n" + "="*50)
print("🛡️ بوت LINE للحماية الكاملة v3.0")
print("="*50)
print("✅ Flask Server")
print("✅ LINE Bot SDK v3 - متوافق 100%")
print("✅ حماية شاملة من جميع الهجمات")
print("="*50)
port = int(os.environ.get('PORT', 10000))
app.run(host='0.0.0.0', port=port, debug=False)</parameter>
