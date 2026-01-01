# -*- coding: utf-8 -*-
"""
بوت LINE للحماية - النسخة النهائية المحدثة
Flask + LINE Bot SDK الرسمي
Compatible with Render.com
يدعم INITIAL_ADMIN_ID من Environment Variables
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

# ========== Flask Setup ==========
app = Flask(__name__)

# ========== LINE Credentials ==========
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
INITIAL_ADMIN_ID = os.getenv('INITIAL_ADMIN_ID', '')  # ✅ جديد

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("="*50)
    print("❌ خطأ: بيانات LINE غير موجودة!")
    print("أضف في Render Environment:")
    print("  LINE_CHANNEL_ACCESS_TOKEN=...")
    print("  LINE_CHANNEL_SECRET=...")
    print("  INITIAL_ADMIN_ID=...  (اختياري)")
    print("="*50)
    exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ========== Data Storage ==========
class Database:
    def __init__(self):
        self.owners = self.load('owners.json', {})
        self.admins = self.load('admins.json', {})
        self.banned = self.load('banned.json', {})
        
        # ✅ إضافة INITIAL_ADMIN_ID تلقائياً
        if INITIAL_ADMIN_ID and INITIAL_ADMIN_ID not in self.owners:
            self.owners[INITIAL_ADMIN_ID] = True
            print(f"✅ تمت إضافة Admin من Environment: {INITIAL_ADMIN_ID[:20]}...")
        
        self.settings = {
            'protect': True,
            'kick_protect': True,
            'invite_protect': True,
            'welcome': True
        }
        self.start_time = time.time()
        self.bot_user_id = None  # ✅ سيتم تعبئته تلقائياً
        
        # محاولة الحصول على Bot User ID
        try:
            profile = line_bot_api.get_bot_info()
            self.bot_user_id = profile.user_id
            print(f"✅ Bot User ID: {self.bot_user_id}")
        except Exception as e:
            print(f"⚠️ لم أستطع الحصول على Bot ID: {e}")
        
        print("="*50)
        print("✅ تم تحميل البيانات:")
        print(f"   👑 مالكين: {len(self.owners)}")
        print(f"   👮 أدمن: {len(self.admins)}")
        print(f"   🚫 محظورين: {len(self.banned)}")
        if self.bot_user_id:
            print(f"   🤖 Bot ID: {self.bot_user_id[:25]}...")
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

db = Database()

# ========== Helper Functions ==========
def is_owner(user_id):
    return user_id in db.owners

def is_admin(user_id):
    return user_id in db.owners or user_id in db.admins

def get_runtime():
    elapsed = int(time.time() - db.start_time)
    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60
    return f"{h}س {m}د {s}ث"

def send_message(to, text):
    try:
        line_bot_api.push_message(to, TextSendMessage(text=text))
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

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
    
    if cmd == 'help' or cmd == 'الأوامر':
        help_text = """╔════════════════════
║ 🤖 بوت الحماية
║
║ 📋 عامة:
║ • help - الأوامر
║ • status - الحالة
║ • myid - معرفي
║ • botid - معرف البوت
║ • time - الوقت
║
║ 👮 أدمن:
║ • protect on/off
║ • adminlist
║ • ownerlist
║
║ 👑 مالك:
║ • addadmin USER_ID
║ • deladmin USER_ID
║ • addowner USER_ID
║ • banlist
║ • clearban
║
╚════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))
    
    elif cmd == 'status' or cmd == 'الحالة':
        status = f"""╔════════════════════
║ 📊 حالة البوت
║
║ ⏰ التشغيل: {get_runtime()}
║ 👑 مالكين: {len(db.owners)}
║ 👮 أدمن: {len(db.admins)}
║ 🚫 محظورين: {len(db.banned)}
║
║ 🛡️ الحماية:
║ • طرد: {'✅' if db.settings['kick_protect'] else '❌'}
║ • دعوات: {'✅' if db.settings['invite_protect'] else '❌'}
║
╚════════════════════"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status))
    
    elif cmd == 'myid' or cmd == 'معرفي':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"📱 معرفك:\n{user_id}\n\n💡 انسخه واستخدمه في Render!")
        )
    
    elif cmd == 'botid' or cmd == 'معرف البوت':
        if db.bot_user_id:
            bot_text = f"""🤖 معرف البوت:
{db.bot_user_id}

