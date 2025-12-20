from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, PushMessageRequest,
    TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent,
    JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent
)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import sqlite3
import os
import logging
import re
import time
import hashlib
from threading import Lock
from collections import defaultdict
import atexit

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

db_lock = Lock()

class Database:
    DB_NAME = 'protection.db'
    
    @staticmethod
    def init():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            
            c.execute('''CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                links_protection BOOLEAN DEFAULT 1,
                spam_protection BOOLEAN DEFAULT 1,
                flood_protection BOOLEAN DEFAULT 1,
                bad_words_protection BOOLEAN DEFAULT 1,
                welcome_enabled BOOLEAN DEFAULT 1,
                protection_enabled BOOLEAN DEFAULT 1
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS owners (
                user_id TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS admins (
                user_id TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS banned_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                banned_by TEXT NOT NULL,
                reason TEXT,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_id, user_id)
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                warned_by TEXT NOT NULL,
                reason TEXT,
                warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
            logger.info("✅ تم تهيئة قاعدة البيانات")
        except Exception as e:
            logger.error(f"❌ خطأ في DB: {e}")
    
    @staticmethod
    def create_group(group_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('INSERT OR IGNORE INTO groups (group_id) VALUES (?)', (group_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def is_owner(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT user_id FROM owners WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            return result is not None
        except:
            return False
    
    @staticmethod
    def is_admin(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            return result is not None
        except:
            return False
    
    @staticmethod
    def add_owner(user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('INSERT OR IGNORE INTO owners (user_id) VALUES (?)', (user_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def remove_owner(user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('DELETE FROM owners WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def add_admin(user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def remove_admin(user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def get_admins_list():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT user_id FROM owners')
            owners = [r[0] for r in c.fetchall()]
            c.execute('SELECT user_id FROM admins')
            admins = [r[0] for r in c.fetchall()]
            conn.close()
            return {'owners': owners, 'admins': admins}
        except:
            return {'owners': [], 'admins': []}
    
    @staticmethod
    def ban_user(group_id, user_id, admin_id, reason):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('''INSERT OR REPLACE INTO banned_users 
                    (group_id, user_id, banned_by, reason) VALUES (?, ?, ?, ?)''',
                    (group_id, user_id, admin_id, reason))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def unban_user(group_id, user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('DELETE FROM banned_users WHERE group_id = ? AND user_id = ?', (group_id, user_id))
                deleted = c.rowcount > 0
                conn.commit()
                conn.close()
                return deleted
            except:
                return False
    
    @staticmethod
    def is_banned(group_id, user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT id FROM banned_users WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            result = c.fetchone()
            conn.close()
            return result is not None
        except:
            return False
    
    @staticmethod
    def add_warning(group_id, user_id, admin_id, reason):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('''INSERT INTO warnings (group_id, user_id, warned_by, reason)
                    VALUES (?, ?, ?, ?)''', (group_id, user_id, admin_id, reason))
                c.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?', (group_id, user_id))
                count = c.fetchone()[0]
                conn.commit()
                conn.close()
                return count
            except:
                return 0
    
    @staticmethod
    def get_warnings(group_id, user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            count = c.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    @staticmethod
    def clear_warnings(group_id, user_id):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                c.execute('DELETE FROM warnings WHERE group_id = ? AND user_id = ?', (group_id, user_id))
                conn.commit()
                conn.close()
                return True
            except:
                return False
    
    @staticmethod
    def get_settings(group_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('''SELECT links_protection, spam_protection, flood_protection,
                bad_words_protection, welcome_enabled, protection_enabled 
                FROM groups WHERE group_id = ?''', (group_id,))
            result = c.fetchone()
            conn.close()
            if result:
                return {
                    'links': bool(result[0]),
                    'spam': bool(result[1]),
                    'flood': bool(result[2]),
                    'bad_words': bool(result[3]),
                    'welcome': bool(result[4]),
                    'protection': bool(result[5])
                }
            return {'links': True, 'spam': True, 'flood': True, 'bad_words': True, 'welcome': True, 'protection': True}
        except:
            return {}
    
    @staticmethod
    def update_setting(group_id, setting, value):
        with db_lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                c = conn.cursor()
                settings_map = {
                    'الروابط': 'links_protection',
                    'السبام': 'spam_protection',
                    'الفلود': 'flood_protection',
                    'الكلمات': 'bad_words_protection',
                    'الترحيب': 'welcome_enabled',
                    'الحماية': 'protection_enabled'
                }
                column = settings_map.get(setting)
                if column:
                    c.execute(f'UPDATE groups SET {column} = ? WHERE group_id = ?', (1 if value else 0, group_id))
                    conn.commit()
                    conn.close()
                    return True
                return False
            except:
                return False
    
    @staticmethod
    def get_banned_list(group_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            c = conn.cursor()
            c.execute('SELECT user_id, reason, banned_at FROM banned_users WHERE group_id = ? ORDER BY banned_at DESC', (group_id,))
            results = c.fetchall()
            conn.close()
            return [{'user_id': r[0], 'reason': r[1], 'banned_at': r[2]} for r in results]
        except:
            return []

class Protection:
    def __init__(self):
        self.lock = Lock()
        self.user_messages = defaultdict(list)
        self.message_hashes = defaultdict(set)
        self.muted_users = {}
        self.join_times = {}
        
        self.bad_words = [
            'غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل',
            'خائن', 'كذاب', 'لعين', 'ملعون', 'عاهر', 'زاني', 'فاسق', 'منافق',
            'حيوان', 'قرد', 'بهيمة', 'كس', 'عرص', 'زبي', 'نيك', 'متناك', 
            'شرموط', 'قحبة', 'عاهرة', 'خول', 'منيوك'
        ]
    
    def normalize_text(self, text):
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def check_flood(self, group_id, user_id):
        with self.lock:
            key = f"{group_id}:{user_id}"
            current_time = time.time()
            
            if key not in self.user_messages:
                self.user_messages[key] = []
            
            self.user_messages[key] = [t for t in self.user_messages[key] if current_time - t < 10]
            self.user_messages[key].append(current_time)
            
            count = len(self.user_messages[key])
            if count > 5:
                return True, f"فلود {count} رسائل في 10 ثواني"
            elif count > 3:
                return True, "رسائل سريعة متتالية"
            return False, None
    
    def check_duplicate(self, group_id, user_id, text):
        msg_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"{group_id}:{user_id}"
        
        with self.lock:
            if key not in self.message_hashes:
                self.message_hashes[key] = set()
            
            if msg_hash in self.message_hashes[key]:
                return True, "رسالة مكررة"
            
            self.message_hashes[key].add(msg_hash)
            if len(self.message_hashes[key]) > 50:
                oldest = list(self.message_hashes[key])[0]
                self.message_hashes[key].remove(oldest)
            
            return False, None
    
    def check_links(self, text):
        patterns = [
            r'http[s]?://', r'www\.', r't\.me', r'line\.me',
            r'bit\.ly', r'tinyurl', r'shorturl', r'cutt\.ly',
            r'\w+\.(com|net|org|me|co|info|tv|cc|ly)'
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "رابط محظور"
        return False, None
    
    def check_mentions(self, text):
        mentions = re.findall(r'@\w+', text)
        if len(mentions) > 3:
            return True, f"منشنات زائدة ({len(mentions)})"
        return False, None
    
    def check_phone(self, text):
        phones = re.findall(r'\d{10,}', text)
        if phones:
            return True, "رقم هاتف محظور"
        return False, None
    
    def check_bad_words(self, text):
        normalized = self.normalize_text(text)
        for word in self.bad_words:
            norm_word = self.normalize_text(word)
            if norm_word in normalized:
                return True, f"كلمة غير لائقة"
        return False, None
    
    def check_caps(self, text):
        if len(text) > 20:
            caps = sum(1 for c in text if c.isupper())
            if caps / len(text) > 0.7:
                return True, "احرف كبيرة زائدة"
        return False, None
    
    def check_repeated(self, text):
        if re.findall(r'(.)\1{5,}', text):
            return True, "احرف متكررة"
        return False, None
    
    def check_emoji_spam(self, text):
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        emojis = emoji_pattern.findall(text)
        if len(emojis) > 10:
            return True, f"ايموجي زائد ({len(emojis)})"
        return False, None
    
    def comprehensive_check(self, group_id, user_id, text, settings):
        if not settings.get('protection', True):
            return {'violation': False}
        
        checks = []
        if settings.get('flood', True):
            checks.append(self.check_flood(group_id, user_id))
            checks.append(self.check_duplicate(group_id, user_id, text))
        if settings.get('links', True):
            checks.append(self.check_links(text))
        if settings.get('spam', True):
            checks.append(self.check_mentions(text))
            checks.append(self.check_phone(text))
            checks.append(self.check_emoji_spam(text))
        if settings.get('bad_words', True):
            checks.append(self.check_bad_words(text))
        
        checks.extend([
            self.check_caps(text),
            self.check_repeated(text)
        ])
        
        for is_violation, reason in checks:
            if is_violation:
                severity = self.get_severity(reason)
                return {
                    'violation': True,
                    'reason': reason,
                    'severity': severity
                }
        
        return {'violation': False}
    
    def get_severity(self, reason):
        high = ['رابط', 'رقم هاتف', 'كلمة غير لائقة', 'فلود']
        for keyword in high:
            if keyword in reason:
                return 'high'
        if 'زائد' in reason or 'متكرر' in reason:
            return 'medium'
        return 'low'
    
    def mute_user(self, group_id, user_id, minutes):
        with self.lock:
            key = f"{group_id}:{user_id}"
            self.muted_users[key] = datetime.now() + timedelta(minutes=minutes)
    
    def is_muted(self, group_id, user_id):
        with self.lock:
            key = f"{group_id}:{user_id}"
            if key in self.muted_users:
                if datetime.now() < self.muted_users[key]:
                    return True
                else:
                    del self.muted_users[key]
            return False
    
    def cleanup(self):
        with self.lock:
            current = time.time()
            for key in list(self.user_messages.keys()):
                self.user_messages[key] = [t for t in self.user_messages[key] if current - t < 60]
                if not self.user_messages[key]:
                    del self.user_messages[key]
            
            for key in list(self.muted_users.keys()):
                if datetime.now() >= self.muted_users[key]:
                    del self.muted_users[key]

class FlexUI:
    @staticmethod
    def settings_card(settings):
        def status(val):
            return {"text": "✅ مفعل", "color": "#27AE60"} if val else {"text": "❌ معطل", "color": "#E74C3C"}
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "⚙️ إعدادات الحماية",
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                }],
                "backgroundColor": "#3498DB",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "🔗 حماية الروابط", "size": "sm", "color": "#555555", "flex": 0},
                            {"type": "text", **status(settings.get('links', True)), "size": "sm", "align": "end"}
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "📨 حماية السبام", "size": "sm", "color": "#555555", "flex": 0},
                            {"type": "text", **status(settings.get('spam', True)), "size": "sm", "align": "end"}
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "💬 حماية الفلود", "size": "sm", "color": "#555555", "flex": 0},
                            {"type": "text", **status(settings.get('flood', True)), "size": "sm", "align": "end"}
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "🚫 حماية الكلمات", "size": "sm", "color": "#555555", "flex": 0},
                            {"type": "text", **status(settings.get('bad_words', True)), "size": "sm", "align": "end"}
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "👋 رسالة الترحيب", "size": "sm", "color": "#555555", "flex": 0},
                            {"type": "text", **status(settings.get('welcome', True)), "size": "sm", "align": "end"}
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "🛡️ الحماية العامة", "size": "md", "color": "#111111", "weight": "bold", "flex": 0},
                            {"type": "text", **status(settings.get('protection', True)), "size": "md", "align": "end", "weight": "bold"}
                        ],
                        "margin": "lg"
                    }
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "استخدم: تفعيل/تعطيل [الخيار]",
                    "color": "#aaaaaa",
                    "size": "xs",
                    "align": "center"
                }],
                "paddingAll": "15px"
            }
        }
    
    @staticmethod
    def commands_card(is_admin, is_owner):
        commands = []
        
        commands.append({
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "📋 الأوامر العامة", "weight": "bold", "size": "md", "color": "#111111"},
                {"type": "text", "text": "• الاوامر\n• الاعدادات\n• انذاراتي", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"}
            ]
        })
        
        if is_admin:
            commands.append({
                "type": "separator",
                "margin": "lg"
            })
            commands.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🛡️ أوامر الحماية", "weight": "bold", "size": "md", "color": "#111111"},
                    {"type": "text", "text": "• بان @المستخدم [السبب]\n• الغاء بان @المستخدم\n• كتم @المستخدم [الدقائق]\n• الغاء كتم @المستخدم\n• طرد @المستخدم\n• انذار @المستخدم [السبب]\n• حذف انذار @المستخدم", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"}
                ],
                "margin": "lg"
            })
            commands.append({
                "type": "separator",
                "margin": "lg"
            })
            commands.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "⚙️ أوامر الإعدادات", "weight": "bold", "size": "md", "color": "#111111"},
                    {"type": "text", "text": "• تفعيل/تعطيل الروابط\n• تفعيل/تعطيل السبام\n• تفعيل/تعطيل الفلود\n• تفعيل/تعطيل الكلمات\n• تفعيل/تعطيل الترحيب\n• تفعيل/تعطيل الحماية", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"}
                ],
                "margin": "lg"
            })
        
        if is_owner:
            commands.append({
                "type": "separator",
                "margin": "lg"
            })
            commands.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "👑 أوامر المالك", "weight": "bold", "size": "md", "color": "#111111"},
                    {"type": "text", "text": "• اضف مالك @المستخدم\n• حذف مالك @المستخدم\n• اضف ادمن @المستخدم\n• حذف ادمن @المستخدم\n• قائمة الادمن", "size": "sm", "color": "#555555", "wrap": True, "margin": "sm"}
                ],
                "margin": "lg"
            })
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "📋 قائمة الأوامر",
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                }],
                "backgroundColor": "#9B59B6",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": commands,
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def welcome_card():
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "🎉 مرحباً بك!",
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "xxl",
                    "align": "center"
                }],
                "backgroundColor": "#27AE60",
                "paddingAll": "25px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "👋 أهلاً بك في القروب",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#111111",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "يرجى احترام قوانين القروب\nوالتعامل بأدب مع الجميع",
                        "size": "sm",
                        "color": "#555555",
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "✅ القروب محمي ببوت الحماية",
                        "size": "xs",
                        "color": "#27AE60",
                        "align": "center",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def bot_joined_card():
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "🛡️ بوت الحماية",
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "xxl",
                    "align": "center"
                }],
                "backgroundColor": "#E74C3C",
                "paddingAll": "25px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "شكراً لإضافة البوت! 🎉",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#111111",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "بوت حماية احترافي للقروبات",
                        "size": "sm",
                        "color": "#555555",
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "✨ المميزات:", "weight": "bold", "size": "sm", "color": "#111111"},
                            {"type": "text", "text": "• حماية من الروابط والسبام\n• منع الفلود والرسائل المكررة\n• فلترة الكلمات السيئة\n• نظام إنذارات ذكي\n• إحصائيات وتقارير", "size": "xs", "color": "#555555", "wrap": True, "margin": "sm"}
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "📋 اكتب: الاوامر\nلعرض جميع الأوامر",
                        "size": "sm",
                        "color": "#E74C3C",
                        "align": "center",
                        "weight": "bold",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def banned_list_card(banned_users):
        contents = []
        
        if banned_users:
            for i, user in enumerate(banned_users[:10], 1):
                contents.append({
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"#{i} - {user['user_id'][:15]}...",
                            "size": "sm",
                            "color": "#111111",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": f"السبب: {user.get('reason', 'غير محدد')}",
                            "size": "xs",
                            "color": "#555555",
                            "margin": "xs",
                            "wrap": True
                        }
                    ],
                    "backgroundColor": "#F8F8F8",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "margin": "md" if i > 1 else "none"
                })
        else:
            contents.append({
                "type": "text",
                "text": "لا يوجد مستخدمين محظورين",
                "size": "sm",
                "color": "#555555",
                "align": "center"
            })
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": f"🚫 قائمة المحظورين ({len(banned_users)})",
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                }],
                "backgroundColor": "#E74C3C",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px"
            }
        }

Database.init()
protection = Protection()

scheduler = BackgroundScheduler()
scheduler.add_job(func=protection.cleanup, trigger="interval", minutes=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def extract_user_id(text):
    pattern = r'U[0-9a-f]{32}'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def reply_message(reply_token, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=reply_token, messages=messages))
    except Exception as e:
        logger.error(f"خطأ في الرد: {e}")

def push_message(to, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.push_message(PushMessageRequest(to=to, messages=messages))
    except Exception as e:
        logger.error(f"خطأ في الإرسال: {e}")

def kick_user(group_id, user_id):
    try:
        line_bot_api.leave_group(group_id, user_id)
        return True
    except Exception as e:
        logger.error(f"فشل الطرد: {e}")
        return False

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None)
        
        if not group_id:
            reply_message(event.reply_token, TextMessage(text="هذا البوت يعمل في القروبات فقط"))
            return
        
        try:
            profile = line_bot_api.get_group_member_profile(group_id, user_id)
            display_name = profile.display_name if profile else "مستخدم"
        except:
            display_name = "مستخدم"
        
        is_owner = Database.is_owner(user_id)
        is_admin = Database.is_admin(user_id) or is_owner
        
        # فحص الكتم
        if protection.is_muted(group_id, user_id) and not is_admin:
            return
        
        # أوامر المالك
        if text.startswith("اضف مالك "):
            if not is_owner:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للمالك فقط"))
                return
            mentioned = extract_user_id(text)
            if mentioned:
                Database.add_owner(mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم اضافة المالك بنجاح"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("حذف مالك "):
            if not is_owner:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للمالك فقط"))
                return
            mentioned = extract_user_id(text)
            if mentioned:
                Database.remove_owner(mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم حذف المالك"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        # أوامر الادمن
        if text.startswith("اضف ادمن "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            mentioned = extract_user_id(text)
            if mentioned:
                Database.add_admin(mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم اضافة الادمن بنجاح"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("حذف ادمن "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            mentioned = extract_user_id(text)
            if mentioned:
                Database.remove_admin(mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم حذف الادمن"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        if text == "قائمة الادمن" or text == "الادمن":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            admins = Database.get_admins_list()
            msg = "👥 قائمة المسؤولين\n\n"
            
            if admins['owners']:
                msg += "👑 المالكين:\n"
                for i, owner in enumerate(admins['owners'], 1):
                    msg += f"{i}. {owner[:20]}...\n"
                msg += "\n"
            
            if admins['admins']:
                msg += "⚡ الادمن:\n"
                for i, admin in enumerate(admins['admins'], 1):
                    msg += f"{i}. {admin[:20]}...\n"
            
            if not admins['owners'] and not admins['admins']:
                msg += "لا يوجد مسؤولين حالياً"
            
            reply_message(event.reply_token, TextMessage(text=msg))
            return
        
        # أوامر الحظر
        if text.startswith("بان ") or text.startswith("حظر "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                if Database.is_admin(mentioned) or Database.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="❌ لا يمكن حظر ادمن او مالك"))
                    return
                
                parts = text.split(maxsplit=2)
                reason = parts[2] if len(parts) > 2 else "مخالفة قوانين القروب"
                
                Database.ban_user(group_id, mentioned, user_id, reason)
                kick_user(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text=f"✅ تم حظر المستخدم\n📝 السبب: {reason}"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم\n💡 مثال: بان @المستخدم السبب"))
            return
        
        if text.startswith("الغاء بان ") or text.startswith("الغاء حظر "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                success = Database.unban_user(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم الغاء الحظر" if success else "❌ المستخدم غير محظور"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        # أوامر الكتم
        if text.startswith("كتم ") or text.startswith("ميوت "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                if Database.is_admin(mentioned) or Database.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="❌ لا يمكن كتم ادمن او مالك"))
                    return
                
                parts = text.split()
                duration = 30
                if len(parts) > 2 and parts[2].isdigit():
                    duration = int(parts[2])
                
                protection.mute_user(group_id, mentioned, duration)
                reply_message(event.reply_token, TextMessage(text=f"🔇 تم كتم المستخدم لمدة {duration} دقيقة"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم\n💡 مثال: كتم @المستخدم 30"))
            return
        
        if text.startswith("الغاء كتم ") or text.startswith("الغاء ميوت "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                protection.mute_user(group_id, mentioned, 0)
                reply_message(event.reply_token, TextMessage(text="🔊 تم الغاء الكتم"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        # أوامر الإنذار
        if text.startswith("انذار ") or text.startswith("تحذير "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                if Database.is_admin(mentioned) or Database.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="❌ لا يمكن انذار ادمن او مالك"))
                    return
                
                parts = text.split(maxsplit=2)
                reason = parts[2] if len(parts) > 2 else "مخالفة"
                
                warnings = Database.add_warning(group_id, mentioned, user_id, reason)
                
                if warnings >= 3:
                    kick_user(group_id, mentioned)
                    reply_message(event.reply_token, TextMessage(text=f"⚠️ تم طرد المستخدم بعد {warnings} انذارات"))
                else:
                    reply_message(event.reply_token, TextMessage(text=f"⚠️ تم اعطاء انذار ({warnings}/3)\n📝 السبب: {reason}"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم\n💡 مثال: انذار @المستخدم السبب"))
            return
        
        if text.startswith("حذف انذار ") or text.startswith("مسح انذار "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                Database.clear_warnings(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text="✅ تم حذف جميع الانذارات"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("انذاراتي") or text.startswith("انذارات "):
            if text == "انذاراتي":
                target_id = user_id
            else:
                target_id = extract_user_id(text)
                if not target_id:
                    reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
                    return
            
            warnings = Database.get_warnings(group_id, target_id)
            reply_message(event.reply_token, TextMessage(text=f"⚠️ عدد الانذارات: {warnings}/3"))
            return
        
        # أوامر الطرد
        if text.startswith("طرد ") or text.startswith("كيك "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            mentioned = extract_user_id(text)
            if mentioned:
                if Database.is_admin(mentioned) or Database.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="❌ لا يمكن طرد ادمن او مالك"))
                    return
                
                if kick_user(group_id, mentioned):
                    reply_message(event.reply_token, TextMessage(text="✅ تم طرد المستخدم"))
                else:
                    reply_message(event.reply_token, TextMessage(text="❌ فشل الطرد، تأكد من صلاحيات البوت"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ قم بعمل منشن للمستخدم"))
            return
        
        # أوامر الإعدادات
        if text.startswith("تفعيل "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            setting = text.replace("تفعيل ", "").strip()
            if Database.update_setting(group_id, setting, True):
                reply_message(event.reply_token, TextMessage(text=f"✅ تم تفعيل {setting}"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ خيار غير صحيح\n💡 الخيارات: الروابط، السبام، الفلود، الكلمات، الترحيب، الحماية"))
            return
        
        if text.startswith("تعطيل "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            setting = text.replace("تعطيل ", "").strip()
            if Database.update_setting(group_id, setting, False):
                reply_message(event.reply_token, TextMessage(text=f"✅ تم تعطيل {setting}"))
            else:
                reply_message(event.reply_token, TextMessage(text="❌ خيار غير صحيح\n💡 الخيارات: الروابط، السبام، الفلود، الكلمات، الترحيب، الحماية"))
            return
        
        # عرض الإعدادات
        if text == "الاعدادات" or text == "الإعدادات":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            settings = Database.get_settings(group_id)
            flex = FlexMessage(
                alt_text="إعدادات الحماية",
                contents=FlexContainer.from_dict(FlexUI.settings_card(settings))
            )
            reply_message(event.reply_token, flex)
            return
        
        # عرض الأوامر
        if text == "الاوامر" or text == "الأوامر" or text == "مساعدة":
            flex = FlexMessage(
                alt_text="قائمة الأوامر",
                contents=FlexContainer.from_dict(FlexUI.commands_card(is_admin, is_owner))
            )
            reply_message(event.reply_token, flex)
            return
        
        # قائمة المحظورين
        if text == "المحظورين" or text == "قائمة المحظورين":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="❌ هذا الامر للادمن فقط"))
                return
            
            banned = Database.get_banned_list(group_id)
            flex = FlexMessage(
                alt_text="قائمة المحظورين",
                contents=FlexContainer.from_dict(FlexUI.banned_list_card(banned))
            )
            reply_message(event.reply_token, flex)
            return
        
        # فحص الحماية للرسائل العادية
        if not is_admin:
            settings = Database.get_settings(group_id)
            result = protection.comprehensive_check(group_id, user_id, text, settings)
            
            if result.get('violation'):
                reason = result['reason']
                severity = result['severity']
                
                if severity == 'high':
                    warnings = Database.add_warning(group_id, user_id, "bot", reason)
                    if warnings >= 2:
                        Database.ban_user(group_id, user_id, "bot", reason)
                        kick_user(group_id, user_id)
                        push_message(group_id, TextMessage(text=f"🚫 تم حظر {display_name}\n📝 السبب: {reason}"))
                    else:
                        protection.mute_user(group_id, user_id, 10)
                        push_message(group_id, TextMessage(text=f"⚠️ انذار {display_name} ({warnings}/3)\n🔇 تم الكتم 10 دقائق\n📝 السبب: {reason}"))
                
                elif severity == 'medium':
                    warnings = Database.add_warning(group_id, user_id, "bot", reason)
                    if warnings >= 3:
                        kick_user(group_id, user_id)
                        push_message(group_id, TextMessage(text=f"👋 تم طرد {display_name} بعد 3 انذارات"))
                    else:
                        push_message(group_id, TextMessage(text=f"⚠️ انذار {display_name} ({warnings}/3)\n📝 السبب: {reason}"))
                
                return
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    try:
        group_id = event.source.group_id
        
        for member in event.joined.members:
            user_id = member.user_id
            
            if Database.is_banned(group_id, user_id):
                kick_user(group_id, user_id)
                push_message(group_id, TextMessage(text="🚫 تم طرد مستخدم محظور حاول الدخول"))
                continue
            
            settings = Database.get_settings(group_id)
            if settings.get('welcome', True):
                flex = FlexMessage(
                    alt_text="مرحباً",
                    contents=FlexContainer.from_dict(FlexUI.welcome_card())
                )
                push_message(group_id, flex)
    
    except Exception as e:
        logger.error(f"خطأ في الانضمام: {e}")

@handler.add(JoinEvent)
def handle_join(event):
    try:
        group_id = event.source.group_id
        Database.create_group(group_id)
        
        flex = FlexMessage(
            alt_text="شكراً للإضافة",
            contents=FlexContainer.from_dict(FlexUI.bot_joined_card())
        )
        push_message(group_id, flex)
    
    except Exception as e:
        logger.error(f"خطأ في انضمام البوت: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'protection-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
