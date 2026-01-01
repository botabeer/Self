# -*- coding: utf-8 -*-
"""
بوت LINE المحسّن - متوافق مع LINE v3
Created by: Abeer Al-Dosari @ 2025
نظام حماية متقدم للمجموعات
"""

from linepy import LINE, OEPoll
from datetime import datetime
import time, json, os, sys, ast

# ========== إعدادات البوت ==========
class BotConfig:
    def __init__(self):
        try:
            self.bot = LINE()
            self.poll = OEPoll(self.bot)
            self.mid = self.bot.profile.mid
            self.name = self.bot.profile.displayName
        except Exception as e:
            print(f"❌ فشل تسجيل الدخول: {e}")
            sys.exit(1)
        
        # تحميل البيانات
        self.owner = self.load_json('owner.json', {})
        self.admin = self.load_json('admin.json', {})
        self.banned = self.load_json('banned.json', {})
        
        # إعدادات الحماية
        self.settings = {
            'protect': True,
            'kick_protection': True,
            'invite_protection': True,
            'qr_protection': True,
            'cancel_protection': True,
            'bot_protection': True,
            'auto_join': True,
            'auto_add': True,
            'auto_close_qr': True,
            'lang': 'AR'
        }
        
        self.start_time = time.time()
        print(f"✅ تم تهيئة البوت: {self.name}")
    
    def load_json(self, filename, default):
        """تحميل ملف JSON"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if data else default
            return default
        except:
            return default
    
    def save_data(self):
        """حفظ البيانات"""
        try:
            with open('owner.json', 'w', encoding='utf-8') as f:
                json.dump(self.owner, f, ensure_ascii=False, indent=2)
            with open('admin.json', 'w', encoding='utf-8') as f:
                json.dump(self.admin, f, ensure_ascii=False, indent=2)
            with open('banned.json', 'w', encoding='utf-8') as f:
                json.dump(self.banned, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ فشل الحفظ: {e}")
            return False

# ========== نظام الحماية ==========
class Protection:
    def __init__(self, config):
        self.config = config
        self.bot = config.bot
    
    def kick_and_ban(self, group_id, user_id, reason=""):
        """طرد وحظر المستخدم"""
        try:
            self.bot.kickoutFromGroup(group_id, [user_id])
            self.config.banned[user_id] = True
            self.config.save_data()
            if reason:
                self.bot.sendMessage(group_id, f"⚠️ {reason}\n🚫 تم طرد وحظر المخالف")
            return True
        except Exception as e:
            print(f"❌ فشل الطرد: {e}")
            return False
    
    def secure_group(self, group_id):
        """إغلاق رابط المجموعة"""
        try:
            group = self.bot.getGroup(group_id)
            if not group.preventedJoinByTicket:
                group.preventedJoinByTicket = True
                self.bot.updateGroup(group)
            return True
        except:
            return False
    
    def rejoin_group(self, group_id):
        """إعادة الانضمام للمجموعة"""
        try:
            group = self.bot.getGroup(group_id)
            group.preventedJoinByTicket = False
            self.bot.updateGroup(group)
            ticket = self.bot.reissueGroupTicket(group_id)
            self.bot.acceptGroupInvitationByTicket(group_id, ticket)
            group.preventedJoinByTicket = True
            self.bot.updateGroup(group)
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
        """معالجة الطرد - Type 19"""
        if not self.config.settings['kick_protection']:
            return
        
        try:
            group_id = op.param1
            kicker = op.param2
            kicked = op.param3
            
            # إذا تم طرد البوت نفسه
            if kicked == self.config.mid:
                if kicker not in self.config.owner:
                    time.sleep(0.5)
                    if self.protection.rejoin_group(group_id):
                        time.sleep(0.5)
                        self.protection.kick_and_ban(group_id, kicker, "طرد البوت")
                return
            
            # حماية الأونر والأدمن
            if kicked in self.config.owner or kicked in self.config.admin:
                if kicker not in self.config.owner:
                    self.protection.kick_and_ban(group_id, kicker, "طرد أدمن/أونر")
                    # إعادة دعوة المطرود
                    try:
                        self.bot.inviteIntoGroup(group_id, [kicked])
                    except:
                        pass
        except Exception as e:
            print(f"❌ خطأ في handle_kick: {e}")
    
    def handle_invite(self, op):
        """معالجة الدعوات - Type 13"""
        if not self.config.settings['invite_protection']:
            return
        
        try:
            group_id = op.param1
            inviter = op.param2
            invited = op.param3
            
            # قبول دعوة البوت تلقائياً
            if invited == self.config.mid:
                if self.config.settings['auto_join']:
                    self.bot.acceptGroupInvitation(group_id)
                    time.sleep(0.5)
                    if self.config.settings['auto_close_qr']:
                        self.protection.secure_group(group_id)
                return
            
            # منع دعوة المحظورين
            if invited in self.config.banned:
                self.bot.cancelGroupInvitation(group_id, [invited])
                self.bot.sendMessage(group_id, "⚠️ هذا الشخص محظور")
                return
            
            # السماح للأونر والأدمن بالدعوة
            if inviter in self.config.owner or inviter in self.config.admin:
                return
            
            # طرد من يدعو بدون صلاحية
            self.bot.cancelGroupInvitation(group_id, [invited])
            self.protection.kick_and_ban(group_id, inviter, "دعوة بدون صلاحية")
        except Exception as e:
            print(f"❌ خطأ في handle_invite: {e}")
    
    def handle_qr(self, op):
        """معالجة فتح الرابط - Type 11"""
        if not self.config.settings['qr_protection']:
            return
        
        try:
            group_id = op.param1
            opener = op.param2
            
            # السماح للأونر والأدمن
            if opener in self.config.owner or opener in self.config.admin:
                return
            
            # إغلاق الرابط وطرد الفاعل
            self.protection.secure_group(group_id)
            self.protection.kick_and_ban(group_id, opener, "فتح رابط المجموعة")
        except Exception as e:
            print(f"❌ خطأ في handle_qr: {e}")
    
    def handle_cancel(self, op):
        """معالجة إلغاء الدعوات - Type 32"""
        if not self.config.settings['cancel_protection']:
            return
        
        try:
            group_id = op.param1
            canceller = op.param2
            
            if canceller not in self.config.owner and canceller not in self.config.admin:
                self.protection.kick_and_ban(group_id, canceller, "إلغاء دعوة")
        except Exception as e:
            print(f"❌ خطأ في handle_cancel: {e}")
    
    def handle_join(self, op):
        """معالجة انضمام عضو - Type 17"""
        try:
            group_id = op.param1
            joiner = op.param2
            
            # إذا انضم البوت
            if joiner == self.config.mid:
                if self.config.settings['auto_close_qr']:
                    time.sleep(1)
                    self.protection.secure_group(group_id)
                
                welcome = """╔════════════════════
