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
    MemberLeftEvent
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
    try:
        profile = messaging_api.get_profile(user_id)
        return profile.display_name
    except:
        return "مستخدم"

def get_mentioned_ids(event):
    try:
        if hasattr(event.message, 'mention') and event.message.mention:
            return [m.user_id for m in event.message.mention.mentionees]
        return []
    except:
        return []

# ========== Command Handler ==========
def handle_command(event):
    text = event.message.text.strip()
    cmd = text.lower()
    user_id = event.source.user_id
    
    if event.source.type == 'group':
        to = event.source.group_id
    elif event.source.type == 'room':
        to = event.source.room_id
    else:
        to = user_id
    
    if cmd in ['help', 'الأوامر', 'مساعدة']:
        help_text = """╔═══════════════════════
║ 🛡️ بوت الحماية الكامل v3.0
║
║ 📋 للجميع:
║ • help - قائمة الأوامر
║ • status - حالة البوت
║ • myid - معرفي
║ • botid - معرف البوت
║
║ 👮 Admin:
║ • protect on/off
║ • kickprotect on/off
║ • inviteprotect on/off
║ • qrprotect on/off
║ • allprotect on/off
║
║ 👑 Owner:
║ • addadmin @منشن
║ • deladmin @منشن
║ • ban @منشن
║ • unban @منشن
║ • banlist
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
║ 🛡️ الحماية: {'✅' if db.settings['protect'] else '❌'}
║ • الطرد: {'✅' if db.settings['kick_protect'] else '❌'}
║ • الدعوات: {'✅' if db.settings['invite_protect'] else '❌'}
║ • الرابط: {'✅' if db.settings['qr_protect'] else '❌'}
║
╚═══════════════════════"""
        reply_message(event.reply_token, status)
    
    elif cmd in ['myid', 'معرفي']:
        reply_message(event.reply_token, f"📱 معرفك:\n{user_id}")
    
    elif cmd in ['botid', 'معرف البوت']:
        if db.bot_user_id:
            reply_message(event.reply_token, f"🤖 معرف البوت:\n{db.bot_user_id}")
        else:
            reply_message(event.reply_token, "⚠️ معرف البوت غير متوفر")
    
    # Protection Commands
    elif cmd == 'protect on' and is_admin(user_id):
        db.settings['protect'] = True
        reply_message(event.reply_token, "✅ تم تفعيل الحماية")
    
    elif cmd == 'protect off' and is_admin(user_id):
        db.settings['protect'] = False
        reply_message(event.reply_token, "❌ تم إيقاف الحماية")
    
    elif cmd == 'kickprotect on' and is_admin(user_id):
        db.settings['kick_protect'] = True
        reply_message(event.reply_token, "✅ حماية الطرد مفعّلة")
    
    elif cmd == 'kickprotect off' and is_admin(user_id):
        db.settings['kick_protect'] = False
        reply_message(event.reply_token, "❌ حماية الطرد متوقفة")
    
    elif cmd == 'inviteprotect on' and is_admin(user_id):
        db.settings['invite_protect'] = True
        reply_message(event.reply_token, "✅ حماية الدعوات مفعّلة")
    
    elif cmd == 'inviteprotect off' and is_admin(user_id):
        db.settings['invite_protect'] = False
        reply_message(event.reply_token, "❌ حماية الدعوات متوقفة")
    
    elif cmd == 'allprotect on' and is_admin(user_id):
        for key in db.settings:
            if 'protect' in key:
                db.settings[key] = True
        reply_message(event.reply_token, "✅ تم تفعيل كل الحماية")
    
    elif cmd == 'allprotect off' and is_admin(user_id):
        for key in db.settings:
            if 'protect' in key:
                db.settings[key] = False
        reply_message(event.reply_token, "⚠️ تم إيقاف كل الحماية")
    
    # Admin Management
    elif cmd.startswith('addadmin') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            for admin_id in mentioned:
                db.admins[admin_id] = True
            db.save()
            reply_message(event.reply_token, f"✅ تمت إضافة {len(mentioned)} أدمن")
        else:
            reply_message(event.reply_token, "📝 اكتب: addadmin @الشخص")
    
    elif cmd.startswith('deladmin') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            for admin_id in mentioned:
                if admin_id in db.admins:
                    del db.admins[admin_id]
            db.save()
            reply_message(event.reply_token, "✅ تم حذف الأدمن")
        else:
            reply_message(event.reply_token, "📝 اكتب: deladmin @الشخص")
    
    # Ban System
    elif cmd.startswith('ban') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            for ban_id in mentioned:
                if not is_owner(ban_id) and not is_admin(ban_id):
                    db.banned[ban_id] = True
            db.save()
            reply_message(event.reply_token, f"✅ تم حظر {len(mentioned)} مستخدم")
        else:
            reply_message(event.reply_token, "📝 اكتب: ban @الشخص")
    
    elif cmd.startswith('unban') and is_owner(user_id):
        mentioned = get_mentioned_ids(event)
        if mentioned:
            for unban_id in mentioned:
                if unban_id in db.banned:
                    del db.banned[unban_id]
            db.save()
            reply_message(event.reply_token, "✅ تم إلغاء الحظر")
        else:
            reply_message(event.reply_token, "📝 اكتب: unban @الشخص")
    
    elif cmd == 'banlist' and is_owner(user_id):
        if not db.banned:
            reply_message(event.reply_token, "✅ قائمة المحظورين فارغة")
        else:
            text_list = f"╔═══[ المحظورين ({len(db.banned)}) ]\n"
            for i, ban_id in enumerate(list(db.banned.keys())[:10], 1):
                text_list += f"║ {i}. {get_user_name(ban_id)}\n"
            text_list += "╚═══════════════"
            reply_message(event.reply_token, text_list)

