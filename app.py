# -*- coding: utf-8 -*-
from linepy import LINE, OEPoll
from datetime import datetime
import time, json, os, sys, ast

# ========== التهيئة ==========
class Bot:
    def __init__(self):
        print("🔄 جاري تسجيل الدخول...")
        try:
            # طريقة 1: استخدام Auth Token (أضف توكنك هنا)
            token = os.getenv('LINE_TOKEN', '')
            if token:
                self.client = LINE(token)
            else:
                # طريقة 2: البريد وكلمة المرور
                email = os.getenv('LINE_EMAIL', '')
                password = os.getenv('LINE_PASSWORD', '')
                if email and password:
                    self.client = LINE(email, password)
                else:
                    print("❌ يجب إضافة LINE_TOKEN أو (LINE_EMAIL + LINE_PASSWORD)")
                    sys.exit(1)
            
            self.poll = OEPoll(self.client)
            self.mid = self.client.profile.mid
            self.name = self.client.profile.displayName
            print(f"✅ تم تسجيل الدخول: {self.name}")
        except Exception as e:
            print(f"❌ فشل تسجيل الدخول: {e}")
            sys.exit(1)
        
        # تحميل البيانات
        self.owner = self.load('owner.json', {})
        self.admin = self.load('admin.json', {})
        self.banned = self.load('banned.json', {})
        
        # الإعدادات
        self.protect = True
        self.kick_protect = True
        self.invite_protect = True
        self.qr_protect = True
        self.auto_join = True
        self.auto_close = True
        
        self.start = time.time()
    
    def load(self, file, default):
        try:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    return json.load(f) or default
            return default
        except:
            return default
    
    def save(self):
        try:
            with open('owner.json', 'w') as f:
                json.dump(self.owner, f, indent=2)
            with open('admin.json', 'w') as f:
                json.dump(self.admin, f, indent=2)
            with open('banned.json', 'w') as f:
                json.dump(self.banned, f, indent=2)
        except:
            pass

# ========== الحماية ==========
def kick_ban(bot, gid, uid, msg=""):
    try:
        bot.client.kickoutFromGroup(gid, [uid])
        bot.banned[uid] = True
        bot.save()
        if msg:
            bot.client.sendMessage(gid, f"⚠️ {msg}")
    except:
        pass

def secure(bot, gid):
    try:
        g = bot.client.getGroup(gid)
        g.preventedJoinByTicket = True
        bot.client.updateGroup(g)
    except:
        pass

def rejoin(bot, gid):
    try:
        g = bot.client.getGroup(gid)
        g.preventedJoinByTicket = False
        bot.client.updateGroup(g)
        t = bot.client.reissueGroupTicket(gid)
        bot.client.acceptGroupInvitationByTicket(gid, t)
        g.preventedJoinByTicket = True
        bot.client.updateGroup(g)
        return True
    except:
        return False

# ========== معالج الأحداث ==========
def handle_kick(bot, op):
    if not bot.kick_protect:
        return
    try:
        gid, kicker, kicked = op.param1, op.param2, op.param3
        
        if kicked == bot.mid:
            if kicker not in bot.owner:
                time.sleep(0.5)
                if rejoin(bot, gid):
                    time.sleep(0.5)
                    kick_ban(bot, gid, kicker, "طرد البوت ❌")
        elif kicked in bot.owner or kicked in bot.admin:
            if kicker not in bot.owner:
                kick_ban(bot, gid, kicker, "طرد أدمن ❌")
                try:
                    bot.client.inviteIntoGroup(gid, [kicked])
                except:
                    pass
    except:
        pass

def handle_invite(bot, op):
    if not bot.invite_protect:
        return
    try:
        gid, inviter, invited = op.param1, op.param2, op.param3
        
        if invited == bot.mid:
            if bot.auto_join:
                bot.client.acceptGroupInvitation(gid)
                time.sleep(0.5)
                if bot.auto_close:
                    secure(bot, gid)
            return
        
        if invited in bot.banned:
            bot.client.cancelGroupInvitation(gid, [invited])
            bot.client.sendMessage(gid, "⚠️ عضو محظور")
            return
        
        if inviter in bot.owner or inviter in bot.admin:
            return
        
        bot.client.cancelGroupInvitation(gid, [invited])
        kick_ban(bot, gid, inviter, "دعوة بدون صلاحية ❌")
    except:
        pass

