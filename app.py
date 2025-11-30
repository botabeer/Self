import os, sys, logging, threading, time, traceback
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from constants import (BOT_NAME, BOT_VERSION, BOT_RIGHTS, LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, 
                       validate_env, get_username, GAME_LIST, DEFAULT_THEME, PRIVACY_SETTINGS, 
                       is_allowed_command, GAME_COMMANDS, get_game_class_name)
from ui_builder import (build_games_menu, build_my_points, build_leaderboard, build_registration_status, 
                        build_winner_announcement, build_help_window, build_theme_selector, build_enhanced_home, 
                        attach_quick_reply, build_error_message, build_game_stopped, build_team_game_end, 
                        build_unregister_confirmation, build_registration_required)
from database import get_database

try:
    validate_env()
except Exception as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger("botmesh")
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
db = get_database()

active_games = {}
game_timers = {}
session_meta = {}
team_mode_state = {}
RATE_LIMIT = {"max_requests": 30, "window_seconds": 60}
user_rate = defaultdict(list)
session_locks = {}
session_lock_main = threading.Lock()


class LRUCache:
    def __init__(self, capacity=1000):
        self.cache = {}
        self.capacity = capacity
        self.order = []
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.order.remove(key)
                self.order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.order.remove(key)
            elif len(self.cache) >= self.capacity:
                oldest = self.order.pop(0)
                del self.cache[oldest]
            self.cache[key] = value
            self.order.append(key)
    
    def remove(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.order.remove(key)


user_cache = LRUCache(capacity=1000)


def get_session_lock(game_id):
    with session_lock_main:
        if game_id not in session_locks:
            session_locks[game_id] = threading.Lock()
        return session_locks[game_id]


def is_rate_limited(user_id):
    now = datetime.utcnow()
    window = timedelta(seconds=RATE_LIMIT["window_seconds"])
    user_rate[user_id] = [t for t in user_rate[user_id] if now - t < window]
    if len(user_rate[user_id]) >= RATE_LIMIT["max_requests"]:
        logger.warning(f"Rate limit exceeded for user: {user_id}")
        return True
    user_rate[user_id].append(now)
    return False


AVAILABLE_GAMES = {}
try:
    from games.iq_game import IqGame
    from games.math_game import MathGame
    from games.word_color_game import WordColorGame
    from games.scramble_word_game import ScrambleWordGame
    from games.fast_typing_game import FastTypingGame
    from games.opposite_game import OppositeGame
    from games.letters_words_game import LettersWordsGame
    from games.song_game import SongGame
    from games.human_animal_plant_game import HumanAnimalPlantGame
    from games.chain_words_game import ChainWordsGame
    from games.guess_game import GuessGame
    from games.compatibility_game import CompatibilitySystem
    
    AVAILABLE_GAMES = {
        "ذكاء": IqGame,
        "رياضيات": MathGame,
        "لون": WordColorGame,
        "ترتيب": ScrambleWordGame,
        "أسرع": FastTypingGame,
        "ضد": OppositeGame,
        "تكوين": LettersWordsGame,
        "أغنيه": SongGame,
        "لعبة": HumanAnimalPlantGame,
        "سلسلة": ChainWordsGame,
        "خمن": GuessGame,
        "توافق": CompatibilitySystem
    }
    logger.info(f"Loaded {len(AVAILABLE_GAMES)} games successfully")
except Exception as e:
    logger.error(f"Error loading games: {e}")
    logger.error(traceback.format_exc())


def ensure_session_meta(game_id):
    if game_id not in session_meta:
        session_meta[game_id] = {
            "session_id": None,
            "team_mode": False,
            "current_game_name": None,
            "session_type": "solo",
            "start_time": time.time()
        }
    return session_meta[game_id]


def launch_game_instance(game_id, owner_id, game_class_name, line_api, theme=None, team_mode=False, source_type="user"):
    if game_class_name not in AVAILABLE_GAMES:
        raise ValueError(f"Game not available: {game_class_name}")
    
    GameClass = AVAILABLE_GAMES[game_class_name]
    game_instance = GameClass(line_api)
    
    try:
        if hasattr(game_instance, 'set_theme') and theme:
            game_instance.set_theme(theme)
    except Exception as e:
        logger.error(f"Failed to set theme: {e}")
    
    try:
        if hasattr(game_instance, 'set_database'):
            game_instance.set_database(db)
        else:
            game_instance.db = db
    except Exception as e:
        logger.warning(f"Failed to link database: {e}")
    
    if team_mode:
        game_instance.team_mode = True
        game_instance.supports_hint = False
        game_instance.supports_reveal = False
        game_instance.session_type = "teams"
    else:
        game_instance.team_mode = False
        game_instance.session_type = "solo" if source_type == "user" else "group"
    
    active_games[game_id] = game_instance
    meta = ensure_session_meta(game_id)
    meta["current_game_name"] = game_class_name
    meta["team_mode"] = team_mode
    meta["session_type"] = game_instance.session_type
    
    if game_class_name != "توافق":
        session_id = db.create_game_session(
            owner_id, 
            game_class_name, 
            mode=game_instance.session_type, 
            team_mode=1 if team_mode else 0
        )
        meta["session_id"] = session_id
    
    logger.info(f"Launched game: {game_class_name} | Mode: {'teams' if team_mode else 'solo'}")
    return game_instance


def get_user_data(user_id, username="مستخدم"):
    cached = user_cache.get(user_id)
    if cached:
        cache_time = cached.get('_cache_time', datetime.min)
        if datetime.utcnow() - cache_time < timedelta(minutes=PRIVACY_SETTINGS["cache_timeout_minutes"]):
            if cached.get('name') != username:
                db.update_user_name(user_id, username)
                cached['name'] = username
            return cached
    
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id, username)
        user = db.get_user(user_id)
        logger.info(f"New user created: {username}")
    else:
        if user.get('name') != username:
            db.update_user_name(user_id, username)
            user['name'] = username
    
    user['_cache_time'] = datetime.utcnow()
    user_cache.put(user_id, user)
    return user


