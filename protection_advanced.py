import re
import time
from datetime import datetime, timedelta
from threading import Lock
from database import Database
import logging
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

class AdvancedProtection:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.lock = Lock()
        
        # تتبع الرسائل
        self.user_messages = defaultdict(list)
        self.message_hashes = defaultdict(set)
        self.join_times = {}
        
        # الكتم والحظر المؤقت
        self.muted_users = {}
        self.temp_restricted = {}
        
        # كلمات محظورة موسعة
        self.bad_words = [
            'غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل',
            'خائن', 'كذاب', 'لعين', 'ملعون', 'عاهر', 'زاني', 'فاسق', 'منافق',
            'حيوان', 'قرد', 'بهيمة', 'ابن', 'بنت', 'كس', 'عرص', 'زبي', 'نيك',
            'متناك', 'شرموط', 'قحبة', 'عاهرة'
        ]
        
        # انماط محظورة
        self.blocked_patterns = [
            r'http[s]?://(?:www\.)?(?:t\.me|line\.me|telegram\.org)',
            r'@[a-zA-Z0-9_]{5,}',
            r'\d{10,}',
            r'bit\.ly|tinyurl|shorturl',
        ]
    
    def normalize_text(self, text):
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def check_new_member_spam(self, group_id, user_id):
        """فحص سبام الاعضاء الجدد"""
        key = f"{group_id}:{user_id}"
        if key in self.join_times:
            join_time = self.join_times[key]
            if datetime.now() - join_time < timedelta(minutes=5):
                return True, "عضو جديد يحاول السبام"
        return False, None
    
    def check_rapid_messages(self, group_id, user_id):
        """فحص الرسائل السريعة المتتالية"""
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
            count = len(self.user_messages[key])
            
            if count > 5:
                return True, f"فلود {count} رسائل في 10 ثواني"
            elif count > 3:
                return True, "رسائل سريعة متتالية"
            
            return False, None
    
    def check_duplicate_content(self, group_id, user_id, text):
        """فحص المحتوى المكرر"""
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
        """فحص الروابط المحظورة"""
        patterns = [
            r'http[s]?://',
            r'www\.',
            r't\.me',
            r'line\.me',
            r'bit\.ly',
            r'tinyurl',
            r'shorturl',
            r'cutt\.ly',
            r'tiny\.cc',
            r'\w+\.(com|net|org|me|co|info|tv|cc|ly)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "رابط محظور"
        
        return False, None
    
    def check_mentions(self, text):
        """فحص المنشنات الزائدة"""
        mentions = re.findall(r'@\w+', text)
        if len(mentions) > 3:
            return True, f"منشنات زائدة ({len(mentions)})"
        return False, None
    
    def check_phone_numbers(self, text):
        """فحص ارقام الهاتف"""
        phones = re.findall(r'\d{10,}', text)
        if phones:
            return True, "رقم هاتف محظور"
        return False, None
    
    def check_bad_words(self, text):
        """فحص الكلمات السيئة"""
        normalized = self.normalize_text(text)
        
        for word in self.bad_words:
            norm_word = self.normalize_text(word)
            if norm_word in normalized:
                return True, f"كلمة غير لائقة: {word}"
        
        return False, None
    
    def check_caps_spam(self, text):
        """فحص الاحرف الكبيرة الزائدة"""
        if len(text) > 20:
            caps_count = sum(1 for c in text if c.isupper())
            caps_ratio = caps_count / len(text)
            
            if caps_ratio > 0.7:
                return True, "احرف كبيرة زائدة"
        
        return False, None
    
    def check_repeated_chars(self, text):
        """فحص الاحرف المتكررة"""
        repeated = re.findall(r'(.)\1{5,}', text)
        if repeated:
            return True, "احرف متكررة زائدة"
        
        return False, None
    
    def check_emoji_spam(self, text):
        """فحص سبام الايموجي"""
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        emojis = emoji_pattern.findall(text)
        if len(emojis) > 10:
            return True, f"ايموجي زائد ({len(emojis)})"
        
        return False, None
    
    def check_long_message(self, text):
        """فحص الرسائل الطويلة"""
        if len(text) > 1000:
            return True, "رسالة طويلة جدا"
        
        lines = text.split('\n')
        if len(lines) > 20:
            return True, "اسطر كثيرة جدا"
        
        return False, None
    
    def check_arabic_english_mix(self, text):
        """فحص خلط العربي والانجليزي المشبوه"""
        arabic = re.findall(r'[\u0600-\u06FF]', text)
        english = re.findall(r'[a-zA-Z]', text)
        
        if len(arabic) > 0 and len(english) > 0:
            if len(english) > len(arabic) * 2:
                return True, "نص مشبوه"
        
        return False, None
    
    def check_invite_links(self, text):
        """فحص روابط الدعوة"""
        invite_patterns = [
            r'join',
            r'invite',
            r'انضم',
            r'دعوة',
            r'group',
            r'قروب',
            r'جروب'
        ]
        
        has_link = any(pattern in text.lower() for pattern in [
            'http', 'www', 't.me', 'line.me'
        ])
        
        has_invite = any(pattern in text.lower() for pattern in invite_patterns)
        
        if has_link and has_invite:
            return True, "رابط دعوة محظور"
        
        return False, None
    
    def comprehensive_check(self, group_id, user_id, text, display_name, is_new_member=False):
        """فحص شامل للرسالة"""
        
        if is_new_member:
            is_spam, reason = self.check_new_member_spam(group_id, user_id)
            if is_spam:
                return {
                    'violation': True,
                    'reason': reason,
                    'action': 'kick',
                    'severity': 'high'
                }
        
        checks = [
            self.check_rapid_messages(group_id, user_id),
            self.check_duplicate_content(group_id, user_id, text),
            self.check_links(text),
            self.check_mentions(text),
            self.check_phone_numbers(text),
            self.check_bad_words(text),
            self.check_caps_spam(text),
            self.check_repeated_chars(text),
            self.check_emoji_spam(text),
            self.check_long_message(text),
            self.check_invite_links(text)
        ]
        
        for is_violation, reason in checks:
            if is_violation:
                severity = self.determine_severity(reason)
                action = self.determine_action(severity, group_id, user_id)
                
                return {
                    'violation': True,
                    'reason': reason,
                    'action': action,
                    'severity': severity,
                    'user': display_name
                }
        
        return {'violation': False}
    
    def determine_severity(self, reason):
        """تحديد شدة المخالفة"""
        high_severity = [
            'رابط دعوة', 'رقم هاتف', 'كلمة غير لائقة',
            'سبام', 'فلود'
        ]
        
        for keyword in high_severity:
            if keyword in reason:
                return 'high'
        
        if 'زائد' in reason or 'متكرر' in reason:
            return 'medium'
        
        return 'low'
    
    def determine_action(self, severity, group_id, user_id):
        """تحديد الاجراء المناسب"""
        warnings = Database.get_user_warnings(group_id, user_id)
        
        if severity == 'high':
            if warnings >= 2:
                return 'ban'
            elif warnings >= 1:
                return 'kick'
            else:
                return 'warn_mute'
        
        elif severity == 'medium':
            if warnings >= 3:
                return 'kick'
            else:
                return 'warn'
        
        else:
            return 'warn'
    
    def register_new_member(self, group_id, user_id):
        """تسجيل عضو جديد"""
        key = f"{group_id}:{user_id}"
        self.join_times[key] = datetime.now()
    
    def mute_user(self, group_id, user_id, duration_minutes):
        """كتم مستخدم"""
        with self.lock:
            key = f"{group_id}:{user_id}"
            expire_time = datetime.now() + timedelta(minutes=duration_minutes)
            self.muted_users[key] = expire_time
            return True
    
    def is_muted(self, group_id, user_id):
        """فحص اذا المستخدم مكتوم"""
        with self.lock:
            key = f"{group_id}:{user_id}"
            if key in self.muted_users:
                if datetime.now() < self.muted_users[key]:
                    return True
                else:
                    del self.muted_users[key]
            return False
    
    def cleanup_old_data(self):
        """تنظيف البيانات القديمة"""
        with self.lock:
            current_time = time.time()
            
            for key in list(self.user_messages.keys()):
                self.user_messages[key] = [
                    t for t in self.user_messages[key]
                    if current_time - t < 60
                ]
                
                if not self.user_messages[key]:
                    del self.user_messages[key]
            
            for key in list(self.join_times.keys()):
                if datetime.now() - self.join_times[key] > timedelta(hours=1):
                    del self.join_times[key]
            
            for key in list(self.muted_users.keys()):
                if datetime.now() >= self.muted_users[key]:
                    del self.muted_users[key]