def handle_qr(bot, op):
    if not bot.qr_protect:
        return
    try:
        gid, opener = op.param1, op.param2
        if opener not in bot.owner and opener not in bot.admin:
            secure(bot, gid)
            kick_ban(bot, gid, opener, "فتح الرابط ❌")
    except:
        pass

def handle_join(bot, op):
    try:
        gid, joiner = op.param1, op.param2
        if joiner == bot.mid:
            if bot.auto_close:
                time.sleep(1)
                secure(bot, gid)
            bot.client.sendMessage(gid, "╔════════════════\n║ 🛡️ بوت الحماية\n║ الأوامر: help\n╚════════════════")
    except:
        pass

# ========== معالج الأوامر ==========
def is_owner(bot, uid):
    return uid in bot.owner

def is_admin(bot, uid):
    return uid in bot.owner or uid in bot.admin

def get_mentions(msg):
    try:
        if 'MENTION' in msg.contentMetadata:
            m = ast.literal_eval(msg.contentMetadata['MENTION'])
            return [x['M'] for x in m['MENTIONEES']]
    except:
        pass
    return []

def handle_cmd(bot, msg):
    try:
        if not msg.text:
            return
        
        txt = msg.text.lower().strip()
        sender = msg._from
        to = msg.to if msg.toType == 2 else sender
        
        if txt == 'help':
            bot.client.sendMessage(to, """╔════════════════
║ 📋 الأوامر
║
║ 🔹 عامة:
║ • help | status | speed
║ • time | runtime
║
║ 🔹 أدمن:
║ • kick @mention
║ • ban @mention
║ • unban @mention
║ • protect on/off
║ • qrclose | qropen
║ • adminlist
║
║ 🔹 أونر:
║ • addowner @mention
║ • delowner @mention
║ • addadmin @mention
║ • deladmin @mention
║ • banlist | clearban
║ • restart
║
╚════════════════""")
        
        elif txt == 'status':
            t = int(time.time() - bot.start)
            h, m = t // 3600, (t % 3600) // 60
            bot.client.sendMessage(to, f"""╔════════════════
║ 📊 الحالة
║
║ 🤖 {bot.name}
║ ⏱️ {h}س {m}د
║ 👑 أونر: {len(bot.owner)}
║ 👮 أدمن: {len(bot.admin)}
║ 🚫 محظورين: {len(bot.banned)}
║
║ 🛡️ الحماية:
║ • طرد: {'✅' if bot.kick_protect else '❌'}
║ • دعوات: {'✅' if bot.invite_protect else '❌'}
║ • رابط: {'✅' if bot.qr_protect else '❌'}
║
╚════════════════""")
        
        elif txt == 'speed':
            s = time.time()
            bot.client.sendMessage(to, "⏱️ جاري...")
            bot.client.sendMessage(to, f"⚡ {time.time() - s:.3f}s")
        
        elif txt == 'time':
            n = datetime.now()
            bot.client.sendMessage(to, f"🕐 {n.strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif txt == 'runtime':
            t = int(time.time() - bot.start)
            d = t // 86400
            h = (t % 86400) // 3600
            m = (t % 3600) // 60
            s = t % 60
            bot.client.sendMessage(to, f"⏰ {d}ي {h}س {m}د {s}ث")
        
        elif txt.startswith('kick') and is_admin(bot, sender):
            for u in get_mentions(msg):
                if u not in bot.owner:
                    kick_ban(bot, to, u, "تم الطرد")
        
        elif txt.startswith('ban') and is_admin(bot, sender):
            for u in get_mentions(msg):
                bot.banned[u] = True
                bot.save()
            bot.client.sendMessage(to, "✅ تم الحظر")
        
        elif txt.startswith('unban') and is_admin(bot, sender):
            for u in get_mentions(msg):
                if u in bot.banned:
                    del bot.banned[u]
                    bot.save()
            bot.client.sendMessage(to, "✅ تم فك الحظر")
        
        elif txt == 'protect on' and is_admin(bot, sender):
            bot.protect = bot.kick_protect = bot.invite_protect = bot.qr_protect = True
            bot.client.sendMessage(to, "✅ تفعيل الحماية")
        
        elif txt == 'protect off' and is_admin(bot, sender):
            bot.protect = bot.kick_protect = bot.invite_protect = bot.qr_protect = False
            bot.client.sendMessage(to, "⚠️ إيقاف الحماية")
        
        elif txt == 'qrclose' and is_admin(bot, sender):
            secure(bot, to)
            bot.client.sendMessage(to, "✅ إغلاق الرابط")
        
        elif txt == 'qropen' and is_admin(bot, sender):
            try:
                g = bot.client.getGroup(to)
                g.preventedJoinByTicket = False
                bot.client.updateGroup(g)
                t = bot.client.reissueGroupTicket(to)
                bot.client.sendMessage(to, f"✅ line.me/R/ti/g/{t}")
            except:
                bot.client.sendMessage(to, "❌ فشل")
        
        elif txt == 'adminlist' and is_admin(bot, sender):
            if not bot.admin:
                bot.client.sendMessage(to, "❌ لا يوجد أدمن")
            else:
                m = "╔════════════════\n║ 👮 الأدمن\n║\n"
                for i, (u, _) in enumerate(bot.admin.items(), 1):
                    try:
                        n = bot.client.getContact(u).displayName
                        m += f"║ {i}. {n}\n"
                    except:
                        pass
                bot.client.sendMessage(to, m + "╚════════════════")
        
        elif txt.startswith('addowner') and is_owner(bot, sender):
            for u in get_mentions(msg):
                bot.owner[u] = True
                bot.save()
            bot.client.sendMessage(to, "✅ إضافة أونر")
        
        elif txt.startswith('delowner') and is_owner(bot, sender):
            for u in get_mentions(msg):
                if u in bot.owner and u != sender:
                    del bot.owner[u]
                    bot.save()
            bot.client.sendMessage(to, "✅ حذف أونر")
        
        elif txt.startswith('addadmin') and is_owner(bot, sender):
            for u in get_mentions(msg):
                bot.admin[u] = True
                bot.save()
            bot.client.sendMessage(to, "✅ إضافة أدمن")
        
        elif txt.startswith('deladmin') and is_owner(bot, sender):
            for u in get_mentions(msg):
                if u in bot.admin:
                    del bot.admin[u]
                    bot.save()
            bot.client.sendMessage(to, "✅ حذف أدمن")
        
        elif txt == 'banlist' and is_owner(bot, sender):
            if not bot.banned:
                bot.client.sendMessage(to, "❌ قائمة فارغة")
            else:
                m = "╔════════════════\n║ 🚫 المحظورين\n║\n"
                for i, (u, _) in enumerate(bot.banned.items(), 1):
                    try:
                        n = bot.client.getContact(u).displayName
                        m += f"║ {i}. {n}\n"
                    except:
                        pass
                bot.client.sendMessage(to, m + f"║\n║ {len(bot.banned)} محظور\n╚════════════════")
        
        elif txt == 'clearban' and is_owner(bot, sender):
            bot.banned = {}
            bot.save()
            bot.client.sendMessage(to, "✅ تم مسح القائمة")
        
        elif txt == 'restart' and is_owner(bot, sender):
            bot.client.sendMessage(to, "🔄 إعادة تشغيل...")
            bot.save()
            time.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)
    
    except Exception as e:
        print(f"❌ خطأ: {e}")

