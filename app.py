# -*- coding: utf-8 -*-
"""
🛡️ LINE Protection Bot - Official API
✅ يعمل 100% على Render
✅ بدون مشاكل Git أو linepy
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ========== LINE Credentials ==========
# احصل عليها من: https://developers.line.biz/console/
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("❌ أضف LINE_CHANNEL_ACCESS_TOKEN و LINE_CHANNEL_SECRET في Environment Variables")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ========== قاعدة البيانات ==========
class Database:
    def __init__(self):
        self.owners = self.load('owners.json', {})
        self.admins = self.load('admins.json', {})
        self.banned = self.load('banned.json', {})
        self.settings = {
            'protect': True,
            'welcome': True,
            'auto_kick_banned': True
        }
        self.start_time = time.time()
    
    def load(self, filename, default):
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return default
        except:
            return default
    
    def save(self):
        try:
            for fname, data in [
                ('owners.json', self.owners),
                ('admins.json', self.admins),
                ('banned.json', self.banned)
            ]:
                with open(fname, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ خطأ حفظ: {e}")
    
    def is_owner(self, user_id):
        return user_id in self.owners
    
    def is_admin(self, user_id):
        return user_id in self.owners or user_id in self.admins
    
    def is_banned(self, user_id):
        return user_id in self.banned

db = Database()

# ========== Flask Routes ==========
@app.route("/")
def home():
    uptime = int(time.time() - db.start_time)
    h, m = uptime // 3600, (uptime % 3600) // 60
    
    return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="utf-8">
    <title>🛡️ LINE Bot</title>
    <style>
        body {{
            font-family: Arial;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
        }}
        .container {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ LINE Protection Bot</h1>
        <p>✅ Online</p>
        <p>⏰ {h}س {m}د</p>
    </div>
</body>
</html>
""", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@app.route("/health")
def health():
    return {"status": "ok", "uptime": int(time.time() - db.start_time)}, 200

# ========== Message Handler ==========
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.lower().strip()
    user_id = event.source.user_id
    
    # منع المحظورين
    if db.is_banned(user_id):
        return
    
    reply_token = event.reply_token
    
    # الأوامر
    if text in ['help', 'مساعدة']:
        msg = """╔═══════════════
║ 🛡️ البوت الحامي
║
║ 📋 الأوامر:
║ • help - المساعدة
║ • status - الحالة
║ • me - معلوماتي
║
║ 👑 Owner:
║ • addowner @
║ • addadmin @
║ • ban @
║ • unban @
║
╚═══════════════"""
        line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))
    
    elif text in ['status', 'الحالة']:
        uptime = int(time.time() - db.start_time)
        h, m = uptime // 3600, (uptime % 3600) // 60
        msg = f"""╔═══════════════
║ 📊 الحالة
║ ⏰ {h}س {m}د
║ 👑 Owners: {len(db.owners)}
║ 👮 Admins: {len(db.admins)}
║ 🚫 Banned: {len(db.banned)}
╚═══════════════"""
        line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))
    
    elif text == 'me':
        try:
            profile = line_bot_api.get_profile(user_id)
            msg = f"""╔═══════════════
║ 📱 معلوماتك
║ 👤 {profile.display_name}
║ 🆔 {user_id}
║ 🏆 {'👑 Owner' if db.is_owner(user_id) else '👮 Admin' if db.is_admin(user_id) else '👤 Member'}
╚═══════════════"""
            line_bot_api.reply_message(reply_token, TextSendMessage(text=msg))
        except:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="❌ خطأ"))
    
    elif text.startswith('addowner') and db.is_owner(user_id):
        # يتطلب mention - راجع LINE API docs
        line_bot_api.reply_message(reply_token, TextSendMessage(text="✅ قريباً"))
    
    elif text.startswith('ban') and db.is_owner(user_id):
        line_bot_api.reply_message(reply_token, TextSendMessage(text="✅ قريباً"))

# ========== Main ==========
if __name__ == "__main__":
    print("="*50)
    print("🛡️ LINE Protection Bot")
    print("✅ استخدم LINE Official Account")
    print("="*50)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
