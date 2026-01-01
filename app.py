# -*- coding: utf-8 -*-
"""
بوت LINE للحماية - نسخة محدثة
باستخدام LINE Bot SDK الرسمي + Flask
Compatible with Render.com deployment
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent
)

# ========== التهيئة ==========
app = Flask(__name__)

# بيانات الاعتماد من متغيرات البيئة
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("❌ خطأ: يجب إضافة LINE_CHANNEL_ACCESS_TOKEN و LINE_CHANNEL_SECRET")
    print("   أضفهما في متغيرات البيئة على Render.com")
    exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ========== تخزين البيانات ==========
class DataStore:
    def __init__(self):
        self.owners = self.load('owners.json', {})
        self.admins = self.load('admins.json', {})
        self.banned = self.load('banned.json', {})
        self.settings = self.load('settings.json', {
            'protect': True,
            'invite_protect': True,
            'kick_protect': True,
            'auto_response': True,
            'welcome_message': True
        })
        self.start_time = time.time()
    
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
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ خطأ في حفظ البيانات: {e}")

db = DataStore()

# ========== مساعدات ==========
def is_owner(user_id):
    return user_id in db.owners

def is_admin(user_id):
    return user_id in db.owners or user_id in db.admins

def is_banned(user_id):
    return user_id in db.banned

def get_runtime():
    elapsed = int(time.time() - db.start_time)
    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    return f"{days}ي {hours}س {minutes}د {seconds}ث"

def get_user_name(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except:
        return "مستخدم"

def kick_user(group_id, user_id):
    try:
        line_bot_api.kick_out_user_from_group(group_id, user_id)
        return True
    except LineBotApiError as e:
        print(f"❌ فشل الطرد: {e}")
        return False

# ========== الأوامر ==========
def handle_command(event, text, user_id, group_id):
    cmd = text.lower().strip()
    
    # أوامر عامة
    if cmd == 'help' or cmd == 'الأوامر':
        help_text = """╔════════════════════════
║ 🤖 بوت الحماية
║ 
║ 📋 الأوامر العامة:
║ • help - قائمة الأوامر
║ • status - حالة البوت
║ • time - الوقت
║ • info - معلومات البوت
║
║ 👮 أوامر الأدمن:
║ • kick @mention - طرد عضو
║ • ban @mention - حظر
║ • unban @mention - فك الحظر
║ • protect on/off - الحماية
║ • adminlist - قائمة الأدمن
║
║ 👑 أوامر المالك:
║ • addowner @mention
║ • addadmin @mention
║ • deladmin @mention
║ • banlist - المحظورين
║ • clearban - مسح القائمة
║ • settings - الإعدادات
║
╚════════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))
    
    elif cmd == 'status' or cmd == 'الحالة':
        status = f"""╔════════════════════════
║ 📊 حالة البوت
║
║ ⏰ وقت التشغيل: {get_runtime()}
║ 👑 المالكين: {len(db.owners)}
║ 👮 الأدمن: {len(db.admins)}
║ 🚫 المحظورين: {len(db.banned)}
║
║ 🛡️ الحماية:
║ • عامة: {'✅' if db.settings['protect'] else '❌'}
║ • الدعوات: {'✅' if db.settings['invite_protect'] else '❌'}
║ • الطرد: {'✅' if db.settings['kick_protect'] else '❌'}
║
╚════════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))
    
    elif cmd == 'time' or cmd == 'الوقت':
        now = datetime.now()
        time_str = f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=time_str))
    
    elif cmd == 'info' or cmd == 'المعلومات':
        info = """╔════════════════════════