║ 🛡️ بوت الحماية المتقدم
║ 
║ 📝 للأوامر اكتب: help
║ 👨‍💻 المطور: Abeer Al-Dosari
╚════════════════════"""
                self.bot.sendMessage(group_id, welcome)
        except Exception as e:
            print(f"❌ خطأ في handle_join: {e}")
    
    def handle_add(self, op):
        """معالجة الإضافة - Type 5"""
        if self.config.settings['auto_add']:
            try:
                user_id = op.param1
                contact = self.bot.getContact(user_id)
                self.bot.sendMessage(user_id, f"👋 مرحباً {contact.displayName}\nشكراً لإضافتي")
            except:
                pass

# ========== معالج الأوامر ==========
class CommandHandler:
    def __init__(self, config, protection):
        self.config = config
        self.bot = config.bot
        self.protection = protection
    
    def is_owner(self, user_id):
        return user_id in self.config.owner
    
    def is_admin(self, user_id):
        return user_id in self.config.admin or user_id in self.config.owner
    
    def get_mentions(self, msg):
        """استخراج المنشنات"""
        try:
            if 'MENTION' in msg.contentMetadata:
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                return [m['M'] for m in mentions['MENTIONEES']]
        except:
            pass
        return []
    
    def handle_command(self, msg):
        """معالجة الأوامر"""
        try:
            if not msg.text:
                return
            
            text = msg.text.lower().strip()
            sender = msg._from
            to = msg.to if msg.toType == 2 else sender
            
            # ========== أوامر عامة ==========
            if text == 'help':
                help_text = """╔════════════════════