def handle_game_answer(game_id, result, user_id, meta):
    pts = result.get('points', 0)
    if pts > 0:
        if meta.get("team_mode"):
            team_name = result.get('team', 'team1')
            db.add_team_points(meta["session_id"], team_name, 1)
        else:
            db.add_points(user_id, 1)
            game_name = meta.get("current_game_name", "unknown")
            db.record_game_stat(user_id, game_name, 1, result.get('game_over', False))
    return pts


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Handler error: {e}")
        logger.error(traceback.format_exc())
        abort(500)
    return "OK"


@app.route("/", methods=['GET'])
def status_page():
    stats = db.get_stats_summary()
    return f"""<html><head><title>{BOT_NAME}</title><style>body{{font-family:'Segoe UI',sans-serif;padding:40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;}}.container{{max-width:800px;margin:0 auto;background:rgba(255,255,255,0.95);padding:40px;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,0.3);color:#333;}}h1{{color:#667eea;margin:0 0 10px;font-size:2.5em;}}.version{{color:#999;margin-bottom:30px;}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:30px 0;}}.stat-card{{background:#f8f9fa;padding:20px;border-radius:15px;text-align:center;border:2px solid #e9ecef;}}.stat-value{{font-size:2em;font-weight:bold;color:#667eea;margin:10px 0;}}.stat-label{{color:#666;font-size:0.9em;text-transform:uppercase;}}.footer{{margin-top:30px;padding-top:20px;border-top:2px solid #e9ecef;text-align:center;color:#999;font-size:0.85em;}}</style></head><body><div class="container"><h1>{BOT_NAME}</h1><div class="version">Version {BOT_VERSION}</div><div class="stats"><div class="stat-card"><div class="stat-label">Active Games</div><div class="stat-value">{len(active_games)}</div></div><div class="stat-card"><div class="stat-label">Available Games</div><div class="stat-value">{len(AVAILABLE_GAMES)}</div></div><div class="stat-card"><div class="stat-label">Total Users</div><div class="stat-value">{stats.get('total_users',0)}</div></div><div class="stat-card"><div class="stat-label">Registered Users</div><div class="stat-value">{stats.get('registered_users',0)}</div></div><div class="stat-card"><div class="stat-label">Total Sessions</div><div class="stat-value">{stats.get('total_sessions',0)}</div></div></div><div class="footer">{BOT_RIGHTS}</div></div></body></html>"""


