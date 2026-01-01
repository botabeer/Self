# -*- coding: utf-8 -*-
"""
بوت LINE للحماية - نسخة Worker
تعمل مع linepy (بدون حاجة لـ Flask)
مناسبة لـ Render Background Worker
"""

from linepy import LINE, OEPoll
import time
import json
import os
import sys
from datetime import datetime

# ========== التهيئة ==========
class ProtectionBot:
    def __init__(self):
        print("\n" + "="*50)
        print("🤖 بوت LINE للحماية - نسخة Worker")
        print("="*50)
        
        # تسجيل الدخول
        try:
            token = os.getenv('LINE_TOKEN', '')
            email = os.getenv('LINE_EMAIL', '')
            password = os.getenv('LINE_PASSWORD', '')
            
            if token:
                print("🔐 تسجيل الدخول بالـ Token...")
                self.client = LINE(token)
            elif email and password:
                print("🔐 تسجيل الدخول بالبريد...")
                self.client = LINE(email, password)
            else:
                print("❌ لم يتم تعيين بيانات تسجيل الدخول!")
                print("   أضف: LINE_TOKEN أو (LINE_EMAIL + LINE_PASSWORD)")
                sys.exit(1)
            
            self.poll = OEPoll(self.client)
            self.mid = self.client.profile.mid
            self.name = self.client.profile.displayName
            
            print(f"✅ تم تسجيل الدخول: {self.name}")
            print(f"✅ المعرف: {self.mid}")
        
        except Exception as e:
            print(f"❌ فشل تسجيل الدخول: {e}")
            sys.exit(1)
        
        # تحميل البيانات
        self.owners = self.load_json('owners.json', {})
        self.admins = self.load_json('admins.json', {})
        self.banned = self.load_json('banned.json', {})
        
        # الإعدادات
        self.protect = True
        self.kick_protect = True
        self.invite_protect = True
        self.qr_protect = True
        self.auto_join = True
        self.welcome = True
        
        self.start_time = time.time()
        
        print(f"✅ مالكين: {len(self.owners)}")
        print(f"✅ أدمن: {len(self.admins)}")
        print(f"✅ محظورين: {len(self.banned)}")
        print("="*50 + "\n")
    
    def load_json(self, filename, default):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f) or default
            return default
        except:
            return default
    
    def save_data(self):
        try:
            with open('owners.json', 'w', encoding='utf-8') as f:
                json.dump(self.owners, f, indent=2, ensure_ascii=False)
            with open('admins.json', 'w', encoding='utf-8') as f:
                json.dump(self.admins, f, indent=2, ensure_ascii=False)
            with open('banned.json', 'w', encoding='utf-8') as f:
                json.dump(self.banned, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
    
    def is_owner(self, uid):
        return uid in self.owners
    
    def is_admin(self, uid):
        return uid in self.owners or uid in self.admins
    
    def get_runtime(self):
        t = int(time.time() - self.start_time)
        h = t // 3600
        m = (t % 3600) // 60
        s = t % 60
        return f"{h}س {m}د {s}ث"
    
    def send(self, to, msg):
        try:
            self.client.sendMessage(to, msg)
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
    
    # ========== معالجات الحماية ==========
    def handle_kick(self, op):
        """حماية من الطرد"""
        if not self.kick_protect:
            return
        
        try:
            gid = op.param1
            kicker = op.param2
            kicked = op.param3
            
            # إذا طردوا البوت
            if kicked == self.mid:
                if not self.is_owner(kicker):
                    print(f"⚠️ تم طرد البوت من {gid} بواسطة {kicker}")
                    # محاولة العودة وطرد المعتدي
                    time.sleep(1)
                    # هنا تحتاج إلى منطق إعادة الانضمام
                    self.banned[kicker] = True
                    self.save_data()
            
            # إذا طردوا أدمن/مالك
            elif self.is_admin(kicked):
                if not self.is_owner(kicker):
                    print(f"⚠️ طرد أدمن في {gid}")
                    self.client.kickoutFromGroup(gid, [kicker])
                    self.banned[kicker] = True
                    self.save_data()
                    self.send(gid, "⚠️ تم طرد المعتدي تلقائياً")
                    # إعادة دعوة المطرود
                    try:
                        self.client.inviteIntoGroup(gid, [kicked])
                    except:
                        pass
        
        except Exception as e:
            print(f"❌ خطأ handle_kick: {e}")
    
    def handle_invite(self, op):
        """حماية الدعوات"""
        try:
            gid = op.param1
            inviter = op.param2
            invited = op.param3
            
            # إذا دعوا البوت
            if invited == self.mid:
                if self.auto_join:
                    self.client.acceptGroupInvitation(gid)
                    time.sleep(1)
                    self.send(gid, "✅ مرحباً! أنا بوت الحماية\nالأوامر: help")
                return
            
            # التحقق من المحظورين
            if invited in self.banned:
                self.client.cancelGroupInvitation(gid, [invited])
                self.send(gid, "⚠️ عضو محظور - تم إلغاء الدعوة")
                return
            
            # حماية الدعوات
            if self.invite_protect:
                if not self.is_admin(inviter):
                    self.client.cancelGroupInvitation(gid, [invited])
                    self.client.kickoutFromGroup(gid, [inviter])
                    self.banned[inviter] = True
                    self.save_data()
                    self.send(gid, "⚠️ دعوة غير مصرح بها")
        
        except Exception as e:
            print(f"❌ خطأ handle_invite: {e}")
    
    def handle_qr(self, op):
        """حماية الرابط"""
        if not self.qr_protect:
            return
        
        try:
            gid = op.param1
            opener = op.param2
            
            if not self.is_admin(opener):
                # إغلاق الرابط
                group = self.client.getGroup(gid)
                group.preventedJoinByTicket = True
                self.client.updateGroup(group)
                
                # طرد الفاعل
                self.client.kickoutFromGroup(gid, [opener])
                self.banned[opener] = True
                self.save_data()
                self.send(gid, "⚠️ تم إغلاق الرابط وطرد المعتدي")
        
        except Exception as e:
            print(f"❌ خطأ handle_qr: {e}")
    
    # ========== معالج الأوامر ==========
    def handle_command(self, msg):
        try:
            text = msg.text
            if not text:
                return
            
            text = text.strip()
            cmd = text.lower()
            sender = msg._from
            to = msg.to if msg.toType == 2 else sender
            
            # الأوامر
            if cmd == 'help' or cmd == 'الأوامر':
                help_txt = """╔════════════════
║ 🤖 بوت الحماية
║
║ 📋 عامة:
║ • help - الأوامر
║ • status - الحالة
║ • time - الوقت
║ • ping - اختبار
║
║ 👮 أدمن:
║ • protect on/off
║ • kick @user
║ • ban @user
║ • adminlist
║
║ 👑 مالك:
║ • addadmin USER_ID
║ • deladmin USER_ID
║ • banlist
║ • clearban
║
╚════════════════"""
                self.send(to, help_txt)
            
            elif cmd == 'status' or cmd == 'الحالة':
                status = f"""╔════════════════
║ 📊 الحالة
║
║ ⏰ {self.get_runtime()}
║ 👑 مالكين: {len(self.owners)}
║ 👮 أدمن: {len(self.admins)}
║ 🚫 محظورين: {len(self.banned)}
║
║ 🛡️ الحماية:
║ • طرد: {'✅' if self.kick_protect else '❌'}
║ • دعوات: {'✅' if self.invite_protect else '❌'}
║ • رابط: {'✅' if self.qr_protect else '❌'}
║
╚════════════════"""
                self.send(to, status)
            
            elif cmd == 'time' or cmd == 'الوقت':
                now = datetime.now()
                self.send(to, f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            elif cmd == 'ping':
                self.send(to, "🏓 Pong!")
            
            elif cmd == 'protect on' and self.is_admin(sender):
                self.protect = self.kick_protect = self.invite_protect = self.qr_protect = True
                self.send(to, "✅ تم تفعيل الحماية")
            
            elif cmd == 'protect off' and self.is_admin(sender):
                self.protect = self.kick_protect = self.invite_protect = self.qr_protect = False
                self.send(to, "⚠️ تم إيقاف الحماية")
            
            elif cmd == 'adminlist' and self.is_admin(sender):
                if not self.admins:
                    self.send(to, "❌ لا يوجد أدمن")
                else:
                    msg_txt = "╔════════════════\n║ 👮 الأدمن\n║\n"
                    for i, aid in enumerate(self.admins.keys(), 1):
                        try:
                            name = self.client.getContact(aid).displayName
                            msg_txt += f"║ {i}. {name}\n"
                        except:
                            msg_txt += f"║ {i}. {aid}\n"
                    msg_txt += "╚════════════════"
                    self.send(to, msg_txt)
            
            elif cmd.startswith('addadmin') and self.is_owner(sender):
                parts = text.split()
                if len(parts) == 2:
                    uid = parts[1]
                    self.admins[uid] = True
                    self.save_data()
                    self.send(to, "✅ تمت إضافة أدمن")
                else:
                    self.send(to, "📝 استخدم: addadmin USER_ID")
            
            elif cmd.startswith('deladmin') and self.is_owner(sender):
                parts = text.split()
                if len(parts) == 2:
                    uid = parts[1]
                    if uid in self.admins:
                        del self.admins[uid]
                        self.save_data()
                        self.send(to, "✅ تم حذف الأدمن")
                else:
                    self.send(to, "📝 استخدم: deladmin USER_ID")
            
            elif cmd == 'banlist' and self.is_owner(sender):
                if not self.banned:
                    self.send(to, "❌ قائمة فارغة")
                else:
                    msg_txt = f"╔════════════════\n║ 🚫 المحظورين ({len(self.banned)})\n║\n"
                    for i, bid in enumerate(list(self.banned.keys())[:20], 1):
                        try:
                            name = self.client.getContact(bid).displayName
                            msg_txt += f"║ {i}. {name}\n"
                        except:
                            msg_txt += f"║ {i}. {bid[:10]}...\n"
                    msg_txt += "╚════════════════"
                    self.send(to, msg_txt)
            
            elif cmd == 'clearban' and self.is_owner(sender):
                self.banned = {}
                self.save_data()
                self.send(to, "✅ تم مسح القائمة")
        
        except Exception as e:
            print(f"❌ خطأ handle_command: {e}")
    
    # ========== الحلقة الرئيسية ==========
    def run(self):
        print("🚀 البوت يعمل...\n")
        
        while True:
            try:
                ops = self.poll.singleTrace(count=50)
                
                if ops:
                    for op in ops:
                        try:
                            # [13] دعوة
                            if op.type == 13:
                                self.handle_invite(op)
                            
                            # [19] طرد
                            elif op.type == 19:
                                self.handle_kick(op)
                            
                            # [11] فتح رابط
                            elif op.type == 11:
                                self.handle_qr(op)
                            
                            # [26] رسالة نصية
                            elif op.type == 26:
                                if op.message and op.message.text:
                                    self.handle_command(op.message)
                            
                            # تحديث المراجعة
                            self.poll.setRevision(op.revision)
                        
                        except Exception as e:
                            print(f"❌ خطأ في معالجة العملية: {e}")
                            continue
            
            except KeyboardInterrupt:
                print("\n👋 توقف البوت...")
                self.save_data()
                break
            
            except Exception as e:
                print(f"❌ خطأ في الحلقة: {e}")
                time.sleep(2)

# ========== التشغيل ==========
if __name__ == "__main__":
    bot = ProtectionBot()
    bot.run()