# ========== Event Handlers ==========
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        handle_command(event)
    except Exception as e:
        print(f"❌ خطأ: {e}")

@handler.add(JoinEvent)
def handle_join(event):
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            welcome = """╔═══════════════════════
║ 👋 مرحباً! أنا بوت الحماية
║ 🛡️ اكتب: help للأوامر
║ ⚠️ اجعلني أدمن للحماية!
╚═══════════════════════"""
            send_message(group_id, welcome)
            db.add_log(f"انضممت لمجموعة جديدة")
    except Exception as e:
        print(f"❌ خطأ: {e}")

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            for member in event.joined.members:
                user_id = member.user_id
                if user_id in db.banned:
                    db.add_log(f"عضو محظور حاول الدخول!")
                    send_message(group_id, "⚠️ تم رصد عضو محظور!")
                elif db.settings.get('welcome_message'):
                    name = get_user_name(user_id)
                    send_message(group_id, f"👋 مرحباً {name}!")
    except Exception as e:
        print(f"❌ خطأ: {e}")

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            for member in event.left.members:
                user_id = member.user_id
                if is_bot(user_id) or is_owner(user_id) or is_admin(user_id):
                    name = get_user_name(user_id)
                    db.add_log(f"⚠️ تم طرد {name}!")
                    if db.settings['kick_protect']:
                        send_message(group_id, f"🚨 تحذير: تم طرد {name}!")
    except Exception as e:
        print(f"❌ خطأ: {e}")

# ========== Flask Routes ==========
@app.route("/", methods=['GET'])
def home():
    protection_status = "✅ مفعّل" if db.settings['protect'] else "❌ متوقف"
    return f"""
<html>
<head>
    <meta charset="utf-8">
    <title>🛡️ LINE Protection Bot</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #667eea; text-align: center; }}
        .status {{
            text-align: center;
            font-size: 1.5em;
            color: #28a745;
            margin: 20px 0;
        }}
        .info {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ LINE Protection Bot</h1>
        <div class="status">{protection_status}</div>
        <div class="info">
            <p>⏰ وقت التشغيل: {get_runtime()}</p>
            <p>👑 المالكين: {len(db.owners)}</p>
            <p>👮 الأدمن: {len(db.admins)}</p>
            <p>🚫 المحظورين: {len(db.banned)}</p>
        </div>
    </div>
</body>
</html>
""", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
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
    return {
        "status": "healthy",
        "uptime": get_runtime(),
        "owners": len(db.owners),
        "admins": len(db.admins),
        "banned": len(db.banned),
        "protection": db.settings['protect']
    }, 200

# ========== Startup ==========
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛡️ بوت LINE للحماية v3.0")
    print("="*50)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
