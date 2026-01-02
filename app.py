# -*- coding: utf-8 -*-
"""
🛡️ LINE Protection Bot - Real Protection 100%
✅ يستخدم حساب LINE عادي (ليس Official Account)
✅ حماية حقيقية: طرد + إلغاء دعوات + تغيير إعدادات
✅ مجاني تماماً
"""

import json
import time
import os
from datetime import datetime
from flask import Flask, request

# ===== المكتبة السحرية =====
# pip install git+https://github.com/dyseo/linepy.git
try:
    from linepy import LINE, OEPoll
    print("✅ linepy مثبتة")
except ImportError:
    print("❌ قم بتثبيت: pip install git+https://github.com/dyseo/linepy.git")
    exit(1)

app = Flask(__name__)

# ========== الإعدادات ==========
class Config:
    # طرق تسجيل الدخول:
    # 1. Email/Password (الأسهل)
    EMAIL = os.getenv('LINE_EMAIL', '')
    PASSWORD = os.getenv('LINE_PASSWORD', '')
    
    # 2. Auth Token (الأأمن - بعد أول تسجيل دخول)
    AUTH_TOKEN = os.getenv('LINE_AUTH_TOKEN', '')
    
    # 3. QR Code (محلياً فقط - مو للـ Server)
    USE_QR = False

# ========== قاعدة البيانات ==========
class Database:
    def __init__(self):
        self.owners = self.load('owners.json', {})
        self.admins = self.load('admins.json', {})
        self.banned = self.load('banned.json', {})
        
        # الإعدادات الافتراضية
        self.settings = {
            'protect': True,
            'kick_protect': True,
            'invite_protect': True,
            'qr_protect': True,
            'cancel_protect': True,
            'auto_kick_banned': True,
            'welcome_message': True,
            'auto_rejoin': True  # إعادة الانضمام تلقائياً بعد الطرد
        }
        
        self.logs = []
        self.start_time = time.time()
    
    def load(self, filename, default):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f) or default
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
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ خطأ حفظ: {e}")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        if len(self.logs) > 200:
            self.logs.pop(0)
        print(f"🛡️ {log_entry}")

db = Database()

