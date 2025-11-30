import sqlite3
import os
import time
import threading
import queue
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_locked(max_retries=5, delay=0.2):
    """إعادة المحاولة عند قفل قاعدة البيانات"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() and attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"DB locked, retry {attempt+1}/{max_retries} after {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    logger.error(f"DB failed after {max_retries} retries: {e}")
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ConnectionPool:
    """تجمع الاتصالات لقاعدة البيانات"""
    
    def __init__(self, db_path: str, pool_size: int = 15, timeout: float = 30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._total_connections = 0
        self._initialize_pool()
    
    def _create_connection(self) -> sqlite3.Connection:
        """إنشاء اتصال جديد بقاعدة البيانات"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            isolation_level=None,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-128000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=536870912")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL")
        conn.execute("PRAGMA page_size=4096")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn
    
    def _initialize_pool(self):
        """تهيئة تجمع الاتصالات"""
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn, block=False)
                self._total_connections += 1
            except Exception as e:
                logger.error(f"Failed to create connection: {e}")
    
    @contextmanager
    def get_connection(self):
        """الحصول على اتصال من التجمع"""
        conn = None
        try:
            try:
                conn = self._pool.get(block=True, timeout=5.0)
            except queue.Empty:
                if self._total_connections < self.pool_size * 2:
                    conn = self._create_connection()
                    self._total_connections += 1
                    logger.info(f"Created new connection, total: {self._total_connections}")
                else:
                    raise Exception("Connection pool exhausted")
            yield conn
        except Exception as e:
            logger.error(f"Connection error: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
        finally:
            if conn:
                try:
                    if self._pool.qsize() < self.pool_size:
                        self._pool.put(conn, block=False)
                    else:
                        conn.close()
                        self._total_connections -= 1
                except:
                    try:
                        conn.close()
                        self._total_connections -= 1
                    except:
                        pass
    
    def close_all(self):
        """إغلاق جميع الاتصالات"""
        while not self._pool.empty():
            try:
                conn = self._pool.get(block=False)
                conn.close()
                self._total_connections -= 1
            except:
                pass
        logger.info("All connections closed")


class Database:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_path='botmesh.db'):
        self.db_path = db_path
        self._ensure_clean_db()
        self.pool = ConnectionPool(db_path, pool_size=15)
        self.init_database()
        self._start_maintenance_thread()
        logger.info(f"Database initialized: {db_path}")
    
    def _ensure_clean_db(self):
        """التأكد من نظافة قاعدة البيانات"""
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path, timeout=5)
                conn.execute("SELECT 1")
                conn.close()
            except sqlite3.OperationalError:
                try:
                    os.remove(self.db_path)
                    logger.warning("Removed locked database")
                except Exception as e:
                    logger.error(f"Failed to remove database: {e}")
    
    @retry_on_locked()
    def init_database(self):
        """تهيئة جداول قاعدة البيانات"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    is_registered BOOLEAN DEFAULT 0,
                    is_online BOOLEAN DEFAULT 0,
                    last_online TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) WITHOUT ROWID
            ''')
            
            # جدول تفضيلات المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences(
                    user_id TEXT PRIMARY KEY,
                    theme TEXT DEFAULT 'أبيض',
                    language TEXT DEFAULT 'ar',
                    notifications BOOLEAN DEFAULT 1,
                    last_theme_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) WITHOUT ROWID
            ''')
            
            # جدول جلسات الألعاب
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions(
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT NOT NULL,
                    game_name TEXT NOT NULL,
                    mode TEXT DEFAULT 'solo',
                    team_mode BOOLEAN DEFAULT 0,
                    score INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY(owner_id) REFERENCES users(user_id)
                )
            ''')
            
            # جدول أعضاء الفريق
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_members(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    team_name TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # جدول نقاط الفرق
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_scores(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
                    UNIQUE(session_id, team_name)
                )
            ''')
            
            # جدول إحصائيات الألعاب
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats(
                    user_id TEXT NOT NULL,
                    game_name TEXT NOT NULL,
                    plays INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    avg_score REAL DEFAULT 0.0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(user_id, game_name),
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) WITHOUT ROWID
            ''')
            
            # الفهارس
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC, last_activity DESC)',
                'CREATE INDEX IF NOT EXISTS idx_users_registered ON users(is_registered, points DESC) WHERE is_registered=1',
                'CREATE INDEX IF NOT EXISTS idx_users_online ON users(is_online, last_online DESC) WHERE is_online=1',
                'CREATE INDEX IF NOT EXISTS idx_sessions_owner ON game_sessions(owner_id, started_at DESC)',
                'CREATE INDEX IF NOT EXISTS idx_sessions_active ON game_sessions(completed, started_at DESC) WHERE completed=0',
                'CREATE INDEX IF NOT EXISTS idx_team_members_session ON team_members(session_id, team_name)',
                'CREATE INDEX IF NOT EXISTS idx_game_stats_user ON game_stats(user_id, plays DESC)',
                'CREATE INDEX IF NOT EXISTS idx_game_stats_plays ON game_stats(game_name, plays DESC)'
            ]
            
            for idx in indexes:
                cursor.execute(idx)
            
            cursor.execute("ANALYZE")
            logger.info("Database tables and indexes initialized")
    
    @retry_on_locked()
    def get_user(self, user_id: str) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.*, p.theme, p.language, p.notifications 
                FROM users u 
                LEFT JOIN user_preferences p ON u.user_id = p.user_id 
                WHERE u.user_id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            
            if row:
                user_dict = dict(row)
                if not user_dict.get('theme'):
                    user_dict['theme'] = 'أبيض'
                return user_dict
            return None
    
    @retry_on_locked()
    def create_user(self, user_id: str, name: str) -> bool:
        """إنشاء مستخدم جديد"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            name = name[:50] if name else "مستخدم"
            cursor.execute('''
                INSERT OR IGNORE INTO users(user_id, name, points, is_registered, is_online, last_online, last_activity)
                VALUES(?, ?, 0, 0, 1, ?, ?)
            ''', (user_id, name, now, now))
            cursor.execute("INSERT OR IGNORE INTO user_preferences(user_id, theme) VALUES(?, 'أبيض')", (user_id,))
            return True
    
    @retry_on_locked()
    def update_user(self, user_id: str, **kwargs) -> bool:
        """تحديث بيانات المستخدم"""
        if not kwargs:
            return False
        
        allowed_fields = {'name', 'points', 'is_registered', 'is_online'}
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            fields.append("last_activity = ?")
            values.extend([datetime.now(), user_id])
            query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
            cursor.execute(query, values)
            return True
    
    @retry_on_locked()
    def update_user_name(self, user_id: str, name: str) -> bool:
        """تحديث اسم المستخدم"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET name = ? WHERE user_id = ?', (name[:50], user_id))
            return True
    
    @retry_on_locked()
    def add_points(self, user_id: str, points: int) -> bool:
        """إضافة نقاط للمستخدم"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET points = points + ?, last_activity = ? WHERE user_id = ?
            ''', (points, datetime.now(), user_id))
            return True
    
    @retry_on_locked()
    def update_activity(self, user_id: str) -> bool:
        """تحديث وقت آخر نشاط"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_activity = ? WHERE user_id = ?', (datetime.now(), user_id))
            return True
    
    @retry_on_locked()
    def set_user_online(self, user_id: str, is_online: bool) -> bool:
        """تعيين حالة المستخدم (متصل/غير متصل)"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET is_online = ?, last_online = ? WHERE user_id = ?
            ''', (1 if is_online else 0, datetime.now(), user_id))
            return True
    
    @retry_on_locked()
    def set_user_theme(self, user_id: str, theme: str) -> bool:
        """تعيين ثيم المستخدم"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_preferences(user_id, theme)
                VALUES(?, ?)
                ON CONFLICT(user_id) DO UPDATE SET theme = ?, last_theme_change = ?
            ''', (user_id, theme, theme, datetime.now()))
            return True
    
    @retry_on_locked()
    def get_leaderboard_all(self, limit: int = 20) -> List:
        """الحصول على لوحة الصدارة"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, points, is_registered 
                FROM users 
                WHERE points > 0 
                ORDER BY points DESC, last_activity DESC 
                LIMIT ?
            ''', (limit,))
            return [(row['name'], row['points'], bool(row['is_registered'])) for row in cursor.fetchall()]
    
    @retry_on_locked()
    def create_game_session(self, owner_id: str, game_name: str, mode: str = "solo", team_mode: int = 0) -> int:
        """إنشاء جلسة لعبة جديدة"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_sessions(owner_id, game_name, mode, team_mode, started_at)
                VALUES(?, ?, ?, ?, ?)
            ''', (owner_id, game_name, mode, team_mode, datetime.now()))
            return cursor.lastrowid
    
    @retry_on_locked()
    def finish_session(self, session_id: int, score: int) -> bool:
        """إنهاء جلسة اللعبة"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE game_sessions SET completed = 1, score = ?, completed_at = ? WHERE session_id = ?
            ''', (score, datetime.now(), session_id))
            return True
    
    @retry_on_locked()
    def add_team_member(self, session_id: int, user_id: str, team_name: str) -> bool:
        """إضافة عضو للفريق"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO team_members(session_id, user_id, team_name)
                VALUES(?, ?, ?)
            ''', (session_id, user_id, team_name))
            cursor.execute('''
                INSERT OR IGNORE INTO team_scores(session_id, team_name, score)
                VALUES(?, ?, 0)
            ''', (session_id, team_name))
            return True
    
    @retry_on_locked()
    def add_team_points(self, session_id: int, team_name: str, points: int) -> bool:
        """إضافة نقاط للفريق"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE team_scores SET score = score + ?, updated_at = ? 
                WHERE session_id = ? AND team_name = ?
            ''', (points, datetime.now(), session_id, team_name))
            return True
    
    @retry_on_locked()
    def get_team_points(self, session_id: int) -> Dict[str, int]:
        """الحصول على نقاط الفرق"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT team_name, score FROM team_scores WHERE session_id = ?
            ''', (session_id,))
            return {row['team_name']: row['score'] for row in cursor.fetchall()}
    
    @retry_on_locked()
    def record_game_stat(self, user_id: str, game_name: str, score: int, won: bool = False) -> bool:
        """تسجيل إحصائيات اللعبة"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_stats(user_id, game_name, plays, wins, total_score, best_score, last_played)
                VALUES(?, ?, 1, ?, ?, ?, ?)
                ON CONFLICT(user_id, game_name) DO UPDATE SET 
                    plays = plays + 1,
                    wins = wins + ?,
                    total_score = total_score + ?,
                    best_score = MAX(best_score, ?),
                    avg_score = CAST(total_score + ? AS REAL) / (plays + 1),
                    last_played = ?
            ''', (user_id, game_name, 1 if won else 0, score, score, datetime.now(),
                  1 if won else 0, score, score, score, datetime.now()))
            return True
    
    @retry_on_locked()
    def get_user_game_stats(self, user_id: str) -> Dict:
        """الحصول على إحصائيات ألعاب المستخدم"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_name, plays, wins, total_score, best_score, avg_score 
                FROM game_stats 
                WHERE user_id = ? 
                ORDER BY plays DESC
            ''', (user_id,))
            return {row['game_name']: dict(row) for row in cursor.fetchall()}
    
    @retry_on_locked()
    def get_top_games(self, limit: int = 12) -> List[str]:
        """الحصول على الألعاب الأكثر استخداماً"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_name, SUM(plays) as total_plays 
                FROM game_stats 
                GROUP BY game_name 
                ORDER BY total_plays DESC 
                LIMIT ?
            ''', (limit,))
            return [row['game_name'] for row in cursor.fetchall()]
    
    @retry_on_locked()
    def get_stats_summary(self) -> Dict:
        """الحصول على ملخص الإحصائيات"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM users')
            total_users = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_registered = 1')
            registered_users = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM game_sessions')
            total_sessions = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM game_sessions WHERE completed = 1')
            completed_sessions = cursor.fetchone()['count']
            
            return {
                'total_users': total_users,
                'registered_users': registered_users,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions
            }
    
    @retry_on_locked()
    def cleanup_inactive_users(self, days: int = 90) -> int:
        """تنظيف المستخدمين غير النشطين"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cutoff = datetime.now() - timedelta(days=days)
            cursor.execute('''
                DELETE FROM users 
                WHERE last_activity < ? AND points = 0 AND is_registered = 0
            ''', (cutoff,))
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} inactive users")
            return deleted
    
    def _start_maintenance_thread(self):
        """بدء مهمة الصيانة الدورية"""
        def maintenance_worker():
            while True:
                try:
                    time.sleep(3600)  # كل ساعة
                    self._perform_maintenance()
                except Exception as e:
                    logger.error(f"Maintenance error: {e}")
        
        thread = threading.Thread(target=maintenance_worker, daemon=True)
        thread.start()
    
    @retry_on_locked()
    def _perform_maintenance(self):
        """تنفيذ صيانة دورية"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA incremental_vacuum(100)")
            cursor.execute("ANALYZE")
            
            old_date = datetime.now() - timedelta(days=7)
            cursor.execute('''
                DELETE FROM game_sessions 
                WHERE completed = 1 AND completed_at < ?
            ''', (old_date,))
            
            logger.info("Periodic maintenance completed")
    
    def close(self):
        """إغلاق قاعدة البيانات"""
        self.pool.close_all()
        logger.info("Database closed")


_db_instance = None
_db_lock = threading.Lock()


def get_database() -> Database:
    """الحصول على نسخة واحدة من قاعدة البيانات"""
    global _db_instance
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = Database()
    return _db_instance


__all__ = ['Database', 'get_database']