║ 📋 قائمة الأوامر
║
║ 🔹 عامة:
║ • help - الأوامر
║ • status - الحالة
║ • speed - السرعة
║ • time - الوقت
║ • runtime - مدة التشغيل
║
║ 🔹 أدمن:
║ • kick @mention - طرد
║ • ban @mention - حظر
║ • unban @mention - فك حظر
║ • protect on/off - الحماية
║ • qrclose - إغلاق الرابط
║ • qropen - فتح الرابط
║ • adminlist - الأدمن
║
║ 🔹 أونر فقط:
║ • addowner @mention
║ • delowner @mention
║ • addadmin @mention
║ • deladmin @mention
║ • banlist - المحظورين
║ • clearban - مسح الحظر
║ • restart - إعادة تشغيل
║
╚════════════════════"""
                self.bot.sendMessage(to, help_text)
            
            elif text == 'status':
                uptime = int(time.time() - self.config.start_time)
                hours = uptime // 3600
                mins = (uptime % 3600) // 60
                
                status = f"""╔════════════════════
║ 📊 حالة البوت
║
║ 🤖 الاسم: {self.config.name}
║ ⏱️ التشغيل: {hours}س {mins}د
║ 👑 الأونر: {len(self.config.owner)}
║ 👮 الأدمن: {len(self.config.admin)}
║ 🚫 المحظورين: {len(self.config.banned)}
║
║ 🛡️ الحماية:
║ • الطرد: {'✅' if self.config.settings['kick_protection'] else '❌'}
║ • الدعوات: {'✅' if self.config.settings['invite_protection'] else '❌'}
║ • الرابط: {'✅' if self.config.settings['qr_protection'] else '❌'}
║ • الإلغاء: {'✅' if self.config.settings['cancel_protection'] else '❌'}
║
╚════════════════════"""
                self.bot.sendMessage(to, status)
            
            elif text == 'speed':
                start = time.time()
                self.bot.sendMessage(to, "⏱️ جاري القياس...")
                elapsed = time.time() - start
                self.bot.sendMessage(to, f"⚡ السرعة: {elapsed:.3f}s")
            
            elif text == 'time':
                now = datetime.now()
                time_text = f"""╔════════════════════
