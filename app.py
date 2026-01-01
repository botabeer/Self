# -*- coding: utf-8 -*-
"""
بوت عبير - LINE Bot المحسن
Created by: Abeer Al-Dosari @ 2025
All Rights Reserved
نظام حماية متقدم للقروبات مع إدارة متكاملة
"""

from linepy import LINE, OEPoll
from datetime import datetime
import time, json, os, sys

# ========== التهيئة الأساسية ==========
class BotConfig:
    def __init__(self):
        self.bot = LINE()
        self.poll = OEPoll(self.bot)
        self.mid = self.bot.profile.mid
        self.name = self.bot.profile.displayName
        
        # تحميل البيانات
        self.owner = self.load_data('owner.json', [])
        self.admin = self.load_data('admin.json', [])
        self.banned = self.load_data('banned.json', [])
        
        # إعدادات الحماية
        self.settings = {
            'protection': True,
            'kick_protection': True,
            'invite_protection': True,
            'qr_protection': True,
            'cancel_protection': True,
            'bot_protection': True,
            'auto_admin': True,
            'auto_close_qr': True,
            'spam_limit': 5,
            'spam_time': 10
        }
        
        # تتبع السبام
        self.spam_tracker = {}
        self.start_time = time.time()
    
    def load_data(self, filename, default):
        """تحميل البيانات من ملف JSON"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return default
        except:
            return default
    
    def save_data(self):
        """حفظ جميع البيانات"""
        try:
            with open('owner.json', 'w') as f:
                json.dump(self.owner, f)
            with open('admin.json', 'w') as f:
                json.dump(self.admin, f)
            with open('banned.json', 'w') as f:
                json.dump(self.banned, f)
            return True
        except:
            return False

# ========== نظام الحماية ==========
class Protection:
    def __init__(self, config):
        self.config = config
        self.bot = config.bot
    
    def is_bot(self, mid):
        """التحقق من البوتات"""
        try:
            contact = self.bot.getContact(mid)
            return contact.attributes == 1 or 'bot' in contact.displayName.lower()
        except:
            return False
    
    def check_spam(self, sender, group_id):
        """فحص السبام"""
        current_time = time.time()
        key = f"{sender}_{group_id}"
        
        if key not in self.config.spam_tracker:
            self.config.spam_tracker[key] = []
        
        # تنظيف الرسائل القديمة
        self.config.spam_tracker[key] = [
            t for t in self.config.spam_tracker[key]
            if current_time - t < self.config.settings['spam_time']
        ]
        
        self.config.spam_tracker[key].append(current_time)
        
        return len(self.config.spam_tracker[key]) >= self.config.settings['spam_limit']
    
    def kick_user(self, group_id, user_id, reason="مخالفة"):
        """طرد مستخدم مع حظره"""
        try:
            self.bot.kickoutFromGroup(group_id, [user_id])
            self.config.banned.append(user_id)
            self.config.save_data()
            self.bot.sendMessage(group_id, f"⚠️ تم طرد المخالف\nالسبب: {reason}")
            return True
        except:
            return False
    
    def secure_group(self, group_id):
        """تأمين القروب"""
        try:
            group = self.bot.getGroup(group_id)
            group.preventedJoinByTicket = True
            self.bot.updateGroup(group)
            return True
        except:
            return False
    
    def make_admin(self, group_id):
        """جعل البوت أدمن تلقائياً"""
        try:
            group = self.bot.getGroup(group_id)
            if self.config.mid not in [m.mid for m in group.members if hasattr(m, 'memberRole')]:
                # محاولة الحصول على صلاحيات أدمن
                return True
        except:
            return False

# ========== معالج الأحداث ==========
class EventHandler:
    def __init__(self, config, protection):
        self.config = config
        self.bot = config.bot
        self.protection = protection
    
    def handle_kick(self, op):
        """معالجة الطرد"""
        if not self.config.settings['kick_protection']:
            return
        
        group_id = op.param1
        kicker = op.param2
        kicked = op.param3
        
        # إذا تم طرد البوت
        if kicked == self.config.mid:
            if kicker not in self.config.owner:
                try:
                    # إعادة الانضمام
                    group = self.bot.getGroup(group_id)
                    group.preventedJoinByTicket = False
                    self.bot.updateGroup(group)
                    ticket = self.bot.reissueGroupTicket(group_id)
                    self.bot.acceptGroupInvitationByTicket(group_id, ticket)
                    
                    # طرد المعتدي
                    self.protection.kick_user(group_id, kicker, "طرد البوت")
                    self.protection.secure_group(group_id)
                except:
                    pass
        
        # حماية الأعضاء
        elif kicked in self.config.admin or kicked in self.config.owner:
            self.protection.kick_user(group_id, kicker, "طرد أدمن")
    
    def handle_invite(self, op):
        """معالجة الدعوات"""
        if not self.config.settings['invite_protection']:
            return
        
        group_id = op.param1
        inviter = op.param2
        invited = op.param3
        
        # منع دعوة البوتات
        if self.config.settings['bot_protection'] and self.protection.is_bot(invited):
            try:
                self.bot.cancelGroupInvitation(group_id, [invited])
                self.protection.kick_user(group_id, inviter, "دعوة بوت")
            except:
                pass
        
        # منع دعوة المحظورين
        elif invited in self.config.banned:
            try:
                self.bot.cancelGroupInvitation(group_id, [invited])
                self.bot.sendMessage(group_id, "⚠️ هذا العضو محظور")
            except:
                pass
        
        # منع الدعوات غير المصرح بها
        elif inviter not in self.config.admin and inviter not in self.config.owner:
            try:
                self.bot.cancelGroupInvitation(group_id, [invited])
                self.protection.kick_user(group_id, inviter, "دعوة بدون صلاحية")
            except:
                pass
    
    def handle_qr(self, op):
        """معالجة فتح الرابط"""
        if not self.config.settings['qr_protection']:
            return
        
        group_id = op.param1
        opener = op.param2
        
        if opener not in self.config.admin and opener not in self.config.owner:
            try:
                self.protection.secure_group(group_id)
                self.protection.kick_user(group_id, opener, "فتح الرابط")
            except:
                pass
    
    def handle_join(self, op):
        """معالجة الانضمام"""
        group_id = op.param1
        
        # تأمين القروب تلقائياً
        if self.config.settings['auto_close_qr']:
            self.protection.secure_group(group_id)
        
        # محاولة الحصول على صلاحيات أدمن
        if self.config.settings['auto_admin']:
            self.protection.make_admin(group_id)
        
        # رسالة ترحيب
        welcome = f"""╔════════════════