📝 لجعل البوت أدمن:
1. اذهب لإعدادات المجموعة
2. اختر 'إدارة الأعضاء'
3. ابحث عن البوت وارفعه لـ Admin"""
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=bot_text))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ معرف البوت غير متوفر حالياً")
            )
    
    elif cmd == 'time' or cmd == 'الوقت':
        now = datetime.now()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}")
        )
    
    elif cmd == 'protect on' and is_admin(user_id):
        db.settings['protect'] = True
        db.settings['kick_protect'] = True
        db.settings['invite_protect'] = True
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم تفعيل الحماية"))
    
    elif cmd == 'protect off' and is_admin(user_id):
        db.settings['protect'] = False
        db.settings['kick_protect'] = False
        db.settings['invite_protect'] = False
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ تم إيقاف الحماية"))
    
    elif cmd == 'ownerlist' and is_admin(user_id):
        if not db.owners:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ لا يوجد مالكين"))
        else:
            owner_text = "╔════════════════════\n║ 👑 قائمة المالكين\n║\n"
            for i, owner_id in enumerate(db.owners.keys(), 1):
                owner_text += f"║ {i}. {owner_id[:20]}...\n"
            owner_text += "╚════════════════════"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=owner_text))
    
    elif cmd == 'adminlist' and is_admin(user_id):
        if not db.admins:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ لا يوجد أدمن"))
        else:
            admin_text = "╔════════════════════\n║ 👮 قائمة الأدمن\n║\n"
            for i, admin_id in enumerate(db.admins.keys(), 1):
                admin_text += f"║ {i}. {admin_id[:20]}...\n"
            admin_text += "╚════════════════════"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=admin_text))
    
    elif cmd.startswith('addadmin') and is_owner(user_id):
        parts = text.split()
        if len(parts) == 2:
            new_admin = parts[1]
            db.admins[new_admin] = True
            db.save()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تمت إضافة أدمن"))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="📝 استخدم: addadmin USER_ID\nاحصل على ID من: myid")
            )
    
    elif cmd.startswith('deladmin') and is_owner(user_id):
        parts = text.split()
        if len(parts) == 2:
            admin_id = parts[1]
            if admin_id in db.admins:
                del db.admins[admin_id]
                db.save()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم حذف الأدمن"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="📝 استخدم: deladmin USER_ID"))
    
    elif cmd.startswith('addowner') and is_owner(user_id):
        parts = text.split()
        if len(parts) == 2:
            new_owner = parts[1]
            db.owners[new_owner] = True
            db.save()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تمت إضافة مالك"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="📝 استخدم: addowner USER_ID"))
    
    elif cmd == 'banlist' and is_owner(user_id):
        if not db.banned:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ قائمة المحظورين فارغة"))
        else:
            ban_text = f"╔════════════════════\n║ 🚫 المحظورين ({len(db.banned)})\n║\n"
            for i, ban_id in enumerate(list(db.banned.keys())[:15], 1):
                ban_text += f"║ {i}. {ban_id[:15]}...\n"
            ban_text += "╚════════════════════"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ban_text))
    
    elif cmd == 'clearban' and is_owner(user_id):
        db.banned = {}
        db.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ تم مسح قائمة المحظورين"))

# ========== Event Handlers ==========

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    try:
        handle_command(event)
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

@handler.add(JoinEvent)
def handle_join(event):
    """عند انضمام البوت لمجموعة"""
    try:
        if event.source.type == 'group':
            group_id = event.source.group_id
            welcome = """╔════════════════════
║ 👋 مرحباً!
║
║ أنا بوت الحماية
║ 🛡️ سأحمي مجموعتك
║
║ 📋 الأوامر: help
║ 📱 معرفك: myid
║ 🤖 معرفي: botid
║
╚════════════════════"""
            line_bot_api.push_message(group_id, TextSendMessage(text=welcome))
            print(f"✅ انضممت لمجموعة: {group_id}")
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
                # التحقق من المحظورين
                if user_id in db.banned:
                    try:
                        line_bot_api.kick_out_user_from_group(group_id, user_id)
                        send_message(group_id, "⚠️ تم طرد عضو محظور")
                        print(f"⚠️ طرد محظور: {user_id}")
                    except Exception as e:
                        print(f"❌ فشل الطرد: {e}")
    except Exception as e:
        print(f"❌ خطأ في handle_member_joined: {e}")

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    """عند مغادرة عضو"""
    pass

# ========== Flask Routes ==========

@app.route("/", methods=['GET'])
def home():
    bot_id_display = db.bot_user_id[:30] + "..." if db.bot_user_id else "غير متوفر"
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>LINE Bot</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
                max-width: 600px;
                margin: 0 auto;
                backdrop-filter: blur(10px);
            }}
            h1 {{ font-size: 3em; margin: 0; }}
            .status {{ font-size: 1.5em; margin: 20px 0; }}
            .info {{ margin: 10px 0; opacity: 0.9; }}
            .bot-id {{ 
                background: rgba(0,0,0,0.2); 
                padding: 10px; 
                border-radius: 5px; 
                font-family: monospace;
                font-size: 0.9em;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖</h1>
            <div class="status">✅ البوت يعمل</div>
            <hr style="border: 1px solid rgba(255,255,255,0.3);">
            <div class="info">🛡️ LINE Protection Bot v2.1</div>
            <div class="info">⏰ التشغيل: {get_runtime()}</div>
            <div class="info">👑 مالكين: {len(db.owners)}</div>
            <div class="info">👮 أدمن: {len(db.admins)}</div>
            <hr style="border: 1px solid rgba(255,255,255,0.3);">
            <div class="info">🤖 Bot ID:</div>
            <div class="bot-id">{bot_id_display}</div>
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
        "uptime": get_runtime(),
        "owners": len(db.owners),
        "admins": len(db.admins),
        "banned": len(db.banned),
        "bot_id": db.bot_user_id,
        "timestamp": datetime.now().isoformat()
    }, 200

# ========== Startup ==========
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 بوت LINE للحماية - النسخة النهائية")
    print("="*50)
    print("✅ Flask Server")
    print("✅ LINE Bot SDK v3")
    print("="*50)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