# ========== LINE Bot Setup ==========
class ProtectionBot:
    def __init__(self):
        self.client = None
        self.poll = None
        self.mid = None
        self.profile = None
        
    def login(self):
        """تسجيل الدخول"""
        try:
            # محاولة 1: Auth Token (الأسرع)
            if Config.AUTH_TOKEN:
                print("🔐 تسجيل دخول بـ Auth Token...")
                self.client = LINE(Config.AUTH_TOKEN)
            
            # محاولة 2: Email/Password
            elif Config.EMAIL and Config.PASSWORD:
                print("🔐 تسجيل دخول بـ Email/Password...")
                self.client = LINE(Config.EMAIL, Config.PASSWORD)
                
                # حفظ Auth Token للمرات القادمة
                Config.AUTH_TOKEN = self.client.authToken
                print(f"✅ Auth Token: {Config.AUTH_TOKEN[:50]}...")
                print("💡 احفظه في Environment Variable: LINE_AUTH_TOKEN")
            
            # محاولة 3: QR Code (محلياً فقط)
            elif Config.USE_QR:
                print("📱 تسجيل دخول بـ QR Code...")
                self.client = LINE()
            
            else:
                print("❌ لا توجد بيانات تسجيل دخول!")
                print("أضف في Environment:")
                print("  LINE_EMAIL=email@example.com")
                print("  LINE_PASSWORD=yourpassword")
                return False
            
            # جلب معلومات الحساب
            self.profile = self.client.getProfile()
            self.mid = self.profile.mid
            self.poll = OEPoll(self.client)
            
            print("="*60)
            print("✅ تم تسجيل الدخول بنجاح!")
            print(f"📱 الاسم: {self.profile.displayName}")
            print(f"🆔 MID: {self.mid[:30]}...")
            print("="*60)
            
            # إضافة نفسك كـ Owner تلقائياً
            if self.mid not in db.owners:
                db.owners[self.mid] = True
                db.save()
                print("👑 تمت إضافتك كـ Owner تلقائياً")
            
            return True
            
        except Exception as e:
            print(f"❌ فشل تسجيل الدخول: {e}")
            return False
    
    def is_owner(self, mid):
        return mid in db.owners
    
    def is_admin(self, mid):
        return mid in db.owners or mid in db.admins
    
    def is_banned(self, mid):
        return mid in db.banned
    
    def handle_message(self, msg):
        """معالج الرسائل"""
        try:
            text = msg.text
            if not text:
                return
            
            sender = msg._from
            to = msg.to
            
            # منع المحظورين
            if self.is_banned(sender):
                db.log(f"محظور حاول إرسال: {sender[:15]}...")
                return
            
            cmd = text.lower().strip()
            
            # ========== الأوامر ==========
            if cmd in ['help', 'مساعدة']:
                help_text = """╔═════════════════════════
║ 🛡️ بوت الحماية الحقيقي
║
║ 📋 للجميع:
║ • help - الأوامر
║ • status - الحالة
║ • me - معلوماتي
║
║ 👮 Admin:
║ • protect on/off
║ • kickprotect on/off
║ • inviteprotect on/off
║ • qrprotect on/off
║ • allprotect on/off
║
║ 👑 Owner:
║ • addowner @mention
║ • addadmin @mention
║ • ban @mention
║ • unban @mention
║ • banlist
║ • kick @mention
║ • kickall
║ • invite @mention
║ • open/close (فتح/إغلاق الرابط)
║ • url (رابط المجموعة)
║
║ ✅ حماية حقيقية 100%
╚═════════════════════════"""
                self.client.sendMessage(to, help_text)
            
            elif cmd in ['status', 'الحالة']:
                uptime = int(time.time() - db.start_time)
                h, m = uptime // 3600, (uptime % 3600) // 60
                
                status = f"""╔═════════════════════════
║ 📊 حالة البوت
║
║ ⏰ التشغيل: {h}س {m}د
║ 👑 Owners: {len(db.owners)}
║ 👮 Admins: {len(db.admins)}
║ 🚫 Banned: {len(db.banned)}
║ 📝 Logs: {len(db.logs)}
║
║ 🛡️ الحماية:
║ • Protect: {'✅' if db.settings['protect'] else '❌'}
║ • Kick: {'✅' if db.settings['kick_protect'] else '❌'}
║ • Invite: {'✅' if db.settings['invite_protect'] else '❌'}
║ • QR: {'✅' if db.settings['qr_protect'] else '❌'}
║ • Auto Rejoin: {'✅' if db.settings['auto_rejoin'] else '❌'}
║
╚═════════════════════════"""
                self.client.sendMessage(to, status)
            
            elif cmd == 'me':
                contact = self.client.getContact(sender)
                info = f"""╔═════════════════════════
║ 📱 معلوماتك
║
║ 👤 الاسم: {contact.displayName}
║ 🆔 MID: {sender}
║ 📝 الحالة: {contact.statusMessage or 'لا يوجد'}
║ 🏆 الصلاحية: {'👑 Owner' if self.is_owner(sender) else '👮 Admin' if self.is_admin(sender) else '👤 Member'}
║
╚═════════════════════════"""
                self.client.sendMessage(to, info)
            
            # ========== Admin Commands ==========
            elif cmd == 'protect on' and self.is_admin(sender):
                db.settings['protect'] = True
                self.client.sendMessage(to, "✅ تم تفعيل الحماية العامة")
                db.log("تفعيل الحماية العامة")
            
            elif cmd == 'protect off' and self.is_admin(sender):
                db.settings['protect'] = False
                self.client.sendMessage(to, "⚠️ تم إيقاف الحماية العامة")
                db.log("إيقاف الحماية العامة")
            
            elif cmd == 'kickprotect on' and self.is_admin(sender):
                db.settings['kick_protect'] = True
                self.client.sendMessage(to, "✅ حماية الطرد مفعّلة")
            
            elif cmd == 'kickprotect off' and self.is_admin(sender):
                db.settings['kick_protect'] = False
                self.client.sendMessage(to, "❌ حماية الطرد متوقفة")
            
            elif cmd == 'inviteprotect on' and self.is_admin(sender):
                db.settings['invite_protect'] = True
                self.client.sendMessage(to, "✅ حماية الدعوات مفعّلة")
            
            elif cmd == 'inviteprotect off' and self.is_admin(sender):
                db.settings['invite_protect'] = False
                self.client.sendMessage(to, "❌ حماية الدعوات متوقفة")
            
            elif cmd == 'qrprotect on' and self.is_admin(sender):
                db.settings['qr_protect'] = True
                self.client.sendMessage(to, "✅ حماية الرابط مفعّلة")
            
            elif cmd == 'qrprotect off' and self.is_admin(sender):
                db.settings['qr_protect'] = False
                self.client.sendMessage(to, "❌ حماية الرابط متوقفة")
            
            elif cmd == 'allprotect on' and self.is_admin(sender):
                db.settings['protect'] = True
                db.settings['kick_protect'] = True
                db.settings['invite_protect'] = True
                db.settings['qr_protect'] = True
                self.client.sendMessage(to, "✅ تم تفعيل جميع أنواع الحماية")
            
            elif cmd == 'allprotect off' and self.is_admin(sender):
                for key in ['protect', 'kick_protect', 'invite_protect', 'qr_protect']:
                    db.settings[key] = False
                self.client.sendMessage(to, "⚠️ تم إيقاف جميع أنواع الحماية")
            
            # ========== Owner Commands ==========
            elif cmd.startswith('addowner') and self.is_owner(sender):
                if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                    mentions = json.loads(msg.contentMetadata['MENTION'])
                    for mention in mentions['MENTIONEES']:
                        db.owners[mention['M']] = True
                    db.save()
                    self.client.sendMessage(to, f"✅ تمت إضافة {len(mentions['MENTIONEES'])} Owner")
                else:
                    self.client.sendMessage(to, "📝 اكتب: addowner @الشخص")
            
            elif cmd.startswith('addadmin') and self.is_owner(sender):
                if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                    mentions = json.loads(msg.contentMetadata['MENTION'])
                    for mention in mentions['MENTIONEES']:
                        db.admins[mention['M']] = True
                    db.save()
                    self.client.sendMessage(to, f"✅ تمت إضافة {len(mentions['MENTIONEES'])} Admin")
                else:
                    self.client.sendMessage(to, "📝 اكتب: addadmin @الشخص")
            
            elif cmd.startswith('ban ') and self.is_owner(sender):
                if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                    mentions = json.loads(msg.contentMetadata['MENTION'])
                    for mention in mentions['MENTIONEES']:
                        mid = mention['M']
                        if not self.is_owner(mid) and not self.is_admin(mid):
                            db.banned[mid] = True
                    db.save()
                    self.client.sendMessage(to, f"🚫 تم حظر {len(mentions['MENTIONEES'])} شخص")
                else:
                    self.client.sendMessage(to, "📝 اكتب: ban @الشخص")
            
            elif cmd.startswith('unban') and self.is_owner(sender):
                if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                    mentions = json.loads(msg.contentMetadata['MENTION'])
                    for mention in mentions['MENTIONEES']:
                        if mention['M'] in db.banned:
                            del db.banned[mention['M']]
                    db.save()
                    self.client.sendMessage(to, "✅ تم إلغاء الحظر")
                else:
                    self.client.sendMessage(to, "📝 اكتب: unban @الشخص")
            
            elif cmd == 'banlist' and self.is_owner(sender):
                if not db.banned:
                    self.client.sendMessage(to, "✅ قائمة الحظر فارغة")
                else:
                    text = f"╔═══[ 🚫 المحظورين ({len(db.banned)}) ]\n"
                    for i, mid in enumerate(list(db.banned.keys())[:20], 1):
                        try:
                            contact = self.client.getContact(mid)
                            text += f"║ {i}. {contact.displayName}\n"
                        except:
                            text += f"║ {i}. {mid[:20]}...\n"
                    text += "╚═══════════════"
                    self.client.sendMessage(to, text)
            
            # ========== Group Actions (Real!) ==========
            elif cmd.startswith('kick ') and self.is_admin(sender):
                try:
                    if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                        mentions = json.loads(msg.contentMetadata['MENTION'])
                        kicked = 0
                        for mention in mentions['MENTIONEES']:
                            mid = mention['M']
                            if not self.is_owner(mid) and not self.is_admin(mid):
                                self.client.kickoutFromGroup(to, [mid])
                                kicked += 1
                                time.sleep(0.5)
                        self.client.sendMessage(to, f"✅ تم طرد {kicked} عضو")
                        db.log(f"طرد {kicked} عضو")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
            
            elif cmd == 'kickall' and self.is_owner(sender):
                try:
                    group = self.client.getGroup(to)
                    kicked = 0
                    for member in group.members:
                        if not self.is_owner(member.mid) and not self.is_admin(member.mid) and member.mid != self.mid:
                            try:
                                self.client.kickoutFromGroup(to, [member.mid])
                                kicked += 1
                                time.sleep(0.3)
                            except:
                                pass
                    self.client.sendMessage(to, f"✅ تم طرد {kicked} عضو")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
            
            elif cmd.startswith('invite ') and self.is_admin(sender):
                try:
                    if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                        mentions = json.loads(msg.contentMetadata['MENTION'])
                        mids = [m['M'] for m in mentions['MENTIONEES']]
                        self.client.inviteIntoGroup(to, mids)
                        self.client.sendMessage(to, f"✅ تمت دعوة {len(mids)} شخص")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
            
            elif cmd == 'open' and self.is_admin(sender):
                try:
                    group = self.client.getGroup(to)
                    group.preventedJoinByTicket = False
                    self.client.updateGroup(group)
                    self.client.sendMessage(to, "✅ تم فتح رابط المجموعة")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
            
            elif cmd == 'close' and self.is_admin(sender):
                try:
                    group = self.client.getGroup(to)
                    group.preventedJoinByTicket = True
                    self.client.updateGroup(group)
                    self.client.sendMessage(to, "✅ تم إغلاق رابط المجموعة")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
            
            elif cmd == 'url' and self.is_admin(sender):
                try:
                    group = self.client.getGroup(to)
                    if group.preventedJoinByTicket:
                        self.client.sendMessage(to, "❌ الرابط مغلق\nاكتب: open لفتحه")
                    else:
                        ticket = self.client.reissueGroupTicket(to)
                        self.client.sendMessage(to, f"🔗 رابط المجموعة:\nhttps://line.me/R/ti/g/{ticket}")
                except Exception as e:
                    self.client.sendMessage(to, f"❌ خطأ: {e}")
        
        except Exception as e:
            print(f"❌ خطأ في handle_message: {e}")
    
    def handle_kick(self, op):
        """حماية من الطرد"""
        try:
            if not db.settings['protect'] or not db.settings['kick_protect']:
                return
            
            kicker = op.param2  # من طرد
            kicked = op.param3  # من تم طرده
            group_id = op.param1
            
            # إذا تم طرد البوت أو Owner أو Admin
            if kicked == self.mid or self.is_owner(kicked) or self.is_admin(kicked):
                # طرد الفاعل
                if not self.is_admin(kicker):
                    self.client.kickoutFromGroup(group_id, [kicker])
                    db.banned[kicker] = True
                    db.save()
                    self.client.sendMessage(group_id, f"⚠️ تم طرد المعتدي\n🚫 تمت إضافته للقائمة السوداء")
                    db.log(f"طرد معتدي: {kicker[:15]}...")
                
                # إعادة دعوة المطرود
                if kicked != self.mid:
                    time.sleep(1)
                    self.client.inviteIntoGroup(group_id, [kicked])
                    db.log(f"إعادة دعوة: {kicked[:15]}...")
                
                # إعادة انضمام البوت
                elif db.settings['auto_rejoin']:
                    time.sleep(1)
                    group = self.client.getGroup(group_id)
                    if not group.preventedJoinByTicket:
                        ticket = self.client.reissueGroupTicket(group_id)
                        self.client.acceptGroupInvitationByTicket(group_id, ticket)
                        db.log("إعادة انضمام تلقائي")
        
        except Exception as e:
            print(f"❌ خطأ في handle_kick: {e}")
    
    def handle_invite(self, op):
        """حماية من الدعوات"""
        try:
            if not db.settings['protect'] or not db.settings['invite_protect']:
                return
            
            inviter = op.param2  # من دعا
            invited = op.param3  # من تمت دعوته
            group_id = op.param1
            
            # إلغاء الدعوة إذا كان المدعو محظور
            if self.is_banned(invited):
                self.client.cancelGroupInvitation(group_id, [invited])
                self.client.sendMessage(group_id, f"🚫 تم إلغاء دعوة محظور")
                db.log(f"إلغاء دعوة محظور: {invited[:15]}...")
            
            # إلغاء وطرد إذا كان الداعي غير مصرح له
            elif not self.is_admin(inviter):
                self.client.cancelGroupInvitation(group_id, [invited])
                self.client.kickoutFromGroup(group_id, [inviter])
                self.client.sendMessage(group_id, f"⚠️ دعوة غير مصرح بها\n🚫 تم طرد الداعي")
                db.log(f"طرد داعٍ غير مصرح: {inviter[:15]}...")
        
        except Exception as e:
            print(f"❌ خطأ في handle_invite: {e}")
    
    def handle_qr_opened(self, op):
        """حماية من فتح الرابط"""
        try:
            if not db.settings['protect'] or not db.settings['qr_protect']:
                return
            
            opener = op.param2
            group_id = op.param1
            
            if not self.is_admin(opener):
                # إغلاق الرابط
                group = self.client.getGroup(group_id)
                group.preventedJoinByTicket = True
                self.client.updateGroup(group)
                
                # طرد الفاعل
                self.client.kickoutFromGroup(group_id, [opener])
                self.client.sendMessage(group_id, f"⚠️ تم إغلاق الرابط وطرد الفاعل")
                db.log(f"طرد فاتح رابط: {opener[:15]}...")
        
        except Exception as e:
            print(f"❌ خطأ في handle_qr_opened: {e}")
    
    def handle_member_join(self, op):
        """معالج انضمام عضو"""
        try:
            joined = op.param2
            group_id = op.param1
            
            # طرد المحظورين تلقائياً
            if db.settings['auto_kick_banned'] and self.is_banned(joined):
                self.client.kickoutFromGroup(group_id, [joined])
                self.client.sendMessage(group_id, f"🚫 تم طرد عضو محظور تلقائياً")
                db.log(f"طرد محظور: {joined[:15]}...")
            
            # رسالة ترحيب
            elif db.settings['welcome_message']:
                try:
                    contact = self.client.getContact(joined)
                    self.client.sendMessage(group_id, f"👋 مرحباً {contact.displayName}!")
                except:
                    pass
        
        except Exception as e:
            print(f"❌ خطأ في handle_member_join: {e}")
    
    def start_polling(self):
        """بدء الاستماع للأحداث"""
        print("\n🚀 البوت يعمل الآن...")
        print("💡 اكتب 'help' في LINE للأوامر\n")
        
        while True:
            try:
                operations = self.poll.singleTrace(count=50)
                
                if operations:
                    for op in operations:
                        # 26 = رسالة
                        if op.type == 26:
                            self.handle_message(op.message)
                        
                        # 19 = طرد عضو
                        elif op.type == 19:
                            self.handle_kick(op)
                        
                        # 13 = دعوة عضو
                        elif op.type == 13:
                            self.handle_invite(op)
                        
                        # 11 = فتح رابط
                        elif op.type == 11:
                            self.handle_qr_opened(op)
                        
                        # 17 = انضمام عضو
                        elif op.type == 17:
                            self.handle_member_join(op)
                        
                        self.poll.setRevision(op.revision)
                
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n👋 إيقاف البوت...")
                db.save()
                break
            
            except Exception as e:
                print(f"❌ خطأ: {e}")
                time.sleep(2)

