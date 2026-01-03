#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ بوت حماية LINE - نسخة عربية
⚠️ استخدم حساب ثانوي فقط
📝 Self-Bot للحماية والإدارة
"""

import json
import time
import os
from datetime import datetime

# ========== فحص المكتبات ==========
print("🔍 جاري فحص المكتبات...")
try:
    from linepy import LINE, OEPoll
    print("✅ linepy جاهز")
except ImportError:
    print("\n❌ خطأ: مكتبة linepy غير مثبتة!\n")
    print("📥 قم بتشغيل الأمر التالي:")
    print("   pip install git+https://github.com/dyseo/linepy.git\n")
    input("اضغط Enter للخروج...")
    exit(1)

# ========== البيانات ==========
class Database:
    def __init__(self):
        self.file = 'bot_data.json'
        self.load()
    
    def load(self):
        """تحميل البيانات"""
        default = {
            'owners': [],      # المالكين
            'admins': [],      # الأدمنز
            'banned': [],      # المحظورين
            'protect': {
                'kick': True,     # حماية الطرد
                'invite': True,   # حماية الدعوة
                'qr': True,       # حماية الرابط
                'cancel': True    # حماية الإلغاء
            },
            'auto': {
                'add': True,      # قبول الإضافة تلقائياً
                'join': True,     # الانضمام تلقائياً
                'read': True      # قراءة الرسائل تلقائياً
            }
        }
        
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                # إضافة المفاتيح المفقودة
                for key in default:
                    if key not in self.data:
                        self.data[key] = default[key]
            except:
                self.data = default
        else:
            self.data = default
        
        self.save()
    
    def save(self):
        """حفظ البيانات"""
        try:
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
            return False
    
    def is_owner(self, mid):
        return mid in self.data['owners']
    
    def is_admin(self, mid):
        return mid in self.data['owners'] or mid in self.data['admins']
    
    def is_banned(self, mid):
        return mid in self.data['banned']

db = Database()

# ========== التسجيل ==========
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print("="*60)
    print("🛡️  بوت حماية LINE - نسخة عربية")
    print("="*60)
    print("⚠️  استخدم حساب ثانوي - ليس الحساب الرئيسي!")
    print("="*60)

def login():
    """تسجيل الدخول"""
    clear()
    banner()
    
    token_file = 'token.txt'
    
    # محاولة Token المحفوظ
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                token = f.read().strip()
            
            print("\n🔐 تسجيل الدخول بـ Token...")
            client = LINE(token)
            print(f"✅ مرحباً: {client.profile.displayName}")
            return client
        except:
            print("❌ Token منتهي، سجل دخول جديد")
            os.remove(token_file)
    
    # تسجيل جديد
    print("\n📧 تسجيل الدخول")
    print("-"*60)
    
    while True:
        email = input("\n📧 Email: ").strip()
        password = input("🔑 Password: ").strip()
        
        if not email or not password:
            print("❌ أدخل Email و Password!")
            continue
        
        try:
            print("\n⏳ جاري التسجيل...")
            client = LINE(email, password)
            
            # حفظ Token
            with open(token_file, 'w') as f:
                f.write(client.authToken)
            
            print(f"\n✅ نجح التسجيل!")
            print(f"👤 الاسم: {client.profile.displayName}")
            print(f"💾 Token محفوظ في: {token_file}")
            return client
            
        except Exception as e:
            print(f"\n❌ فشل: {e}")
            print("\n💡 تأكد من:")
            print("  • Email/Password صحيح")
            print("  • التحقق بخطوتين معطّل")
            
            if input("\nحاول مرة أخرى؟ (y/n): ").lower() != 'y':
                exit(0)

# تسجيل الدخول
client = login()
oepoll = OEPoll(client)
my_mid = client.profile.mid

# إضافة نفسك كـ Owner
if my_mid not in db.data['owners']:
    db.data['owners'].append(my_mid)
    db.save()

clear()
banner()
print(f"\n✅ البوت جاهز!")
print(f"👤 {client.profile.displayName}")
print(f"🆔 {my_mid}")
print(f"👑 Owners: {len(db.data['owners'])}")
print(f"👮 Admins: {len(db.data['admins'])}")
print(f"🚫 Banned: {len(db.data['banned'])}")
print("\n" + "="*60)

# ========== قائمة الأوامر ==========
def help_msg():
    return """╔═══════════════════════════
