import re
import time
from datetime import datetime, timedelta
from threading import Lock
from database import Database
import logging

logger = logging.getLogger(__name__)

class ProtectionManager:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.muted_users = {}
        self.user_messages = {}
        self.lock = Lock()
        
        self.bad_words = [
            'غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل',
            'خائن', 'كذاب', 'لعين', 'ملعون', 'عاهر', 'زاني', 'فاسق', 'منافق',
            'حيوان', 'قرد', 'بهيمة', 'ابن', 'بنت'
        ]
    
    def init_group(self, group_id):
        Database.create_group(group_id)
    
    def normalize_text(self, text):
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        return text
    
    def check_links(self, text):
        patterns = [
            r'http[s]?://',
            r'www\.',
            r't\.me',
            r'line\.me',
            r'bit\.ly',
            r'tinyurl',
            r'\w+\.(com|net|org|me|co|info|tv)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def check_bad_words(self, text):
        normalized = self.normalize_text(text)
        
        for word in self.bad_words:
            norm_word = self.normalize_text(word)
            if norm_word in normalized:
                return True
        return False
    
    def check_spam(self, text):
        if len(text) > 500:
            return True
        
        if text.count('\n') > 10:
            return True
        
        repeated_chars = re.findall(r'(.)\1{4,}', text)
        if repeated_chars:
            return True
        
        return False
    
    def check_flood(self, group_id, user_id):
        with self.lock:
            key = f"{group_id}:{user_id}"
            current_time = time.time()
            
            if key not in self.user_messages:
                self.user_messages[key] = []
            
            self.user_messages[key] = [
                t for t in self.user_messages[key] 
                if current_time - t < 10
            ]
            
            self.user_messages[key].append(current_time)
            
            return len(self.user_messages[key]) > 5
    
    def check_message(self, group_id, user_id, text, display_name):
        settings = self.get_settings(group_id)
        
        if settings.get('links', True):
            if self.check_links(text):
                self.warn_user(group_id, user_id, "bot", "ارسال روابط")
                return f"تحذير {display_name}\nممنوع ارسال الروابط"
        
        if settings.get('bad_words', True):
            if self.check_bad_words(text):
                self.warn_user(group_id, user_id, "bot", "استخدام كلمات غير لائقة")
                return f"تحذير {display_name}\nممنوع الكلمات غير اللائقة"
        
        if settings.get('spam', True):
            if self.check_spam(text):
                self.warn_user(group_id, user_id, "bot", "سبام")
                return f"تحذير {display_name}\nممنوع السبام"
        
        if settings.get('flood', True):
            if self.check_flood(group_id, user_id):
                self.mute_user(group_id, user_id, 5)
                return f"تم كتم {display_name} لمدة 5 دقائق\nالسبب: فلود"
        
        return None
    
    def ban_user(self, group_id, user_id, admin_id, reason):
        return Database.ban_user(group_id, user_id, admin_id, reason)
    
    def unban_user(self, group_id, user_id):
        return Database.unban_user(group_id, user_id)
    
    def is_banned(self, group_id, user_id):
        return Database.is_banned(group_id, user_id)
    
    def get_banned_users(self, group_id):
        return Database.get_banned_users(group_id)
    
    def mute_user(self, group_id, user_id, duration_minutes):
        with self.lock:
            key = f"{group_id}:{user_id}"
            expire_time = datetime.now() + timedelta(minutes=duration_minutes)
            self.muted_users[key] = expire_time
            
            Database.log_action(
                group_id, user_id, "bot", "mute",
                f"مكتوم لمدة {duration_minutes} دقيقة"
            )
            return True
    
    def unmute_user(self, group_id, user_id):
        with self.lock:
            key = f"{group_id}:{user_id}"
            if key in self.muted_users:
                del self.muted_users[key]
                return True
            return False
    
    def is_muted(self, group_id, user_id):
        with self.lock:
            key = f"{group_id}:{user_id}"
            if key in self.muted_users:
                if datetime.now() < self.muted_users[key]:
                    return True
                else:
                    del self.muted_users[key]
            return False
    
    def cleanup_temp_bans(self):
        with self.lock:
            current_time = datetime.now()
            expired = [
                key for key, expire_time in self.muted_users.items()
                if current_time >= expire_time
            ]
            for key in expired:
                del self.muted_users[key]
    
    def warn_user(self, group_id, user_id, admin_id, reason):
        return Database.add_warning(group_id, user_id, admin_id, reason)
    
    def clear_warnings(self, group_id, user_id):
        return Database.clear_warnings(group_id, user_id)
    
    def get_user_warnings(self, group_id, user_id):
        return Database.get_user_warnings(group_id, user_id)
    
    def update_settings(self, group_id, setting_name, value):
        return Database.update_group_settings(group_id, setting_name, value)
    
    def get_settings(self, group_id):
        return Database.get_group_settings(group_id)
    
    def get_group_stats(self, group_id):
        return Database.get_group_stats(group_id)
