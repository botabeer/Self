import time
import random
import threading
from datetime import datetime
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, PushMessageRequest,
    TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

class SpamBot:
    def __init__(self):
        self.active_spams = {}
        self.spam_threads = {}
        self.spam_messages = []
        self.spam_speed = 1
        self.spam_count = 0
        
    def start_spam(self, group_id, messages, speed, count):
        if group_id in self.active_spams:
            return False, "السبام يعمل بالفعل"
        
        self.active_spams[group_id] = True
        thread = threading.Thread(
            target=self._spam_worker,
            args=(group_id, messages, speed, count)
        )
        self.spam_threads[group_id] = thread
        thread.start()
        return True, "تم بدء السبام"
    
    def stop_spam(self, group_id):
        if group_id in self.active_spams:
            self.active_spams[group_id] = False
            return True, "تم ايقاف السبام"
        return False, "السبام غير نشط"
    
    def _spam_worker(self, group_id, messages, speed, count):
        sent = 0
        while self.active_spams.get(group_id, False):
            if count > 0 and sent >= count:
                break
            
            try:
                msg = random.choice(messages)
                push_message(group_id, msg)
                sent += 1
                logger.info(f"ارسال رسالة {sent}")
                time.sleep(speed)
            except Exception as e:
                logger.error(f"خطأ في السبام: {e}")
                time.sleep(1)
        
        if group_id in self.active_spams:
            del self.active_spams[group_id]
        if group_id in self.spam_threads:
            del self.spam_threads[group_id]

spam_bot = SpamBot()

DEFAULT_MESSAGES = [
    "مرحبا",
    "كيف الحال",
    "السلام عليكم",
    "صباح الخير",
    "مساء الخير",
    "كيفكم",
    "وش اخباركم",
    "شخباركم",
    "هلا",
    "اهلين",
]

EMOJIS = ["😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😊", "😎", "🔥", "💯", "✨", "⭐", "🎉", "🎊", "❤️", "💙", "💚", "💛"]

FLOOD_MESSAGES = [
    "فلود " * 10,
    "سبام " * 15,
    "تيست " * 20,
    "هلا " * 25,
    "." * 50,
]

def push_message(to, text):
    try:
        line_bot_api.push_message(
            PushMessageRequest(to=to, messages=[TextMessage(text=text)])
        )
    except Exception as e:
        logger.error(f"خطأ في الارسال: {e}")

def reply_message(reply_token, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
    except Exception as e:
        logger.error(f"خطأ في الرد: {e}")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        logger.error(f"خطأ: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text.strip()
        group_id = getattr(event.source, 'group_id', None)
        
        if not group_id:
            reply_message(event.reply_token, TextMessage(text="يعمل في القروبات فقط"))
            return
        
        if text == "سبام":
            success, msg = spam_bot.start_spam(group_id, DEFAULT_MESSAGES, 0.5, 50)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text.startswith("سبام "):
            try:
                parts = text.split(maxsplit=1)
                custom_msg = parts[1]
                messages = [custom_msg] * 10
                success, msg = spam_bot.start_spam(group_id, messages, 0.3, 100)
                reply_message(event.reply_token, TextMessage(text=msg))
            except:
                reply_message(event.reply_token, TextMessage(text="صيغة خاطئة\nاكتب: سبام الرسالة"))
            return
        
        if text == "فلود":
            success, msg = spam_bot.start_spam(group_id, FLOOD_MESSAGES, 0.1, 100)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text == "ايموجي":
            emoji_msgs = [random.choice(EMOJIS) * random.randint(5, 20) for _ in range(20)]
            success, msg = spam_bot.start_spam(group_id, emoji_msgs, 0.2, 50)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text.startswith("سبام سريع"):
            success, msg = spam_bot.start_spam(group_id, ["سريع"] * 20, 0.05, 200)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text.startswith("سبام بطيء"):
            success, msg = spam_bot.start_spam(group_id, DEFAULT_MESSAGES, 2, 30)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text.startswith("سبام ارقام"):
            num_msgs = [str(i) for i in range(1, 101)]
            success, msg = spam_bot.start_spam(group_id, num_msgs, 0.3, 100)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text == "ايقاف":
            success, msg = spam_bot.stop_spam(group_id)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text == "الاوامر":
            commands = """اوامر السبام

سبام - سبام عادي 50 رسالة
سبام [نص] - سبام نص مخصص
فلود - فلود قوي 100 رسالة
ايموجي - سبام ايموجي
سبام سريع - سبام فائق السرعة
سبام بطيء - سبام بطيء
سبام ارقام - سبام من 1 الى 100
ايقاف - ايقاف السبام

تحذير: استخدم بمسؤولية"""
            reply_message(event.reply_token, TextMessage(text=commands))
            return
        
        if text == "سبام منشن":
            mention_msgs = ["@المستخدم " * 5 for _ in range(30)]
            success, msg = spam_bot.start_spam(group_id, mention_msgs, 0.4, 30)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text == "سبام اسطر":
            line_msgs = ["\n" * random.randint(10, 20) + "سطر" for _ in range(20)]
            success, msg = spam_bot.start_spam(group_id, line_msgs, 0.5, 20)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text.startswith("سبام متقدم"):
            try:
                parts = text.split()
                count = int(parts[2]) if len(parts) > 2 else 50
                speed = float(parts[3]) if len(parts) > 3 else 0.5
                
                advanced_msgs = [
                    f"رسالة {i} - {random.choice(['تجربة', 'تيست', 'سبام', 'فلود'])}"
                    for i in range(count)
                ]
                success, msg = spam_bot.start_spam(group_id, advanced_msgs, speed, count)
                reply_message(event.reply_token, TextMessage(text=msg))
            except:
                reply_message(event.reply_token, TextMessage(text="صيغة: سبام متقدم [العدد] [السرعة]"))
            return
        
        if text == "سبام عشوائي":
            random_msgs = []
            for _ in range(50):
                msg_type = random.choice(['text', 'emoji', 'number', 'mixed'])
                if msg_type == 'text':
                    random_msgs.append(random.choice(DEFAULT_MESSAGES))
                elif msg_type == 'emoji':
                    random_msgs.append(random.choice(EMOJIS) * random.randint(3, 10))
                elif msg_type == 'number':
                    random_msgs.append(str(random.randint(1, 1000)))
                else:
                    random_msgs.append(f"{random.choice(DEFAULT_MESSAGES)} {random.choice(EMOJIS)}")
            
            success, msg = spam_bot.start_spam(group_id, random_msgs, 0.3, 50)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        if text == "قنبلة":
            bomb_msgs = ["💣"] * 100
            success, msg = spam_bot.start_spam(group_id, bomb_msgs, 0.05, 100)
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'online', 'active_spams': len(spam_bot.active_spams)}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