║ 🛡️ أوامر البوت
║
║ 📋 عامة:
║ ├ الأوامر - هذه القائمة
║ ├ معلوماتي - بياناتك
║ ├ السرعة - سرعة البوت
║ ├ الحالة - حالة الحماية
║ ├ الوقت - التاريخ والوقت
║
║ 🛡️ الحماية (مالك):
║ ├ تفعيل_الحماية
║ ├ ايقاف_الحماية
║ ├ تفعيل_حماية_الطرد
║ ├ ايقاف_حماية_الطرد
║ ├ تفعيل_حماية_الدعوة
║ ├ ايقاف_حماية_الدعوة
║ ├ تفعيل_حماية_الرابط
║ ├ ايقاف_حماية_الرابط
║
║ 👥 المجموعة (أدمن):
║ ├ معلومات_المجموعة
║ ├ الاعضاء - قائمة الأعضاء
║ ├ طرد @منشن
║ ├ طرد_الكل (مالك فقط)
║ ├ دعوة @منشن
║ ├ فتح_الرابط
║ ├ اغلاق_الرابط
║ ├ جلب_الرابط
║ ├ مغادرة
║
║ 👮 الصلاحيات (مالك):
║ ├ اضافة_ادمن @منشن
║ ├ حذف_ادمن @منشن
║ ├ قائمة_الادمنز
║ ├ حظر @منشن
║ ├ الغاء_حظر @منشن
║ ├ قائمة_المحظورين
║
╚═══════════════════════════"""

# ========== معالج الأحداث ==========
def handle_op(op):
    """معالجة الأحداث"""
    try:
        # [5] إضافة صديق
        if op.type == 5:
            if db.data['auto']['add']:
                try:
                    contact = client.getContact(op.param1)
                    client.sendMessage(op.param1,
                        f"👋 أهلاً {contact.displayName}!\n"
                        "شكراً لإضافتك 💚\n"
                        "أرسل: الأوامر")
                    print(f"✅ إضافة: {contact.displayName}")
                except Exception as e:
                    print(f"❌ خطأ إضافة: {e}")
        
        # [13] دعوة لمجموعة
        elif op.type == 13:
            inviter = op.param2
            invited = op.param3
            group_id = op.param1
            
            # حماية الدعوات
            if db.data['protect']['invite']:
                if not db.is_admin(inviter):
                    print(f"⚠️ دعوة غير مصرح من: {inviter}")
                    try:
                        client.cancelGroupInvitation(group_id, [invited])
                        client.kickoutFromGroup(group_id, [inviter])
                        
                        if inviter not in db.data['banned']:
                            db.data['banned'].append(inviter)
                            db.save()
                        
                        print(f"✅ طرد المخالف")
                    except Exception as e:
                        print(f"❌ فشل: {e}")
            
            # قبول الدعوة
            if db.data['auto']['join']:
                try:
                    client.acceptGroupInvitation(group_id)
                    group = client.getGroup(group_id)
                    client.sendMessage(group_id,
                        f"✅ انضممت: {group.name}\n"
                        "🛡️ الحماية مفعّلة\n"
                        "📝 أرسل: الأوامر")
                    print(f"✅ انضمام: {group.name}")
                except:
                    pass
        
        # [19] طرد من مجموعة
        elif op.type == 19:
            kicker = op.param2
            kicked = op.param3
            group_id = op.param1
            
            if db.data['protect']['kick']:
                # حماية البوت والأدمنز
                if kicked == my_mid or db.is_admin(kicked):
                    if not db.is_admin(kicker):
                        print(f"🚨 محاولة طرد من: {kicker}")
                        try:
                            # إعادة دعوة
                            client.inviteIntoGroup(group_id, [kicked])
                            # طرد المعتدي
                            client.kickoutFromGroup(group_id, [kicker])
                            client.sendMessage(group_id,
                                "🛡️ تم اكتشاف محاولة طرد!\n"
                                "✅ تمت معالجتها")
                            
                            if kicker not in db.data['banned']:
                                db.data['banned'].append(kicker)
                                db.save()
                            
                            print(f"✅ طرد المعتدي")
                        except Exception as e:
                            print(f"❌ فشل: {e}")
        
        # [11] تغيير رابط
        elif op.type == 11:
            changer = op.param2
            group_id = op.param1
            
            if db.data['protect']['qr']:
                if not db.is_admin(changer):
                    print(f"⚠️ محاولة فتح رابط")
                    try:
                        group = client.getGroup(group_id)
                        group.preventedJoinByTicket = True
                        client.updateGroup(group)
                        client.kickoutFromGroup(group_id, [changer])
                    except:
                        pass
        
        # [32] إلغاء دعوة
        elif op.type == 32:
            if db.data['protect']['cancel']:
                canceller = op.param2
                group_id = op.param1
                
                if not db.is_admin(canceller):
                    try:
                        client.kickoutFromGroup(group_id, [canceller])
                    except:
                        pass
        
        # [26] رسالة
        elif op.type == 26:
            msg = op.message
            if msg.contentType == 0 and msg.text:
                handle_msg(msg)
        
        # قراءة تلقائية
        if db.data['auto']['read'] and op.type == 26:
            try:
                client.sendChatChecked(op.param1, op.param2)
            except:
                pass
    
    except Exception as e:
        print(f"❌ خطأ في op {op.type}: {e}")

def handle_msg(msg):
    """معالجة الرسائل"""
    text = msg.text.strip()
    sender = msg._from
    to = msg.to if msg.toType == 2 else sender
    is_group = msg.toType == 2
    
    # منع المحظورين
    if db.is_banned(sender):
        return
    
    try:
        # ===== الأوامر العامة =====
        if text == 'الأوامر':
            client.sendMessage(to, help_msg())
        
        elif text == 'معلوماتي':
            contact = client.getContact(sender)
            role = "👑 مالك" if db.is_owner(sender) else \
                   "👮 أدمن" if db.is_admin(sender) else "👤 عضو"
            
            info = f"""╔═══════════════════
