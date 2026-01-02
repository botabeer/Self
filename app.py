#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ LINE Protection Bot - Official API
✅ يشتغل 100% على Render المجاني
✅ مع نظام إضافة Owner تلقائي
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    JoinEvent,
    MemberJoinedEvent,
    MemberLeftEvent
)

app = Flask(__name__)

# ========== إعدادات LINE Bot ==========
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

# 🔑 كود التفعيل السري - غيره بعد ما تضيف نفسك!
ACTIVATION_CODE = os.getenv('ACTIVATION_CODE', 'OWNER2026')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("❌ خطأ: أضف LINE_CHANNEL_ACCESS_TOKEN و LINE_CHANNEL_SECRET")
    exit(1)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ========== قاعدة البيانات ==========
class BotDatabase:
    def __init__(self):
        self.data_file = 'bot_data.json'
        self.data = self.load_data()
        self.start_time = time.time()
    
    def load_data(self):
        """تحميل البيانات من ملف JSON"""
        default_data = {
            'owners': {},
            'admins': {},
            'banned': {},
            'settings': {
                'protect': True,
                'welcome': True,
                'auto_kick': True,
                'language': 'ar'
            }
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    for key in default_data:
                        if key not in loaded:
                            loaded[key] = default_data[key]
                    return loaded
            except Exception as e:
                print(f"⚠️ خطأ تحميل: {e}")
                return default_data
        return default_data
    
    def save_data(self):
        """حفظ البيانات"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ حفظ: {e}")
            return False
    
    def is_owner(self, user_id):
        return user_id in self.data['owners']
    
    def is_admin(self, user_id):
        return self.is_owner(user_id) or user_id in self.data['admins']
    
    def is_banned(self, user_id):
        return user_id in self.data['banned']
    
    def add_owner(self, user_id, name="Unknown"):
        self.data['owners'][user_id] = {
            'name': name,
            'added': time.time(),
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
        print(f"✅ Owner added: {user_id} ({name})")
    
    def remove_owner(self, user_id):
        if user_id in self.data['owners']:
            del self.data['owners'][user_id]
            self.save_data()
            return True
        return False
    
    def add_admin(self, user_id, name="Unknown"):
        self.data['admins'][user_id] = {
            'name': name,
            'added': time.time(),
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
    
    def remove_admin(self, user_id):
        if user_id in self.data['admins']:
            del self.data['admins'][user_id]
            self.save_data()
            return True
        return False
    
    def ban_user(self, user_id, reason="No reason"):
        self.data['banned'][user_id] = {
            'reason': reason,
            'banned_at': time.time(),
            'banned_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
    
    def unban_user(self, user_id):
        if user_id in self.data['banned']:
            del self.data['banned'][user_id]
            self.save_data()
            return True
        return False

db = BotDatabase()

# ========== وظائف مساعدة ==========
def get_uptime():
    """حساب وقت التشغيل"""
    uptime = int(time.time() - db.start_time)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    seconds = uptime % 60
    return f"{hours}س {minutes}د {seconds}ث"

def get_commands_text():
    """قائمة الأوامر"""
    return """╔═══════════════════
║ 🛡️ أوامر البوت الحامي
║
║ 📋 عام:
║ • help - قائمة الأوامر
║ • status - حالة البوت
║ • me - معلوماتي
║ • myid - معرفي
║ • time - الوقت الحالي
║
║ 👑 المالك فقط:
║ • addadmin @mention
║ • removeadmin @mention
║ • ban @mention
║ • unban @mention
║ • owners - قائمة المالكين
║ • admins - قائمة الأدمنز
║ • banned - قائمة المحظورين
║ • addowner [user_id]
║ • removeowner [user_id]
║
║ 🔧 إعدادات:
║ • protect on/off
║ • welcome on/off
║
║ 🔐 التفعيل الأول:
║ • activate [code]
║
╚═══════════════════"""

def get_user_profile(user_id):
    """جلب معلومات المستخدم"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            profile = line_bot_api.get_profile(user_id)
            return {
                'display_name': profile.display_name,
                'user_id': profile.user_id,
                'picture_url': profile.picture_url if hasattr(profile, 'picture_url') else None,
                'status_message': profile.status_message if hasattr(profile, 'status_message') else None
            }
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return None

# ========== Flask Routes ==========
@app.route("/")
def home():
    """الصفحة الرئيسية"""
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🛡️ LINE Protection Bot</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        .container {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 50px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
        .status {{ 
            background: rgba(0,255,0,0.2);
            padding: 15px;
            border-radius: 15px;
            margin: 20px 0;
            font-size: 1.2em;
        }}
        .info {{ 
            margin: 10px 0; 
            font-size: 1.1em;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .footer {{ margin-top: 30px; opacity: 0.7; }}
        .setup-info {{
            background: rgba(255,200,0,0.2);
            padding: 15px;
            border-radius: 15px;
            margin-top: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ LINE Protection Bot</h1>
        <div class="status">✅ Online & Working</div>
        <div class="info">⏰ Uptime: {get_uptime()}</div>
        <div class="info">👑 Owners: {len(db.data['owners'])}</div>
        <div class="info">👮 Admins: {len(db.data['admins'])}</div>
        <div class="info">🚫 Banned: {len(db.data['banned'])}</div>
        {'<div class="setup-info">⚠️ لإضافة نفسك كـ Owner:<br>أرسل للبوت: activate ' + ACTIVATION_CODE + '</div>' if len(db.data['owners']) == 0 else ''}
        <div class="footer">Made with ❤️ for LINE</div>
    </div>
</body>
</html>""", 200

@app.route("/callback", methods=['POST'])
def callback():
    """استقبال رسائل LINE"""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ Invalid signature")
        abort(400)
    
    return 'OK'

@app.route("/health")
def health():
    """فحص صحة البوت"""
    return {
        "status": "healthy",
        "uptime": int(time.time() - db.start_time),
        "owners": len(db.data['owners']),
        "admins": len(db.data['admins'])
    }, 200

# ========== معالجات الرسائل ==========
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """معالجة الرسائل النصية"""
    text = event.message.text.strip()
    text_lower = text.lower()
    user_id = event.source.user_id
    
    # منع المحظورين
    if db.is_banned(user_id):
        return
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        reply_text = ""
        
        # 🔐 تفعيل Owner الأول
        if text_lower.startswith('activate '):
            code = text[9:].strip()
            if code == ACTIVATION_CODE:
                if not db.is_owner(user_id):
                    profile = get_user_profile(user_id)
                    name = profile['display_name'] if profile else "Unknown"
                    db.add_owner(user_id, name)
                    reply_text = f"""╔═══════════════════
║ 🎉 تم التفعيل بنجاح!
║ 👑 أنت الآن Owner
║ 👤 {name}
║ 🆔 {user_id}
║
║ 📝 استخدم 'help' للأوامر
╚═══════════════════"""
                else:
                    reply_text = "✅ أنت Owner بالفعل!"
            else:
                reply_text = "❌ كود خاطئ!"
        
        # الأوامر
        elif text_lower in ['help', 'مساعدة', 'الأوامر']:
            reply_text = get_commands_text()
        
        elif text_lower in ['status', 'الحالة']:
            reply_text = f"""╔═══════════════════
║ 📊 حالة البوت
║ ⏰ {get_uptime()}
║ 👑 المالكين: {len(db.data['owners'])}
║ 👮 الأدمنز: {len(db.data['admins'])}
║ 🚫 المحظورين: {len(db.data['banned'])}
║ 🛡️ الحماية: {'مفعلة ✅' if db.data['settings']['protect'] else 'معطلة ❌'}
║ 👋 الترحيب: {'مفعل ✅' if db.data['settings']['welcome'] else 'معطل ❌'}
╚═══════════════════"""
        
        elif text_lower in ['me', 'معلوماتي']:
            profile = get_user_profile(user_id)
            role = '👑 Owner' if db.is_owner(user_id) else '👮 Admin' if db.is_admin(user_id) else '👤 Member'
            reply_text = f"""╔═══════════════════
║ 📱 معلوماتك
║ 👤 {profile['display_name'] if profile else 'Unknown'}
║ 🆔 {user_id}
║ 🏆 الرتبة: {role}
╚═══════════════════"""
        
        elif text_lower in ['myid', 'معرفي']:
            reply_text = f"🆔 معرفك:\n{user_id}"
        
        elif text_lower in ['time', 'الوقت']:
            now = datetime.now()
            reply_text = f"🕐 الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        elif text_lower == 'owners' and db.is_admin(user_id):
            if db.data['owners']:
                reply_text = "╔═══ 👑 المالكين ═══\n"
                for i, (uid, data) in enumerate(db.data['owners'].items(), 1):
                    reply_text += f"║ {i}. {data.get('name', 'Unknown')}\n"
                    reply_text += f"║    🆔 {uid}\n"
                reply_text += "╚═══════════════════"
            else:
                reply_text = "❌ لا يوجد مالكين"
        
        elif text_lower == 'admins' and db.is_admin(user_id):
            if db.data['admins']:
                reply_text = "╔═══ 👮 الأدمنز ═══\n"
                for i, (uid, data) in enumerate(db.data['admins'].items(), 1):
                    reply_text += f"║ {i}. {data.get('name', 'Unknown')}\n"
                    reply_text += f"║    🆔 {uid}\n"
                reply_text += "╚═══════════════════"
            else:
                reply_text = "❌ لا يوجد أدمنز"
        
        elif text_lower == 'banned' and db.is_admin(user_id):
            if db.data['banned']:
                reply_text = "╔═══ 🚫 المحظورين ═══\n"
                for i, (uid, data) in enumerate(db.data['banned'].items(), 1):
                    reply_text += f"║ {i}. {uid}\n"
                    reply_text += f"║    📝 {data.get('reason', 'No reason')}\n"
                reply_text += "╚═══════════════════"
            else:
                reply_text = "✅ لا يوجد محظورين"
        
        elif text_lower == 'protect on' and db.is_owner(user_id):
            db.data['settings']['protect'] = True
            db.save_data()
            reply_text = "✅ تم تفعيل الحماية"
        
        elif text_lower == 'protect off' and db.is_owner(user_id):
            db.data['settings']['protect'] = False
            db.save_data()
            reply_text = "❌ تم إيقاف الحماية"
        
        elif text_lower == 'welcome on' and db.is_admin(user_id):
            db.data['settings']['welcome'] = True
            db.save_data()
            reply_text = "✅ تم تفعيل الترحيب"
        
        elif text_lower == 'welcome off' and db.is_admin(user_id):
            db.data['settings']['welcome'] = False
            db.save_data()
            reply_text = "❌ تم إيقاف الترحيب"
        
        elif text_lower.startswith('addowner ') and db.is_owner(user_id):
            target_id = text[9:].strip()
            if target_id and not db.is_owner(target_id):
                profile = get_user_profile(target_id)
                name = profile['display_name'] if profile else "Unknown"
                db.add_owner(target_id, name)
                reply_text = f"✅ تمت إضافة {name} كـ Owner"
            else:
                reply_text = "❌ معرف خاطئ أو موجود مسبقاً"
        
        elif text_lower.startswith('removeowner ') and db.is_owner(user_id):
            target_id = text[12:].strip()
            if db.remove_owner(target_id):
                reply_text = "✅ تم حذف Owner"
            else:
                reply_text = "❌ غير موجود"
        
        elif text_lower.startswith('addadmin ') and db.is_owner(user_id):
            target_id = text[9:].strip()
            if target_id and not db.is_admin(target_id):
                profile = get_user_profile(target_id)
                name = profile['display_name'] if profile else "Unknown"
                db.add_admin(target_id, name)
                reply_text = f"✅ تمت إضافة {name} كـ Admin"
            else:
                reply_text = "❌ معرف خاطئ أو موجود مسبقاً"
        
        elif text_lower.startswith('removeadmin ') and db.is_owner(user_id):
            target_id = text[12:].strip()
            if db.remove_admin(target_id):
                reply_text = "✅ تم حذف Admin"
            else:
                reply_text = "❌ غير موجود"
        
        elif text_lower.startswith('ban ') and db.is_owner(user_id):
            parts = text[4:].split(' ', 1)
            target_id = parts[0].strip()
            reason = parts[1] if len(parts) > 1 else "No reason"
            if target_id and not db.is_owner(target_id):
                db.ban_user(target_id, reason)
                reply_text = f"✅ تم حظر المستخدم"
            else:
                reply_text = "❌ لا يمكن حظر Owner"
        
        elif text_lower.startswith('unban ') and db.is_owner(user_id):
            target_id = text[6:].strip()
            if db.unban_user(target_id):
                reply_text = "✅ تم إلغاء الحظر"
            else:
                reply_text = "❌ غير محظور"
        
        else:
            # رد تلقائي إذا لم يكن أمراً معروفاً
            if not db.data['owners']:
                reply_text = f"🔐 للتفعيل الأول:\nactivate {ACTIVATION_CODE}\n\n📝 بعدها استخدم: help"
            else:
                reply_text = "❓ أمر غير معروف\n📝 استخدم: help"
        
        # إرسال الرد
        if reply_text:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )

@handler.add(JoinEvent)
def handle_join(event):
    """عند انضمام البوت لمجموعة"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        welcome = """🛡️ مرحباً! أنا بوت الحماية
✅ تم تفعيلي بنجاح
📝 استخدم 'help' للأوامر
👑 المالكين فقط يمكنهم التحكم"""
        
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome)]
            )
        )

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    """عند انضمام عضو جديد"""
    if db.data['settings']['welcome']:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            welcome = "👋 مرحباً بك في المجموعة!"
            
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome)]
                )
            )

# ========== تشغيل البوت ==========
if __name__ == "__main__":
    print("="*60)
    print("🛡️ LINE Protection Bot Starting...")
    print("="*60)
    print(f"✅ Owners: {len(db.data['owners'])}")
    print(f"✅ Admins: {len(db.data['admins'])}")
    if len(db.data['owners']) == 0:
        print(f"⚠️  First setup: Send 'activate {ACTIVATION_CODE}' to bot")
    print(f"✅ Settings loaded successfully")
    print("="*60)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
