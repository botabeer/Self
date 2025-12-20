import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    DB_NAME = 'protection.db'
    _lock = Lock()
    
    @staticmethod
    def init():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                links_protection BOOLEAN DEFAULT 1,
                spam_protection BOOLEAN DEFAULT 1,
                flood_protection BOOLEAN DEFAULT 1,
                bad_words_protection BOOLEAN DEFAULT 1,
                welcome_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS owners (
                user_id TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                user_id TEXT PRIMARY KEY,
                added_by TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS banned_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                banned_by TEXT NOT NULL,
                reason TEXT,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_id, user_id)
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                warned_by TEXT NOT NULL,
                reason TEXT,
                warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                admin_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
            logger.info("تم تهيئة قاعدة البيانات")
        except Exception as e:
            logger.error(f"خطأ تهيئة DB: {e}")
    
    @staticmethod
    def create_group(group_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT OR IGNORE INTO groups (group_id) VALUES (?)''', (group_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ انشاء قروب: {e}")
                return False
    
    @staticmethod
    def is_owner(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM owners WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"خطأ فحص مالك: {e}")
            return False
    
    @staticmethod
    def is_admin(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"خطأ فحص ادمن: {e}")
            return False
    
    @staticmethod
    def add_owner(user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT OR IGNORE INTO owners (user_id) VALUES (?)''', (user_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ اضافة مالك: {e}")
                return False
    
    @staticmethod
    def remove_owner(user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM owners WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ حذف مالك: {e}")
                return False
    
    @staticmethod
    def add_admin(user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT OR IGNORE INTO admins (user_id) VALUES (?)''', (user_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ اضافة ادمن: {e}")
                return False
    
    @staticmethod
    def remove_admin(user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ حذف ادمن: {e}")
                return False
    
    @staticmethod
    def get_owners():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, added_at FROM owners')
            results = cursor.fetchall()
            conn.close()
            return [{'user_id': r[0], 'added_at': r[1]} for r in results]
        except Exception as e:
            logger.error(f"خطأ جلب مالكين: {e}")
            return []
    
    @staticmethod
    def get_admins():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, added_at FROM admins')
            results = cursor.fetchall()
            conn.close()
            return [{'user_id': r[0], 'added_at': r[1]} for r in results]
        except Exception as e:
            logger.error(f"خطأ جلب ادمن: {e}")
            return []
    
    @staticmethod
    def ban_user(group_id, user_id, admin_id, reason):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT OR REPLACE INTO banned_users 
                    (group_id, user_id, banned_by, reason) VALUES (?, ?, ?, ?)''',
                    (group_id, user_id, admin_id, reason))
                conn.commit()
                conn.close()
                
                Database.log_action(group_id, user_id, admin_id, "ban", reason)
                return True
            except Exception as e:
                logger.error(f"خطأ حظر: {e}")
                return False
    
    @staticmethod
    def unban_user(group_id, user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM banned_users WHERE group_id = ? AND user_id = ?',
                    (group_id, user_id))
                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return deleted
            except Exception as e:
                logger.error(f"خطأ الغاء حظر: {e}")
                return False
    
    @staticmethod
    def is_banned(group_id, user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM banned_users WHERE group_id = ? AND user_id = ?',
                (group_id, user_id))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"خطأ فحص حظر: {e}")
            return False
    
    @staticmethod
    def get_banned_users(group_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''SELECT user_id, reason, banned_at 
                FROM banned_users WHERE group_id = ? ORDER BY banned_at DESC''',
                (group_id,))
            results = cursor.fetchall()
            conn.close()
            return [{'user_id': r[0], 'reason': r[1], 'banned_at': r[2]} for r in results]
        except Exception as e:
            logger.error(f"خطأ جلب محظورين: {e}")
            return []
    
    @staticmethod
    def add_warning(group_id, user_id, admin_id, reason):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO warnings (group_id, user_id, warned_by, reason)
                    VALUES (?, ?, ?, ?)''', (group_id, user_id, admin_id, reason))
                
                cursor.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?',
                    (group_id, user_id))
                count = cursor.fetchone()[0]
                
                conn.commit()
                conn.close()
                
                Database.log_action(group_id, user_id, admin_id, "warn", reason)
                return count
            except Exception as e:
                logger.error(f"خطأ انذار: {e}")
                return 0
    
    @staticmethod
    def get_user_warnings(group_id, user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?',
                (group_id, user_id))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"خطأ جلب انذارات: {e}")
            return 0
    
    @staticmethod
    def clear_warnings(group_id, user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM warnings WHERE group_id = ? AND user_id = ?',
                    (group_id, user_id))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ حذف انذارات: {e}")
                return False
    
    @staticmethod
    def cleanup_warnings():
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('DELETE FROM warnings WHERE warned_at < ?', (cutoff,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تنظيف: {e}")
                return False
    
    @staticmethod
    def update_group_settings(group_id, setting, value):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                setting_map = {
                    'links': 'links_protection',
                    'spam': 'spam_protection',
                    'flood': 'flood_protection',
                    'bad_words': 'bad_words_protection',
                    'welcome': 'welcome_enabled'
                }
                
                column = setting_map.get(setting)
                if not column:
                    return False
                
                cursor.execute(f'UPDATE groups SET {column} = ? WHERE group_id = ?',
                    (1 if value else 0, group_id))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تحديث اعدادات: {e}")
                return False
    
    @staticmethod
    def get_group_settings(group_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''SELECT links_protection, spam_protection, flood_protection,
                bad_words_protection, welcome_enabled FROM groups WHERE group_id = ?''',
                (group_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'links': bool(result[0]),
                    'spam': bool(result[1]),
                    'flood': bool(result[2]),
                    'bad_words': bool(result[3]),
                    'welcome': bool(result[4])
                }
            return {
                'links': True,
                'spam': True,
                'flood': True,
                'bad_words': True,
                'welcome': True
            }
        except Exception as e:
            logger.error(f"خطأ جلب اعدادات: {e}")
            return {}
    
    @staticmethod
    def log_action(group_id, user_id, admin_id, action_type, reason):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO action_logs 
                    (group_id, user_id, admin_id, action_type, reason)
                    VALUES (?, ?, ?, ?, ?)''',
                    (group_id, user_id, admin_id, action_type, reason))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تسجيل: {e}")
                return False
    
    @staticmethod
    def get_group_stats(group_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM banned_users WHERE group_id = ?', (group_id,))
            banned_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ?', (group_id,))
            warnings_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM action_logs WHERE group_id = ?', (group_id,))
            actions_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'banned': banned_count,
                'warnings': warnings_count,
                'actions': actions_count
            }
        except Exception as e:
            logger.error(f"خطأ احصائيات: {e}")
            return {}
