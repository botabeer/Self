import json, time, os, getpass, threading
from datetime import datetime, timedelta
from collections import defaultdict

print("\n" + "="*60)
print("LINE Protection Bot - Professional Edition")
print("="*60)

# ================== Check Libraries ==================
try:
    from linepy import LINE, OEPoll
    print("linepy ready")
except ImportError:
    print("\n✗ linepy not installed!")
    print("\nInstall: pip install git+https://github.com/dyseo/linepy.git")
    exit(1)

# ================== Configuration ==================
DB_FILE = "db.json"
LOG_FILE = "logs.txt"
TOKEN_FILE = "token.txt"

# Limits
AUTO_WARN_LIMIT = 3
SPAM_TIME = 2
SPAM_COUNT = 5
MAX_KICK_PER_MIN = 3
PROTECT_REJOIN_DELAY = 2

# ================== Default Database ==================
DEFAULT_DB = {
    "owners": [],
    "admins": [],
    "vip": [],
    "banned": [],
    "muted": [],
    "warnings": {},
    "lock": {},
    "freeze": {},
    "watched": {},
    "ghost_mode": False,
    "shield_mode": False,
    "protect": {
        "kick": True,
        "invite": True,
        "qr": True,
        "bots": True,
        "spam": True,
        "flood": True
    },
    "whitelist_bots": [],
    "kick_history": {},
    "last_kick": "",
    "last_ban": "",
    "stats": {
        "kicks": 0,
        "bans": 0,
        "protections": 0,
        "messages": 0
    },
    "enabled": True
}

# ================== Database Functions ==================
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump(DEFAULT_DB, f, indent=2)
        return DEFAULT_DB.copy()
    
    with open(DB_FILE) as f:
        db = json.load(f)
    
    for key in DEFAULT_DB:
        if key not in db:
            db[key] = DEFAULT_DB[key]
    
    return db

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