║ 👋 مرحباً بكم في بوت عبير
║ 🛡️ نظام حماية متقدم
║ 
║ الأوامر: اكتب help
║ المطور: Abeer Al-Dosari @ 2025
╚════════════════"""
        self.bot.sendMessage(group_id, welcome)

# ========== معالج الأوامر ==========
class CommandHandler:
    def __init__(self, config, protection):
        self.config = config
        self.bot = config.bot
        self.protection = protection
    
    def is_owner(self, sender):
        return sender in self.config.owner
    
    def is_admin(self, sender):
        return sender in self.config.admin or sender in self.config.owner
    
    def handle_command(self, msg):
        """معالجة الأوامر"""
        text = msg.text.lower().strip()
        sender = msg._from
        to = msg.to if hasattr(msg, 'to') and msg.to else sender
        
        # ========== أوامر عامة ==========
        if text == 'help':
            help_text = """╔════════════════
║ 📋 قائمة الأوامر - بوت عبير
║
║ 🔹 أوامر عامة:
║ ➤ help - عرض الأوامر
║ ➤ status - حالة البوت
║ ➤ speed - سرعة الاستجابة
║ ➤ time - الوقت الحالي
║ ➤ runtime - مدة التشغيل
║
║ 🔹 أوامر الأدمن:
║ ➤ kick @mention - طرد عضو
║ ➤ ban @mention - حظر عضو
║ ➤ unban @mention - فك حظر
║ ➤ protect on/off - الحماية
║ ➤ qrclose - إغلاق الرابط
║ ➤ qropen - فتح الرابط
║ ➤ adminlist - قائمة الأدمن
║
║ 🔹 أوامر الأونر:
║ ➤ addowner @mention - إضافة أونر
║ ➤ delowner @mention - حذف أونر
║ ➤ addadmin @mention - إضافة أدمن
║ ➤ deladmin @mention - حذف أدمن
║ ➤ banlist - المحظورين
║ ➤ clearban - مسح المحظورين
║ ➤ settings - الإعدادات
║ ➤ restart - إعادة تشغيل
║
║ المطور: Abeer Al-Dosari @ 2025
╚════════════════"""
            self.bot.sendMessage(to, help_text)
        
        elif text == 'status':
            uptime = int(time.time() - self.config.start_time)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            
            status = f"""╔════════════════