@app.route("/health", methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "version": BOT_VERSION,
        "active_games": len(active_games),
        "available_games": len(AVAILABLE_GAMES)
    })


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text.strip()
        
        if not text:
            return
        
        in_group = hasattr(event.source, 'group_id')
        game_id = event.source.group_id if in_group else user_id
        is_command = is_allowed_command(text)
        is_game_active = game_id in active_games
        
        if not is_command and not is_game_active:
            return
        
        if is_rate_limited(user_id):
            return
        
        lock = get_session_lock(game_id)
        
        with lock:
            source_type = "group" if in_group else "user"
            
            with ApiClient(configuration) as api_client:
                line_api = MessagingApi(api_client)
                
                try:
                    profile = line_api.get_profile(user_id)
                    username = get_username(profile)
                except:
                    username = "مستخدم"
                
                user = get_user_data(user_id, username)
                db.update_activity(user_id)
                db.set_user_online(user_id, True)
                
                current_theme = user.get("theme") or DEFAULT_THEME
                lowered = text.lower()
                reply_message = None
                
                # معالجة الأوامر
                if lowered in ["مساعدة", "help"]:
                    reply_message = build_help_window(current_theme)
                
                elif lowered in ["بداية", "home", "الرئيسية", "start"]:
                    current_mode = team_mode_state.get(game_id, False)
                    mode_label = "فريقين" if current_mode else "فردي"
                    reply_message = build_enhanced_home(
                        username, 
                        user['points'], 
                        user.get('is_registered'), 
                        current_theme, 
                        mode_label
                    )
                
                elif lowered in ["ألعاب", "games", "العاب"]:
                    top_games = db.get_top_games(12)
                    reply_message = build_games_menu(current_theme, top_games)
                
                elif lowered in ["نقاطي", "points", "نقاط"]:
                    stats = db.get_user_game_stats(user_id)
                    reply_message = build_my_points(username, user['points'], stats, current_theme)
                
                elif lowered in ["صدارة", "leaderboard", "مستوى"]:
                    top = db.get_leaderboard_all(20)
                    reply_message = build_leaderboard(top, current_theme)
                
                elif lowered in ["انضم", "join", "تسجيل"]:
                    if not user.get('is_registered'):
                        db.update_user(user_id, is_registered=1)
                        user_cache.remove(user_id)
                        user = get_user_data(user_id, username)
                        logger.info(f"User registered: {username}")
                    reply_message = build_registration_status(username, user['points'], current_theme)
                
                elif lowered in ["انسحب", "leave", "خروج"]:
                    if user.get('is_registered'):
                        db.update_user(user_id, is_registered=0)
                        user_cache.remove(user_id)
                        user = get_user_data(user_id, username)
                        logger.info(f"User unregistered: {username}")
                        reply_message = build_unregister_confirmation(username, user['points'], current_theme)
                    else:
                        return
                
                elif lowered in ["فريقين", "teams", "فرق", "فردي", "solo"]:
                    if in_group:
                        current = team_mode_state.get(game_id, False)
                        team_mode_state[game_id] = not current
                        new_mode = team_mode_state[game_id]
                        mode_label = "فريقين" if new_mode else "فردي"
                        reply_message = TextMessage(text=f"تم التبديل إلى وضع {mode_label}")
                    else:
                        return
                
                elif lowered.startswith("ثيم "):
                    theme_name = text.replace("ثيم ", "").strip()
                    from constants import THEMES
                    if theme_name in THEMES:
                        db.set_user_theme(user_id, theme_name)
                        user_cache.remove(user_id)
                        user = get_user_data(user_id, username)
                        current_mode = team_mode_state.get(game_id, False)
                        mode_label = "فريقين" if current_mode else "فردي"
                        reply_message = build_enhanced_home(
                            username, 
                            user['points'], 
                            user.get('is_registered'), 
                            theme_name, 
                            mode_label
                        )
                    else:
                        reply_message = build_theme_selector(current_theme)
                
                elif lowered in ["ثيمات", "themes", "مظهر"]:
                    reply_message = build_theme_selector(current_theme)
                
                elif lowered in ["إيقاف", "stop", "انهاء"]:
                    if game_id in active_games:
                        game_name = session_meta.get(game_id, {}).get("current_game_name", "اللعبة")
                        del active_games[game_id]
                        session_meta.pop(game_id, None)
                        reply_message = build_game_stopped(game_name, current_theme)
                    else:
                        return
                
                elif text in GAME_COMMANDS:
                    game_class_name = get_game_class_name(text)
                    
                    if game_class_name == "توافق":
                        try:
                            game_instance = launch_game_instance(
                                game_id, user_id, game_class_name, line_api, current_theme, False, source_type
                            )
                            start_msg = game_instance.start_game()
                            attach_quick_reply(start_msg)
                            line_api.reply_message(
                                ReplyMessageRequest(reply_token=event.reply_token, messages=[start_msg])
                            )
                            return
                        except Exception as e:
                            logger.error(f"Error starting compatibility: {e}")
                            logger.error(traceback.format_exc())
                            return
                    
                    elif not user.get('is_registered'):
                        reply_message = build_registration_required(current_theme)
                    
                    else:
                        meta = ensure_session_meta(game_id)
                        team_mode = team_mode_state.get(game_id, False)
                        
                        try:
                            game_instance = launch_game_instance(
                                game_id, user_id, game_class_name, line_api, current_theme, team_mode, source_type
                            )
                            
                            if team_mode:
                                logger.info(f"Team mode active for game {game_class_name}")
                            
                            start_msg = game_instance.start_game()
                            attach_quick_reply(start_msg)
                            line_api.reply_message(
                                ReplyMessageRequest(reply_token=event.reply_token, messages=[start_msg])
                            )
                            return
                        except Exception as e:
                            logger.error(f"Error starting game: {e}")
                            logger.error(traceback.format_exc())
                            return
                
                elif game_id in active_games:
                    meta = ensure_session_meta(game_id)
                    is_compatibility = meta.get("current_game_name") == "توافق"
                    
                    if is_compatibility:
                        game_instance = active_games[game_id]
                        try:
                            result = game_instance.check_answer(text, user_id, username)
                            if not result:
                                return
                            
                            if result.get('game_over'):
                                if result.get('response'):
                                    response_msg = result['response']
                                    attach_quick_reply(response_msg)
                                    line_api.reply_message(
                                        ReplyMessageRequest(reply_token=event.reply_token, messages=[response_msg])
                                    )
                                del active_games[game_id]
                                session_meta.pop(game_id, None)
                                return
                            else:
                                if result.get('response'):
                                    response_msg = result['response']
                                    attach_quick_reply(response_msg)
                                    line_api.reply_message(
                                        ReplyMessageRequest(reply_token=event.reply_token, messages=[response_msg])
                                    )
                                    return
                        except Exception as e:
                            logger.error(f"Error in check_answer: {e}")
                            logger.error(traceback.format_exc())
                            if game_id in active_games:
                                del active_games[game_id]
                            return
                    
                    else:
                        if not user.get('is_registered'):
                            return
                        
                        game_instance = active_games[game_id]
                        try:
                            result = game_instance.check_answer(text, user_id, username)
                            if not result:
                                return
                            
                            pts = handle_game_answer(game_id, result, user_id, meta)
                            
                            if result.get('game_over'):
                                if meta.get("session_id"):
                                    db.finish_session(meta["session_id"], pts)
                                
                                if meta.get("team_mode"):
                                    team_pts = db.get_team_points(meta["session_id"])
                                    reply_message = build_team_game_end(team_pts, current_theme)
                                else:
                                    reply_message = build_winner_announcement(
                                        username, 
                                        meta.get("current_game_name", "اللعبة"), 
                                        pts, 
                                        user['points'] + pts, 
                                        current_theme
                                    )
                                
                                del active_games[game_id]
                                session_meta.pop(game_id, None)
                            else:
                                if result.get('response'):
                                    response_msg = result['response']
                                    attach_quick_reply(response_msg)
                                    line_api.reply_message(
                                        ReplyMessageRequest(reply_token=event.reply_token, messages=[response_msg])
                                    )
                                    return
                                else:
                                    return
                        except Exception as e:
                            logger.error(f"Error in check_answer: {e}")
                            logger.error(traceback.format_exc())
                            if game_id in active_games:
                                del active_games[game_id]
                            return
                else:
                    return
                
                if reply_message:
                    attach_quick_reply(reply_message)
                    line_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply_message])
                    )
    
    except Exception as e:
        logger.error(f"General error in handle_message: {e}")
        logger.error(traceback.format_exc())