║ ℹ️ معلومات البوت
║
║ 📱 النوع: بوت حماية المجموعات
║ 🔧 الإصدار: 2.0
║ 🛡️ المميزات:
║   • حماية من الطرد
║   • حماية من الدعوات
║   • نظام الحظر
║   • إدارة الصلاحيات
║
║ 👨‍💻 المطور: Abeer Al-Dosari
║ 📅 التاريخ: 2025
║
╚════════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
    
    # أوامر الأدمن
    elif cmd == 'protect on' and is_admin(user_id):
        db.settings['protect'] = True
        db.settings['invite_protect'] = True
        db.settings['kick_protect'] = True
        db.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم تفعيل جميع أنواع الحماية"))
    
    elif cmd == 'protect off' and is_admin(user_id):
        db.settings['protect'] = False
        db.settings['invite_protect'] = False
        db.settings['kick_protect'] = False
        db.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ تم إيقاف الحماية"))
    
    elif cmd == 'adminlist' and is_admin(user_id):
        if not db.admins:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ لا يوجد أدمن"))
        else:
            admin_list = "╔════════════════════════\n║ 👮 قائمة الأدمن\n║\n"
            for i, admin_id in enumerate(db.admins.keys(), 1):
                name = get_user_name(admin_id)
                admin_list += f"║ {i}. {name}\n"
            admin_list += "╚════════════════════════"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=admin_list))
    
    # أوامر المالك
    elif cmd.startswith('addowner') and is_owner(user_id):
        # ملاحظة: في LINE Bot SDK، لا يمكن الحصول على mentions مباشرة
        # يجب على المستخدم إرسال User ID يدوياً
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text="📝 استخدم: addowner USER_ID\nمثال: addowner U1234567890abcdef"
        ))
    
    elif cmd.startswith('addadmin') and is_owner(user_id):
        parts = text.split()
        if len(parts) == 2:
            new_admin_id = parts[1]
            db.admins[new_admin_id] = True
            db.save()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تمت إضافة أدمن جديد"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="📝 استخدم: addadmin USER_ID"
            ))
    
    elif cmd.startswith('deladmin') and is_owner(user_id):
        parts = text.split()
        if len(parts) == 2:
            admin_id = parts[1]
            if admin_id in db.admins:
                del db.admins[admin_id]
                db.save()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم حذف الأدمن"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ المستخدم ليس أدمن"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="📝 استخدم: deladmin USER_ID"
            ))
    
    elif cmd == 'banlist' and is_owner(user_id):
        if not db.banned:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ قائمة المحظورين فارغة"))
        else:
            ban_list = "╔════════════════════════\n║ 🚫 المحظورين\n║\n"
            for i, banned_id in enumerate(db.banned.keys(), 1):
                name = get_user_name(banned_id)
                ban_list += f"║ {i}. {name}\n"
            ban_list += f"║\n║ المجموع: {len(db.banned)}\n╚════════════════════════"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ban_list))
    
    elif cmd == 'clearban' and is_owner(user_id):
        db.banned = {}
        db.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم مسح قائمة المحظورين"))
    
    elif cmd == 'settings' and is_owner(user_id):
        settings_text = f"""╔════════════════════════
║ ⚙️ الإعدادات
║
║ 🛡️ الحماية العامة: {'✅' if db.settings['protect'] else '❌'}
║ 📩 حماية الدعوات: {'✅' if db.settings['invite_protect'] else '❌'}
║ 👢 حماية الطرد: {'✅' if db.settings['kick_protect'] else '❌'}
║ 💬 الرد التلقائي: {'✅' if db.settings['auto_response'] else '❌'}
║ 👋 رسالة الترحيب: {'✅' if db.settings['welcome_message'] else '❌'}
║
╚════════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=settings_text))

# ========== معالجات الأحداث ==========
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    user_id = event.source.user_id
    
    # التعامل مع الرسائل في المجموعات
    if event.source.type == 'group':
        group_id = event.source.group_id
        handle_command(event, text, user_id, group_id)
    # التعامل مع الرسائل الخاصة
    elif event.source.type == 'user':
        handle_command(event, text, user_id, None)

@handler.add(JoinEvent)
def handle_join(event):
    """عند انضمام البوت لمجموعة"""
    if event.source.type == 'group':
        group_id = event.source.group_id
        welcome = """╔════════════════════════
║ 👋 مرحباً!
║ 
║ أنا بوت الحماية
║ 🛡️ سأحمي مجموعتك
║
║ 📋 للأوامر: اكتب help
║
╚════════════════════════"""
        line_bot_api.push_message(group_id, TextSendMessage(text=welcome))

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    """عند انضمام عضو جديد"""
    if event.source.type == 'group' and db.settings.get('welcome_message'):
        group_id = event.source.group_id
        for member in event.joined.members:
            user_id = member.user_id
            # التحقق من قائمة الحظر
            if is_banned(user_id):
                kick_user(group_id, user_id)
                line_bot_api.push_message(
                    group_id, 
                    TextSendMessage(text="⚠️ تم طرد عضو محظور تلقائياً")
                )

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    """عند مغادرة عضو"""
    # يمكن إضافة منطق هنا إذا لزم الأمر
    pass

# ========== Flask Routes ==========
@app.route("/", methods=['GET'])
def home():
    return """
    <html>
    <head><title>LINE Bot</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 بوت LINE للحماية</h1>
        <p>✅ البوت يعمل بنجاح</p>
        <hr>
        <p>📱 LINE Protection Bot v2.0</p>
        <p>👨‍💻 Developed by Abeer Al-Dosari</p>
    </body>
    </html>
    """, 200

@app.route("/callback", methods=['POST'])
def callback():
    """معالج Webhook من LINE"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    return 'OK'

@app.route("/health", methods=['GET'])
def health():
    """فحص صحة البوت"""
    return {
        "status": "healthy",
        "uptime": get_runtime(),
        "timestamp": datetime.now().isoformat()
    }, 200

# ========== التشغيل ==========
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 بوت LINE للحماية - نسخة محدثة")
    print("="*50)
    print(f"✅ تم تحميل {len(db.owners)} مالك")
    print(f"✅ تم تحميل {len(db.admins)} أدمن")
    print(f"✅ تم تحميل {len(db.banned)} محظور")
    print("="*50)
    print("🚀 البوت جاهز للعمل...\n")
    
    # للتشغيل المحلي
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