║ 📊 حالة البوت - {self.config.name}
║
║ 🟢 الحالة: يعمل
║ ⏱️ وقت التشغيل: {hours}س {minutes}د
║ 👥 الأونر: {len(self.config.owner)}
║ 👮 الأدمن: {len(self.config.admin)}
║ 🚫 المحظورين: {len(self.config.banned)}
║
║ 🛡️ الحماية:
║ ➤ الطرد: {'✅' if self.config.settings['kick_protection'] else '❌'}
║ ➤ الدعوات: {'✅' if self.config.settings['invite_protection'] else '❌'}
║ ➤ الرابط: {'✅' if self.config.settings['qr_protection'] else '❌'}
║ ➤ البوتات: {'✅' if self.config.settings['bot_protection'] else '❌'}
║
║ Created by: Abeer Al-Dosari @ 2025
╚════════════════"""
            self.bot.sendMessage(to, status)
        
        elif text == 'speed':
            start = time.time()
            self.bot.sendMessage(to, "⏱️ جاري القياس...")
            elapsed = time.time() - start
            self.bot.sendMessage(to, f"⚡ السرعة: {elapsed:.3f} ثانية")
        
        elif text == 'time':
            now = datetime.now()
            time_text = f"""╔════════════════
║ 🕐 الوقت الحالي
║
║ التاريخ: {now.strftime('%Y-%m-%d')}
║ الوقت: {now.strftime('%H:%M:%S')}
║ اليوم: {now.strftime('%A')}
║
║ بوت عبير @ 2025
╚════════════════"""
            self.bot.sendMessage(to, time_text)
        
        elif text == 'runtime':
            uptime = int(time.time() - self.config.start_time)
            days = uptime // 86400
            hours = (uptime % 86400) // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            
            self.bot.sendMessage(to, f"⏰ مدة التشغيل:\n{days} يوم، {hours} ساعة، {minutes} دقيقة، {seconds} ثانية")
        
        # ========== أوامر الأدمن ==========
        elif text.startswith('kick') and self.is_admin(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target not in self.config.owner:
                        self.protection.kick_user(to, target, "بأمر الأدمن")
        
        elif text.startswith('ban') and self.is_admin(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target not in self.config.banned:
                        self.config.banned.append(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, f"🚫 تم حظر العضو")
        
        elif text.startswith('unban') and self.is_admin(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target in self.config.banned:
                        self.config.banned.remove(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, f"✅ تم فك حظر العضو")
        
        elif text == 'protect on' and self.is_admin(sender):
            for key in ['protection', 'kick_protection', 'invite_protection', 'qr_protection', 'bot_protection']:
                self.config.settings[key] = True
            self.bot.sendMessage(to, "🛡️ تم تفعيل جميع أنظمة الحماية")
        
        elif text == 'protect off' and self.is_admin(sender):
            for key in ['protection', 'kick_protection', 'invite_protection', 'qr_protection', 'bot_protection']:
                self.config.settings[key] = False
            self.bot.sendMessage(to, "⚠️ تم إيقاف جميع أنظمة الحماية")
        
        elif text == 'qrclose' and self.is_admin(sender):
            self.protection.secure_group(to)
            self.bot.sendMessage(to, "✅ تم إغلاق رابط القروب")
        
        elif text == 'qropen' and self.is_admin(sender):
            try:
                group = self.bot.getGroup(to)
                group.preventedJoinByTicket = False
                self.bot.updateGroup(group)
                ticket = self.bot.reissueGroupTicket(to)
                self.bot.sendMessage(to, f"✅ تم فتح الرابط:\nline.me/R/ti/g/{ticket}")
            except:
                self.bot.sendMessage(to, "❌ فشل فتح الرابط")
        
        elif text == 'adminlist' and self.is_admin(sender):
            if not self.config.admin:
                self.bot.sendMessage(to, "❌ لا يوجد أدمن")
            else:
                msg_text = "╔════════════════\n║ 👮 قائمة الأدمن\n║\n"
                for i, mid in enumerate(self.config.admin, 1):
                    try:
                        name = self.bot.getContact(mid).displayName
                        msg_text += f"║ {i}. {name}\n"
                    except:
                        pass
                msg_text += "╚════════════════"
                self.bot.sendMessage(to, msg_text)
        
        # ========== أوامر الأونر ==========
        elif text.startswith('addowner') and self.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target not in self.config.owner:
                        self.config.owner.append(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, "👑 تم إضافة أونر جديد")
        
        elif text.startswith('delowner') and self.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target in self.config.owner and target != sender:
                        self.config.owner.remove(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, "✅ تم حذف الأونر")
        
        elif text.startswith('addadmin') and self.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target not in self.config.admin:
                        self.config.admin.append(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, "👮 تم إضافة أدمن جديد")
        
        elif text.startswith('deladmin') and self.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target in self.config.admin:
                        self.config.admin.remove(target)
                        self.config.save_data()
                        self.bot.sendMessage(to, "✅ تم حذف الأدمن")
        
        elif text == 'banlist' and self.is_owner(sender):
            if not self.config.banned:
                self.bot.sendMessage(to, "❌ قائمة المحظورين فارغة")
            else:
                msg_text = "╔════════════════\n║ 🚫 المحظورين\n║\n"
                for i, mid in enumerate(self.config.banned, 1):
                    try:
                        name = self.bot.getContact(mid).displayName
                        msg_text += f"║ {i}. {name}\n"
                    except:
                        pass
                msg_text += f"║\n║ المجموع: {len(self.config.banned)}\n╚════════════════"
                self.bot.sendMessage(to, msg_text)
        
        elif text == 'clearban' and self.is_owner(sender):
            self.config.banned = []
            self.config.save_data()
            self.bot.sendMessage(to, "✅ تم مسح قائمة المحظورين")
        
        elif text == 'settings' and self.is_owner(sender):
            settings_text = f"""╔════════════════