║ 📱 معلوماتك
║ 👤 {contact.displayName}
║ 🆔 {sender}
║ 🏆 {role}
╚═══════════════════"""
            client.sendMessage(to, info)
        
        elif text == 'السرعة':
            start = time.time()
            client.sendMessage(to, "⏱️ جاري القياس...")
            elapsed = time.time() - start
            client.sendMessage(to, f"⚡ السرعة: {elapsed:.2f}s")
        
        elif text == 'الحالة':
            p = db.data['protect']
            a = db.data['auto']
            
            status = f"""╔═══════════════════
║ 📊 حالة البوت
║
║ 🛡️ الحماية:
║ ├ الطرد: {'✅' if p['kick'] else '❌'}
║ ├ الدعوة: {'✅' if p['invite'] else '❌'}
║ ├ الرابط: {'✅' if p['qr'] else '❌'}
║ └ الإلغاء: {'✅' if p['cancel'] else '❌'}
║
║ ⚙️ التلقائي:
║ ├ الإضافة: {'✅' if a['add'] else '❌'}
║ ├ الانضمام: {'✅' if a['join'] else '❌'}
║ └ القراءة: {'✅' if a['read'] else '❌'}
║
║ 👥 الإحصائيات:
║ ├ 👑 Owners: {len(db.data['owners'])}
║ ├ 👮 Admins: {len(db.data['admins'])}
║ └ 🚫 Banned: {len(db.data['banned'])}
╚═══════════════════"""
            client.sendMessage(to, status)
        
        elif text == 'الوقت':
            now = datetime.now()
            client.sendMessage(to, 
                f"🕐 التاريخ والوقت:\n"
                f"{now.strftime('%Y-%m-%d')}\n"
                f"{now.strftime('%H:%M:%S')}")
        
        # ===== الحماية =====
        elif text == 'تفعيل_الحماية' and db.is_owner(sender):
            for key in db.data['protect']:
                db.data['protect'][key] = True
            db.save()
            client.sendMessage(to, "✅ تم تفعيل كل الحماية")
        
        elif text == 'ايقاف_الحماية' and db.is_owner(sender):
            for key in db.data['protect']:
                db.data['protect'][key] = False
            db.save()
            client.sendMessage(to, "❌ تم إيقاف كل الحماية")
        
        elif text == 'تفعيل_حماية_الطرد' and db.is_owner(sender):
            db.data['protect']['kick'] = True
            db.save()
            client.sendMessage(to, "✅ حماية الطرد مفعلة")
        
        elif text == 'ايقاف_حماية_الطرد' and db.is_owner(sender):
            db.data['protect']['kick'] = False
            db.save()
            client.sendMessage(to, "❌ حماية الطرد معطلة")
        
        elif text == 'تفعيل_حماية_الدعوة' and db.is_owner(sender):
            db.data['protect']['invite'] = True
            db.save()
            client.sendMessage(to, "✅ حماية الدعوة مفعلة")
        
        elif text == 'ايقاف_حماية_الدعوة' and db.is_owner(sender):
            db.data['protect']['invite'] = False
            db.save()
            client.sendMessage(to, "❌ حماية الدعوة معطلة")
        
        elif text == 'تفعيل_حماية_الرابط' and db.is_owner(sender):
            db.data['protect']['qr'] = True
            db.save()
            client.sendMessage(to, "✅ حماية الرابط مفعلة")
        
        elif text == 'ايقاف_حماية_الرابط' and db.is_owner(sender):
            db.data['protect']['qr'] = False
            db.save()
            client.sendMessage(to, "❌ حماية الرابط معطلة")
        
        # ===== المجموعة =====
        elif text == 'معلومات_المجموعة' and is_group:
            group = client.getGroup(to)
            creator = group.creator.displayName if group.creator else "غير معروف"
            qr = "مفتوح 🔓" if not group.preventedJoinByTicket else "مغلق 🔒"
            
            info = f"""╔═══════════════════