║ 🕐 الوقت الحالي
║
║ 📅 {now.strftime('%Y-%m-%d')}
║ ⏰ {now.strftime('%H:%M:%S')}
║ 📆 {now.strftime('%A')}
║
╚════════════════════"""
                self.bot.sendMessage(to, time_text)
            
            elif text == 'runtime':
                uptime = int(time.time() - self.config.start_time)
                days = uptime // 86400
                hours = (uptime % 86400) // 3600
                mins = (uptime % 3600) // 60
                secs = uptime % 60
                self.bot.sendMessage(to, f"⏰ مدة التشغيل:\n{days}ي {hours}س {mins}د {secs}ث")
            
            # ========== أوامر الأدمن ==========
            elif text.startswith('kick') and self.is_admin(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    if target not in self.config.owner:
                        self.protection.kick_and_ban(to, target, "بأمر الأدمن")
            
            elif text.startswith('ban') and self.is_admin(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    if target not in self.config.banned:
                        self.config.banned[target] = True
                        self.config.save_data()
                self.bot.sendMessage(to, "✅ تم حظر العضو")
            
            elif text.startswith('unban') and self.is_admin(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    if target in self.config.banned:
                        del self.config.banned[target]
                        self.config.save_data()
                self.bot.sendMessage(to, "✅ تم فك حظر العضو")
            
            elif text == 'protect on' and self.is_admin(sender):
                for key in ['protect', 'kick_protection', 'invite_protection', 'qr_protection', 'cancel_protection']:
                    self.config.settings[key] = True
                self.bot.sendMessage(to, "✅ تم تفعيل جميع أنظمة الحماية")
            
            elif text == 'protect off' and self.is_admin(sender):
                for key in ['protect', 'kick_protection', 'invite_protection', 'qr_protection', 'cancel_protection']:
                    self.config.settings[key] = False
                self.bot.sendMessage(to, "⚠️ تم إيقاف جميع أنظمة الحماية")
            
            elif text == 'qrclose' and self.is_admin(sender):
                if self.protection.secure_group(to):
                    self.bot.sendMessage(to, "✅ تم إغلاق رابط المجموعة")
            
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
                    msg_text = "╔════════════════════\n║ 👮 قائمة الأدمن\n║\n"
                    for i, (mid, _) in enumerate(self.config.admin.items(), 1):
                        try:
                            name = self.bot.getContact(mid).displayName
                            msg_text += f"║ {i}. {name}\n"
                        except:
                            pass
                    msg_text += "╚════════════════════"
                    self.bot.sendMessage(to, msg_text)
            
            # ========== أوامر الأونر ==========
            elif text.startswith('addowner') and self.is_owner(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    self.config.owner[target] = True
                    self.config.save_data()
                self.bot.sendMessage(to, "✅ تم إضافة أونر جديد")
            
            elif text.startswith('delowner') and self.is_owner(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    if target in self.config.owner and target != sender:
                        del self.config.owner[target]
                        self.config.save_data()
                self.bot.sendMessage(to, "✅ تم حذف الأونر")
            
            elif text.startswith('addadmin') and self.is_owner(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    self.config.admin[target] = True
                    self.config.save_data()
                self.bot.sendMessage(to, "✅ تم إضافة أدمن جديد")
            
            elif text.startswith('deladmin') and self.is_owner(sender):
                mentions = self.get_mentions(msg)
                for target in mentions:
                    if target in self.config.admin:
                        del self.config.admin[target]
                        self.config.save_data()
                self.bot.sendMessage(to, "✅ تم حذف الأدمن")
            
            elif text == 'banlist' and self.is_owner(sender):
                if not self.config.banned:
                    self.bot.sendMessage(to, "❌ قائمة المحظورين فارغة")
                else:
                    msg_text = "╔════════════════════\n║ 🚫 المحظورين\n║\n"
                    for i, (mid, _) in enumerate(self.config.banned.items(), 1):
                        try:
                            name = self.bot.getContact(mid).displayName
                            msg_text += f"║ {i}. {name}\n"
                        except:
                            pass
                    msg_text += f"║\n║ المجموع: {len(self.config.banned)}\n╚════════════════════"
                    self.bot.sendMessage(to, msg_text)
            
            elif text == 'clearban' and self.is_owner(sender):
                self.config.banned = {}
                self.config.save_data()
                self.bot.sendMessage(to, "✅ تم مسح قائمة المحظورين")
            
            elif text == 'restart' and self.is_owner(sender):
                self.bot.sendMessage(to, "🔄 جاري إعادة التشغيل...")
                self.config.save_data()
                time.sleep(2)
                os.execl(sys.executable, sys.executable, *sys.argv)
        
        except Exception as e:
            print(f"❌ خطأ في الأوامر: {e}")

# ========== البرنامج الرئيسي ==========
def main():
    print("╔════════════════════════════════════╗")
    print("║   بوت LINE المحسّن v3.0            ║")
    print("║   Created by: Abeer Al-Dosari      ║")
    print("║   Year: 2025                       ║")
    print("╚════════════════════════════════════╝\n")
    
    # تهيئة البوت
    config = BotConfig()
    protection = Protection(config)
    event_handler = EventHandler(config, protection)
    command_handler = CommandHandler(config, protection)
    
    print(f"✅ البوت: {config.name}")
    print(f"✅ المعرف: {config.mid}")
    print(f"✅ الأونر: {len(config.owner)}")
    print(f"✅ الأدمن: {len(config.admin)}\n")
    print("🚀 البوت يعمل الآن...\n")
    
    # الحلقة الرئيسية
    while True:
        try:
            ops = config.poll.singleTrace(count=50)
            if ops:
                for op in ops:
                    try:
                        # الأحداث
                        if op.type == 5:  # إضافة صديق
                            event_handler.handle_add(op)
                        
                        elif op.type == 13:  # دعوة
                            event_handler.handle_invite(op)
                        
                        elif op.type == 17:  # انضمام
                            event_handler.handle_join(op)
                        
                        elif op.type == 19:  # طرد
                            event_handler.handle_kick(op)
                        
                        elif op.type == 11:  # فتح رابط
                            event_handler.handle_qr(op)
                        
                        elif op.type == 32:  # إلغاء دعوة
                            event_handler.handle_cancel(op)
                        
                        elif op.type == 26:  # رسالة
                            command_handler.handle_command(op.message)
                        
                        # تحديث
                        config.poll.setRevision(op.revision)
                    
                    except Exception as e:
                        print(f"❌ خطأ في العملية: {e}")
                        continue
        
        except KeyboardInterrupt:
            print("\n\n👋 إيقاف البوت...")
            config.save_data()
            break
        
        except Exception as e:
            print(f"❌ خطأ في الحلقة: {e}")
            time.sleep(1)
            continue

if __name__ == "__main__":
    main()