║ ⚙️ إعدادات البوت
║
║ 🛡️ أنظمة الحماية:
║ ➤ الحماية العامة: {'✅' if self.config.settings['protection'] else '❌'}
║ ➤ حماية الطرد: {'✅' if self.config.settings['kick_protection'] else '❌'}
║ ➤ حماية الدعوات: {'✅' if self.config.settings['invite_protection'] else '❌'}
║ ➤ حماية الرابط: {'✅' if self.config.settings['qr_protection'] else '❌'}
║ ➤ منع البوتات: {'✅' if self.config.settings['bot_protection'] else '❌'}
║
║ 🔧 الإعدادات المتقدمة:
║ ➤ أدمن تلقائي: {'✅' if self.config.settings['auto_admin'] else '❌'}
║ ➤ إغلاق الرابط تلقائياً: {'✅' if self.config.settings['auto_close_qr'] else '❌'}
║ ➤ حد السبام: {self.config.settings['spam_limit']} رسائل
║ ➤ مدة السبام: {self.config.settings['spam_time']} ثانية
║
║ Created by: Abeer Al-Dosari @ 2025
╚════════════════"""
            self.bot.sendMessage(to, settings_text)
        
        elif text == 'restart' and self.is_owner(sender):
            self.bot.sendMessage(to, "🔄 جاري إعادة التشغيل...")
            self.config.save_data()
            time.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)

# ========== البوت الرئيسي ==========
def main():
    print("╔════════════════════════════════════╗")
    print("║   بوت عبير - LINE Bot              ║")
    print("║   Created by: Abeer Al-Dosari      ║")
    print("║   Year: 2025                       ║")
    print("║   Status: Starting...              ║")
    print("╚════════════════════════════════════╝")
    
    # تهيئة البوت
    config = BotConfig()
    protection = Protection(config)
    event_handler = EventHandler(config, protection)
    command_handler = CommandHandler(config, protection)
    
    print(f"\n✅ تم تسجيل الدخول: {config.name}")
    print(f"✅ معرف البوت: {config.mid}")
    print(f"✅ الأونر: {len(config.owner)}")
    print(f"✅ الأدمن: {len(config.admin)}")
    print("\n🚀 البوت يعمل الآن...\n")
    
    # الحلقة الرئيسية
    while True:
        try:
            ops = config.poll.singleTrace(count=50)
            if ops:
                for op in ops:
                    try:
                        # معالجة الأحداث
                        if op.type == 19:  # طرد
                            event_handler.handle_kick(op)
                        
                        elif op.type == 13:  # دعوة
                            event_handler.handle_invite(op)
                        
                        elif op.type == 11:  # فتح رابط
                            event_handler.handle_qr(op)
                        
                        elif op.type == 17:  # انضمام عضو
                            event_handler.handle_join(op)
                        
                        elif op.type == 26:  # رسالة
                            msg = op.message
                            if msg.text:
                                # فحص السبام
                                if msg.toType == 2:  # في قروب
                                    if protection.check_spam(msg._from, msg.to):
                                        protection.kick_user(msg.to, msg._from, "سبام")
                                        continue
                                
                                # معالجة الأوامر
                                command_handler.handle_command(msg)
                        
                        # تحديث المراجعة
                        config.poll.setRevision(op.revision)
                    
                    except Exception as e:
                        print(f"❌ خطأ في معالجة العملية: {e}")
                        continue
        
        except KeyboardInterrupt:
            print("\n\n👋 إيقاف البوت...")
            config.save_data()
            break
        
        except Exception as e:
            print(f"❌ خطأ في الحلقة الرئيسية: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