║ 📊 معلومات المجموعة
║
║ 📝 {group.name}
║ 👤 المنشئ: {creator}
║ 👥 الأعضاء: {len(group.members)}
║ 🔗 الرابط: {qr}
╚═══════════════════"""
            client.sendMessage(to, info)
        
        elif text == 'الاعضاء' and is_group:
            group = client.getGroup(to)
            msg_text = "╔═══ 👥 الأعضاء ═══\n"
            
            for i, m in enumerate(group.members[:30], 1):
                msg_text += f"║ {i}. {m.displayName}\n"
            
            if len(group.members) > 30:
                msg_text += f"║ و {len(group.members) - 30} آخرين\n"
            
            msg_text += f"╚═══ المجموع: {len(group.members)} ═══"
            client.sendMessage(to, msg_text)
        
        elif text.startswith('طرد ') and db.is_admin(sender) and is_group:
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                kicked = 0
                
                for m in mentions['MENTIONEES']:
                    target = m['M']
                    if not db.is_admin(target):
                        try:
                            client.kickoutFromGroup(to, [target])
                            kicked += 1
                        except:
                            pass
                
                if kicked > 0:
                    client.sendMessage(to, f"✅ تم طرد {kicked} عضو")
            else:
                client.sendMessage(to, "❌ منشن العضو!")
        
        elif text == 'طرد_الكل' and db.is_owner(sender) and is_group:
            group = client.getGroup(to)
            kicked = 0
            
            client.sendMessage(to, "⏳ جاري طرد الجميع...")
            
            for m in group.members:
                if not db.is_admin(m.mid) and m.mid != my_mid:
                    try:
                        client.kickoutFromGroup(to, [m.mid])
                        kicked += 1
                        time.sleep(0.5)
                    except:
                        pass
            
            client.sendMessage(to, f"✅ تم طرد {kicked} عضو")
        
        # ===== الصلاحيات =====
        elif text.startswith('اضافة_ادمن') and db.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for m in mentions['MENTIONEES']:
                    target = m['M']
                    if target not in db.data['admins']:
                        db.data['admins'].append(target)
                
                db.save()
                client.sendMessage(to, "✅ تمت الإضافة")
            else:
                client.sendMessage(to, "❌ منشن العضو!")
        
        elif text.startswith('حذف_ادمن') and db.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for m in mentions['MENTIONEES']:
                    target = m['M']
                    if target in db.data['admins']:
                        db.data['admins'].remove(target)
                
                db.save()
                client.sendMessage(to, "✅ تم الحذف")
            else:
                client.sendMessage(to, "❌ منشن العضو!")
        
        elif text == 'قائمة_الادمنز' and db.is_admin(sender):
            if db.data['admins']:
                msg_text = "╔═══ 👮 الأدمنز ═══\n"
                for i, admin_mid in enumerate(db.data['admins'], 1):
                    try:
                        contact = client.getContact(admin_mid)
                        msg_text += f"║ {i}. {contact.displayName}\n"
                    except:
                        msg_text += f"║ {i}. {admin_mid[:15]}...\n"
                msg_text += "╚═══════════════════"
                client.sendMessage(to, msg_text)
            else:
                client.sendMessage(to, "❌ لا يوجد أدمنز")
        
        elif text.startswith('حظر ') and db.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for m in mentions['MENTIONEES']:
                    target = m['M']
                    if not db.is_owner(target) and target not in db.data['banned']:
                        db.data['banned'].append(target)
                
                db.save()
                client.sendMessage(to, "✅ تم الحظر")
            else:
                client.sendMessage(to, "❌ منشن العضو!")
        
        elif text.startswith('الغاء_حظر ') and db.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for m in mentions['MENTIONEES']:
                    target = m['M']
                    if target in db.data['banned']:
                        db.data['banned'].remove(target)
                
                db.save()
                client.sendMessage(to, "✅ تم إلغاء الحظر")
            else:
                client.sendMessage(to, "❌ منشن العضو!")
        
        elif text == 'قائمة_المحظورين' and db.is_admin(sender):
            if db.data['banned']:
                msg_text = "╔═══ 🚫 المحظورين ═══\n"
                for i, banned_mid in enumerate(db.data['banned'][:20], 1):
                    msg_text += f"║ {i}. {banned_mid[:15]}...\n"
                msg_text += f"╚═══ المجموع: {len(db.data['banned'])} ═══"
                client.sendMessage(to, msg_text)
            else:
                client.sendMessage(to, "✅ لا يوجد محظورين")
        
        # ===== إدارة الرابط =====
        elif text == 'فتح_الرابط' and db.is_admin(sender) and is_group:
            group = client.getGroup(to)
            group.preventedJoinByTicket = False
            client.updateGroup(group)
            client.sendMessage(to, "🔓 تم فتح الرابط")
        
        elif text == 'اغلاق_الرابط' and db.is_admin(sender) and is_group:
            group = client.getGroup(to)
            group.preventedJoinByTicket = True
            client.updateGroup(group)
            client.sendMessage(to, "🔒 تم إغلاق الرابط")
        
        elif text == 'جلب_الرابط' and db.is_admin(sender) and is_group:
            try:
                ticket = client.reissueGroupTicket(to)
                client.sendMessage(to, 
                    f"🔗 رابط المجموعة:\n"
                    f"https://line.me/R/ti/g/{ticket}")
            except:
                client.sendMessage(to, 
                    "❌ الرابط مغلق!\n"
                    "استخدم: فتح_الرابط")
        
        elif text == 'مغادرة' and db.is_admin(sender) and is_group:
            client.sendMessage(to, "👋 وداعاً!")
            time.sleep(1)
            client.leaveGroup(to)
    
    except Exception as e:
        print(f"❌ خطأ في الرسالة: {e}")

# ========== الحلقة الرئيسية ==========
print("\n🚀 البوت يعمل الآن...")
print("💡 اضغط Ctrl+C للإيقاف\n")
print("="*60)

last_save = time.time()

try:
    while True:
        try:
            ops = oepoll.fetchOperations()
            
            for op in ops:
                handle_op(op)
            
            # حفظ كل 5 دقائق
            if time.time() - last_save > 300:
                db.save()
                last_save = time.time()
                print(f"💾 [{datetime.now().strftime('%H:%M:%S')}] حفظ تلقائي")
        
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(3)

except KeyboardInterrupt:
    print("\n\n⏹️ إيقاف البوت...")
    db.save()
    print("💾 تم حفظ البيانات")
    print("👋 وداعاً!")