def periodic_cleanup():
    def _cleanup():
        while True:
            try:
                cleanup_hours = PRIVACY_SETTINGS["cleanup_interval_hours"]
                time.sleep(cleanup_hours * 3600)
                
                now = datetime.utcnow()
                timeout_minutes = PRIVACY_SETTINGS["cache_timeout_minutes"]
                current_time = time.time()
                old_sessions = []
                
                for gid, meta in list(session_meta.items()):
                    start_time = meta.get('start_time', 0)
                    if (gid not in active_games and start_time > 0 and current_time - start_time > 3600):
                        old_sessions.append(gid)
                
                for gid in old_sessions:
                    session_meta.pop(gid, None)
                
                if old_sessions:
                    logger.info(f"Cleaned {len(old_sessions)} old sessions")
                
                delete_days = PRIVACY_SETTINGS["auto_delete_inactive_days"]
                deleted = db.cleanup_inactive_users(delete_days)
                
                if deleted > 0:
                    logger.info(f"Deleted {deleted} inactive users")
                
                logger.info("Periodic cleanup completed")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    t = threading.Thread(target=_cleanup, daemon=True)
    t.start()


periodic_cleanup()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info("=" * 70)
    logger.info(f"{BOT_NAME} v{BOT_VERSION}")
    logger.info(f"{BOT_RIGHTS}")
    logger.info(f"Available games: {len(AVAILABLE_GAMES)}")
    logger.info(f"One point per correct answer")
    logger.info(f"Automatic team mode | Easy toggle")
    logger.info(f"Compatibility: Entertainment system without points")
    logger.info(f"Permanent leaderboard in database")
    logger.info(f"Port: {port}")
    logger.info("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=False)