# ========== الرئيسي ==========
def main():
    print("\n╔════════════════════════════════════╗")
    print("║   بوت LINE - نظام حماية متقدم      ║")
    print("║   By: Abeer Al-Dosari @ 2025      ║")
    print("╚════════════════════════════════════╝\n")
    
    bot = Bot()
    
    print(f"✅ البوت: {bot.name}")
    print(f"✅ المعرف: {bot.mid}")
    print(f"✅ أونر: {len(bot.owner)}")
    print(f"✅ أدمن: {len(bot.admin)}\n")
    print("🚀 البوت يعمل...\n")
    
    while True:
        try:
            ops = bot.poll.singleTrace(count=50)
            if ops:
                for op in ops:
                    try:
                        if op.type == 5:  # إضافة
                            pass
                        elif op.type == 13:  # دعوة
                            handle_invite(bot, op)
                        elif op.type == 17:  # انضمام
                            handle_join(bot, op)
                        elif op.type == 19:  # طرد
                            handle_kick(bot, op)
                        elif op.type == 11:  # فتح رابط
                            handle_qr(bot, op)
                        elif op.type == 26:  # رسالة
                            handle_cmd(bot, op.message)
                        
                        bot.poll.setRevision(op.revision)
                    except Exception as e:
                        print(f"❌ {e}")
                        continue
        
        except KeyboardInterrupt:
            print("\n👋 توقف...")
            bot.save()
            break
        
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