# ================== Logging ==================
def log(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

# ================== Login ==================
def login():
    print("\n" + "-"*60)
    print("Login to LINE")
    print("-"*60)
    
    if os.path.exists(TOKEN_FILE):
        try:
            print("Attempting login with saved token...")
            with open(TOKEN_FILE) as f:
                token = f.read().strip()
            client = LINE(token)
            print("Login successful!")
            return client
        except:
            print("Token invalid, removing...")
            os.remove(TOKEN_FILE)
    
    print("\nUse secondary LINE account only!")
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    
    try:
        print("\nLogging in...")
        client = LINE(email, password)
        
        with open(TOKEN_FILE, "w") as f:
            f.write(client.authToken)
        
        print("Login successful!")
        print(f"Account: {client.profile.displayName}")
        return client
    except Exception as e:
        print(f"\n✗ Login failed: {e}")
        print("\nCheck:")
        print("  - Email and Password correct")
        print("  - Disable 2FA in LINE settings")
        print("  - Internet connection")
        exit(1)

cl = login()
op = OEPoll(cl)
my_mid = cl.profile.mid

if my_mid not in db["owners"]:
    db["owners"].append(my_mid)
    save_db()
    log(f"Added {my_mid} as owner")

print("\n" + "="*60)
print(f"Bot Ready: {cl.profile.displayName}")
print(f"ID: {my_mid}")
print(f"Owners: {len(db['owners'])} | Admins: {len(db['admins'])}")
print("="*60 + "\n")
print("Bot is running...")
print("Press Ctrl+C to stop\n")
print("="*60 + "\n")

# ================== Permission System ==================
def is_owner(u):
    return u in db["owners"]

def is_admin(u):
    return u in db["admins"] or is_owner(u)

def is_vip(u):
    return u in db["vip"]

def is_banned(u):
    return u in db["banned"]

def is_muted(u):
    return u in db["muted"]

def is_watched(u):
    return u in db["watched"]

def get_role(u):
    if is_owner(u):
        return "Owner"
    elif is_admin(u):
        return "Admin"
    elif is_vip(u):
        return "VIP"
    else:
        return "Member"

# ================== Anti-Spam System ==================
user_msgs = defaultdict(list)
spammers = []

def is_spam(u):
    if is_vip(u) or not db["protect"]["spam"]:
        return False
    
    now = time.time()
    user_msgs[u] = [t for t in user_msgs[u] if now - t < SPAM_TIME]
    user_msgs[u].append(now)
    
    if len(user_msgs[u]) > SPAM_COUNT:
        if u not in spammers:
            spammers.append(u)
        return True
    
    return False

# ================== Anti-Flood System ==================
kick_history = defaultdict(list)

def can_kick(u, g):
    if not db["protect"]["flood"]:
        return True
    
    now = time.time()
    key = f"{u}:{g}"
    kick_history[key] = [t for t in kick_history[key] if now - t < 60]
    
    if len(kick_history[key]) >= MAX_KICK_PER_MIN:
        return False
    
    kick_history[key].append(now)
    return True

# ================== Warning System ==================
def add_warn(u, silent=False):
    db["warnings"].setdefault(u, 0)
    db["warnings"][u] += 1
    save_db()
    if not silent:
        log(f"Warning added to {u} (total: {db['warnings'][u]})")
    return db["warnings"][u]

def clear_warn(u):
    if u in db["warnings"]:
        del db["warnings"][u]
        save_db()
        log(f"Warnings cleared for {u}")

def get_warns(u):
    return db["warnings"].get(u, 0)

# ================== Bot Detection ==================
def is_bot(name):
    bot_keywords = ["bot", "self", "auto", "[bot]", "{bot}", "🤖", "robot"]
    name_lower = name.lower()
    return any(keyword in name_lower for keyword in bot_keywords)

def is_whitelisted_bot(mid):
    return mid in db["whitelist_bots"] or mid == my_mid

# ================== Protection Functions ==================
def safe_kick(g, target, reason="", silent=False):
    try:
        if target == my_mid:
            return False
        
        if is_owner(target):
            return False
        
        cl.kickoutFromGroup(g, [target])
        db["stats"]["kicks"] += 1
        db["last_kick"] = f"{target} - {reason} - {datetime.now()}"
        save_db()
        if not silent:
            log(f"Kicked {target} from {g} - {reason}")
        return True
    except Exception as e:
        if not silent:
            log(f"Kick failed: {e}")
        return False

def rejoin_group(g):
    try:
        time.sleep(PROTECT_REJOIN_DELAY)
        cl.acceptGroupInvitation(g)
        log(f"Rejoined group {g}")
        return True
    except Exception as e:
        log(f"Rejoin failed: {e}")
        return False

# ================== Mention Parser ==================
def get_mentioned_mid(msg):
    try:
        if not msg.contentMetadata or "MENTION" not in msg.contentMetadata:
            return None
        
        mention_data = msg.contentMetadata["MENTION"]
        mid = mention_data.split('"M":"')[1].split('"')[0]
        return mid
    except:
        return None

# ================== Send Message (Ghost Mode) ==================
def send_msg(g, text):
    if not db["ghost_mode"]:
        cl.sendMessage(g, text)

# ================== Command Handler ==================
def handle_message(msg):
    if not msg.text:
        return
    
    text = msg.text.strip()
    text_lower = text.lower()
    sender = msg._from
    group = msg.to
    
    db["stats"]["messages"] += 1
    
    if not db["enabled"]:
        return
    
    # Auto Ban
    if is_banned(sender):
        safe_kick(group, sender, "banned user", True)
        return
    
    # Auto Kick Muted
    if is_muted(sender):
        safe_kick(group, sender, "muted user", True)
        return
    
    # Group Lock
    if db["lock"].get(group, False) and not is_admin(sender):
        safe_kick(group, sender, "group locked", True)
        return
    
    # Freeze Mode
    if db["freeze"].get(group, False) and not is_admin(sender):
        safe_kick(group, sender, "freeze mode", True)
        return
    
    # Shield Mode
    if db["shield_mode"] and not is_admin(sender):
        safe_kick(group, sender, "shield mode", True)
        return
    
    # Watch Mode
    if is_watched(sender) and not is_admin(sender):
        if is_spam(sender):
            safe_kick(group, sender, "watched + spam", True)
            return
    
    # Anti-Spam
    if is_spam(sender):
        log(f"Spam detected from {sender}")
        return
    
    # ================== Secret Commands (Hidden) ==================
    
    # General Secret
    if text == ".":
        send_msg(group, ".")
        return
    
    elif text_lower == "id":
        send_msg(group, sender)
        return
    
    elif text_lower == "gid":
        send_msg(group, group)
        return
    
    elif text_lower == "r" and is_admin(sender):
        global db
        db = load_db()
        send_msg(group, "Reloaded")
        return
    
    # Admin Secret
    elif text_lower in ["sk", "x"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            safe_kick(group, target, "silent kick", True)
        return
    
    elif text_lower in ["sm", "z"] and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            if target not in db["muted"]:
                db["muted"].append(target)
                save_db()
        return
    
    elif text_lower == "zz" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and target in db["muted"]:
            db["muted"].remove(target)
            save_db()
        return
    
    elif text_lower == "sw" and is_admin(sender):
        target = get_mentioned_mid(msg)
        if target and not is_owner(target):
            add_warn(target, True)
        return
    
    elif text_lower