# ========== Flask Routes (للـ Health Check فقط) ==========
@app.route("/")
def home():
    uptime = int(time.time() - db.start_time)
    h, m = uptime // 3600, (uptime % 3600) // 60
    
    return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="utf-8">
    <title>🛡️ LINE Protection Bot</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
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
            max-width: 500px;
        }}
        h1 {{ font-size: 3em; margin: 0; }}
        .status {{ font-size: 1.5em; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️</h1>
        <h2>LINE Protection Bot</h2>
        <div class="status">✅ Online</div>
        <p>⏰ التشغيل: {h}س {m}د</p>
        <p>🛡️ الحماية: {'✅ مفعّلة' if db.settings['protect'] else '❌ متوقفة'}</p>
        <p>📝 Logs: {len(db.logs)}</p>
    </div>
</body>
</html>
""", 200

@app.route("/health")
def health():
    return {
        "status": "ok",
        "uptime": int(time.time() - db.start_time),
        "protect": db.settings['protect'],
        "logs": len(db.logs)
    }, 200

# ========== Main ==========
if __name__ == "__main__":
    print("="*60)
    print("🛡️ LINE Protection Bot - Real Protection")
    print("="*60)
    
    bot = ProtectionBot()
    
    if bot.login():
        # تشغيل Flask في خيط منفصل
        import threading
        
        def run_flask():
            port = int(os.environ.get('PORT', 10000))
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        print("✅ Flask Server بدأ")
        time.sleep(2)
        
        # بدء الاستماع للأحداث
        bot.start_polling()
    else:
        print("❌ فشل التشغيل - تحقق من بيانات الدخول")
