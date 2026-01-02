#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ LINE Protection Self-Bot
⚠️ استخدم حساب ثانوي فقط!
✅ حماية كاملة + إدارة مجموعات
"""

import json
import time
import os
import sys
from datetime import datetime

# ========== فحص المكتبات ==========
try:
    from linepy import LINE, OEPoll
    print("✅ linepy جاهز")
except ImportError:
    print("❌ linepy غير مثبت!")
    print("📥 قم بتشغيل: pip install git+https://github.com/dyseo/linepy.git")
    input("اضغط Enter للخروج...")
    sys.exit(1)

# ========== إعدادات البوت ==========
class BotConfig:
    def __init__(self):
        self.config_file = 'bot_config.json'
        self.token_file = 'line_token.txt'
        self.load_config()
    
    def load_config(self):
        """تحميل الإعدادات"""
        default = {
            'owners': [],
            'admins': [],
            'banned': [],
            'protect': {
                'kick': True,
                'invite': True,
                'qr': True,
                'cancel': True
            },
            'auto': {
                'add': True,
                'join': True,
                'leave': False
            },
            'language': 'ar'
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                for key in default:
                    if key not in self.data:
                        self.data[key] = default[key]
            except:
                self.data = default
        else:
            self.data = default
        
        self.save()
    
    def save(self):
        """حفظ الإعدادات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
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

config = BotConfig()

# ========== تسجيل الدخول ==========
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("="*60)
    print("🛡️  LINE PROTECTION SELF-BOT")
    print("="*60)
    print("⚠️  استخدم حساب ثانوي - ليس الرئيسي!")
    print("="*60)

def login():
    """تسجيل الدخول إلى LINE"""
    clear_screen()
    print_banner()
    
    # محاولة استخدام Token المحفوظ
    if os.path.exists(config.token_file):
        try:
            with open(config.token_file, 'r') as f:
                token = f.read().strip()
            
            print("\n🔐 تسجيل الدخول بـ Token المحفوظ...")
            client = LINE(token)
            print(f"✅ مرحباً: {client.profile.displayName}")
            return client
        except Exception as e:
            print(f"❌ Token منتهي: {e}")
            os.remove(config.token_file)
    
    # تسجيل دخول جديد
    print("\n📧 تسجيل دخول جديد")
    print("-"*60)
    
    while True:
        print("\nاختر طريقة التسجيل:")
        print("1. Email/Password")
        print("2. QR Code (قريباً)")
        print("3. إلغاء")
        
        choice = input("\nاختيارك: ").strip()
        
        if choice == '1':
            email = input("\n📧 Email: ").strip()
            password = input("🔑 Password: ").strip()
            
            if not email or not password:
                print("❌ الرجاء إدخال Email وPassword!")
                continue
            
            try:
                print("\n⏳ جاري التسجيل...")
                client = LINE(email, password)
                
                # حفظ Token
                with open(config.token_file, 'w') as f:
                    f.write(client.authToken)
                
                print(f"\n✅ تم التسجيل: {client.profile.displayName}")
                print(f"💾 Token محفوظ")
                return client
                
            except Exception as e:
                print(f"\n❌ فشل التسجيل: {e}")
                print("\n💡 تأكد من:")
                print("  • Email/Password صحيح")
                print("  • التحقق بخطوتين معطّل")
                print("  • الحساب ليس محظور")
                
                retry = input("\nحاول مرة أخرى؟ (y/n): ").lower()
                if retry != 'y':
                    sys.exit(1)
        
        elif choice == '3':
            print("\n👋 إلغاء...")
            sys.exit(0)
        else:
            print("❌ اختيار خاطئ!")

# تسجيل الدخول
client = login()
oepoll = OEPoll(client)
bot_mid = client.profile.mid

# إضافة نفسك كـ Owner تلقائياً
if bot_mid not in config.data['owners']:
    config.data['owners'].append(bot_mid)
    config.save()

clear_screen()
print_banner()
print(f"\n✅ البوت جاهز!")
print(f"👤 الاسم: {client.profile.displayName}")
print(f"🆔 MID: {bot_mid[:20]}...")
print(f"👑 Owners: {len(config.data['owners'])}")
print(f"👮 Admins: {len(config.data['admins'])}")
print("\n" + "="*60)

# ========== الأوامر ==========
def get_help():
    return """╔═══════════════════════
║ 🛡️ أوامر البوت الحامي
║
║ 📋 الأوامر العامة:
║ ├ help - قائمة الأوامر
║ ├ me - معلوماتي
║ ├ speed - سرعة البوت
║ ├ status - حالة الحماية
║ ├ time - الوقت الحالي
║ └ about - عن البوت
║
║ 🛡️ الحماية (Owner):
║ ├ protect on/off - كل الحماية
║ ├ kick on/off - حماية الطرد
║ ├ invite on/off - حماية الدعوة
║ ├ qr on/off - حماية الرابط
║ └ cancel on/off - حماية الإلغاء
║
║ 👥 الصلاحيات (Owner):
║ ├ addadmin @mention
║ ├ deladmin @mention
║ ├ adminlist
║ ├ ban @mention [reason]
║ ├ unban @mention
║ └ banlist
║
║ 🔧 المجموعة (Admin):
║ ├ ginfo - معلومات المجموعة
║ ├ members - الأعضاء
║ ├ kick @mention - طرد
║ ├ kickall - طرد الجميع
║ ├ invite @mention - دعوة
║ ├ openqr - فتح الرابط
║ ├ closeqr - إغلاق الرابط
║ ├ getqr - جلب الرابط
║ └ leave - مغادرة
║
║ ⚙️ إعدادات (Owner):
║ ├ autoadd on/off
║ ├ autojoin on/off
║ └ autoleave on/off
║
╚═══════════════════════"""

# ========== معالج الأحداث ==========
def handle_operation(op):
    try:
        # [5] إضافة صديق
        if op.type == 5:
            if config.data['auto']['add']:
                try:
                    contact = client.getContact(op.param1)
                    client.sendMessage(op.param1, 
                        f"👋 مرحباً {contact.displayName}!\n"
                        "شكراً لإضافتك 🌟\n"
                        "أرسل 'help' للأوامر")
                    print(f"✅ تمت إضافة: {contact.displayName}")
                except:
                    pass
        
        # [13] دعوة إلى مجموعة
        elif op.type == 13:
            inviter = op.param2
            invited = op.param3
            group_id = op.param1
            
            # حماية الدعوات
            if config.data['protect']['invite']:
                if not config.is_admin(inviter):
                    print(f"⚠️ دعوة غير مصرح: {inviter}")
                    try:
                        client.cancelGroupInvitation(group_id, [invited])
                        client.kickoutFromGroup(group_id, [inviter])
                        client.sendMessage(group_id, "🚫 تم طرد عضو حاول دعوة بدون صلاحية!")
                        
                        if inviter not in config.data['banned']:
                            config.data['banned'].append(inviter)
                            config.save()
                    except Exception as e:
                        print(f"❌ فشل الحماية: {e}")
            
            # قبول الدعوة
            if config.data['auto']['join']:
                try:
                    client.acceptGroupInvitation(group_id)
                    group = client.getGroup(group_id)
                    client.sendMessage(group_id, 
                        f"✅ انضممت للمجموعة: {group.name}\n"
                        "🛡️ الحماية مفعّلة\n"
                        "📝 أرسل 'help' للأوامر")
                    print(f"✅ انضممت: {group.name}")
                except:
                    pass
        
        # [19] طرد من مجموعة
        elif op.type == 19:
            kicker = op.param2
            kicked = op.param3
            group_id = op.param1
            
            if config.data['protect']['kick']:
                # حماية البوت والأدمنز
                if kicked == bot_mid or config.is_admin(kicked):
                    if not config.is_admin(kicker):
                        print(f"🚨 محاولة طرد: {kicker} طرد {kicked}")
                        try:
                            # إعادة دعوة
                            client.inviteIntoGroup(group_id, [kicked])
                            # طرد المعتدي
                            client.kickoutFromGroup(group_id, [kicker])
                            client.sendMessage(group_id, 
                                "🛡️ تم اكتشاف محاولة طرد!\n"
                                "✅ تمت معالجتها")
                            
                            if kicker not in config.data['banned']:
                                config.data['banned'].append(kicker)
                                config.save()
                            
                            print(f"✅ تم طرد المعتدي: {kicker}")
                        except Exception as e:
                            print(f"❌ فشل الحماية: {e}")
        
        # [11] تغيير رابط
        elif op.type == 11:
            changer = op.param2
            group_id = op.param1
            
            if config.data['protect']['qr']:
                if not config.is_admin(changer):
                    print(f"⚠️ محاولة تغيير رابط: {changer}")
                    try:
                        group = client.getGroup(group_id)
                        group.preventedJoinByTicket = True
                        client.updateGroup(group)
                        client.kickoutFromGroup(group_id, [changer])
                        client.sendMessage(group_id, 
                            "🔒 محاولة فتح الرابط!\n"
                            "✅ تم إغلاقه وطرد المعتدي")
                    except Exception as e:
                        print(f"❌ فشل الحماية: {e}")
        
        # [32] إلغاء دعوة
        elif op.type == 32:
            if config.data['protect']['cancel']:
                canceller = op.param2
                group_id = op.param1
                
                if not config.is_admin(canceller):
                    print(f"⚠️ محاولة إلغاء دعوة: {canceller}")
                    try:
                        client.kickoutFromGroup(group_id, [canceller])
                    except:
                        pass
        
        # [26] رسالة جديدة
        elif op.type == 26:
            msg = op.message
            if msg.contentType == 0 and msg.text:
                handle_message(msg)
        
        # [17] انضمام عضو
        elif op.type == 17:
            if config.data['auto']['leave']:
                try:
                    client.leaveGroup(op.param1)
                except:
                    pass
        
    except Exception as e:
        print(f"❌ خطأ في العملية {op.type}: {e}")

def handle_message(msg):
    """معالج الرسائل"""
    text = msg.text.strip()
    sender = msg._from
    to = msg.to if msg.toType == 2 else sender
    is_group = msg.toType == 2
    
    # منع المحظورين
    if config.is_banned(sender):
        return
    
    text_lower = text.lower()
    
    try:
        # ===== الأوامر العامة =====
        if text_lower == 'help':
            client.sendMessage(to, get_help())
        
        elif text_lower == 'me':
            contact = client.getContact(sender)
            role = "👑 Owner" if config.is_owner(sender) else \
                   "👮 Admin" if config.is_admin(sender) else "👤 Member"
            
            msg_text = f"""╔═══════════════════
║ 📱 معلوماتك
║ 👤 {contact.displayName}
║ 🆔 {sender}
║ 🏆 الرتبة: {role}
╚═══════════════════"""
            client.sendMessage(to, msg_text)
        
        elif text_lower == 'speed':
            start = time.time()
            client.sendMessage(to, "⏱️ جاري القياس...")
            elapsed = time.time() - start
            client.sendMessage(to, f"⚡ السرعة: {elapsed:.3f} ثانية")
        
        elif text_lower == 'status':
            p = config.data['protect']
            a = config.data['auto']
            
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
║ └ المغادرة: {'✅' if a['leave'] else '❌'}
║
║ 👥 الإحصائيات:
║ ├ 👑 Owners: {len(config.data['owners'])}
║ ├ 👮 Admins: {len(config.data['admins'])}
║ └ 🚫 Banned: {len(config.data['banned'])}
╚═══════════════════"""
            client.sendMessage(to, status)
        
        elif text_lower == 'time':
            now = datetime.now()
            client.sendMessage(to, f"🕐 الوقت:\n{now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif text_lower == 'about':
            client.sendMessage(to, 
                "╔═══════════════════\n"
                "║ 🛡️ LINE Protection Bot\n"
                "║ 📌 Self-Bot Version\n"
                "║ ✅ حماية كاملة\n"
                "║ ⚡ سريع ومستقر\n"
                "╚═══════════════════")
        
        # ===== التحكم في الحماية =====
        elif text_lower == 'protect on' and config.is_owner(sender):
            for key in config.data['protect']:
                config.data['protect'][key] = True
            config.save()
            client.sendMessage(to, "✅ تم تفعيل جميع أنواع الحماية")
        
        elif text_lower == 'protect off' and config.is_owner(sender):
            for key in config.data['protect']:
                config.data['protect'][key] = False
            config.save()
            client.sendMessage(to, "❌ تم إيقاف جميع أنواع الحماية")
        
        elif text_lower == 'kick on' and config.is_owner(sender):
            config.data['protect']['kick'] = True
            config.save()
            client.sendMessage(to, "✅ حماية الطرد مفعلة")
        
        elif text_lower == 'kick off' and config.is_owner(sender):
            config.data['protect']['kick'] = False
            config.save()
            client.sendMessage(to, "❌ حماية الطرد معطلة")
        
        elif text_lower == 'invite on' and config.is_owner(sender):
            config.data['protect']['invite'] = True
            config.save()
            client.sendMessage(to, "✅ حماية الدعوة مفعلة")
        
        elif text_lower == 'invite off' and config.is_owner(sender):
            config.data['protect']['invite'] = False
            config.save()
            client.sendMessage(to, "❌ حماية الدعوة معطلة")
        
        elif text_lower == 'qr on' and config.is_owner(sender):
            config.data['protect']['qr'] = True
            config.save()
            client.sendMessage(to, "✅ حماية الرابط مفعلة")
        
        elif text_lower == 'qr off' and config.is_owner(sender):
            config.data['protect']['qr'] = False
            config.save()
            client.sendMessage(to, "❌ حماية الرابط معطلة")
        
        # ===== معلومات المجموعة =====
        elif text_lower == 'ginfo' and is_group:
            group = client.getGroup(to)
            creator = group.creator.displayName if group.creator else "غير معروف"
            qr_status = "مغلق 🔒" if group.preventedJoinByTicket else "مفتوح 🔓"
            
            info = f"""╔═══════════════════
║ 📊 معلومات المجموعة
║
║ 📝 الاسم: {group.name}
║ 🆔 المعرف: {group.id}
║ 👤 المنشئ: {creator}
║ 👥 الأعضاء: {len(group.members)}
║ 🔗 الرابط: {qr_status}
╚═══════════════════"""
            client.sendMessage(to, info)
        
        elif text_lower == 'members' and is_group:
            group = client.getGroup(to)
            members_text = "╔═══ 👥 الأعضاء ═══\n"
            
            for i, member in enumerate(group.members[:30], 1):
                members_text += f"║ {i}. {member.displayName}\n"
            
            if len(group.members) > 30:
                members_text += f"║ ... و {len(group.members) - 30} آخرين\n"
            
            members_text += f"╚═══ Total: {len(group.members)} ═══"
            client.sendMessage(to, members_text)
        
        # ===== إدارة الأعضاء =====
        elif text_lower.startswith('kick ') and config.is_admin(sender) and is_group:
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                kicked_count = 0
                
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if not config.is_admin(target):
                        try:
                            client.kickoutFromGroup(to, [target])
                            kicked_count += 1
                        except:
                            pass
                
                if kicked_count > 0:
                    client.sendMessage(to, f"✅ تم طرد {kicked_count} عضو")
        
        elif text_lower == 'kickall' and config.is_owner(sender) and is_group:
            group = client.getGroup(to)
            kicked = 0
            
            for member in group.members:
                if not config.is_admin(member.mid) and member.mid != bot_mid:
                    try:
                        client.kickoutFromGroup(to, [member.mid])
                        kicked += 1
                        time.sleep(0.5)
                    except:
                        pass
            
            client.sendMessage(to, f"✅ تم طرد {kicked} عضو")
        
        # ===== إدارة الصلاحيات =====
        elif text_lower.startswith('addadmin') and config.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target not in config.data['admins']:
                        config.data['admins'].append(target)
                
                config.save()
                client.sendMessage(to, "✅ تمت إضافة Admin")
        
        elif text_lower.startswith('deladmin') and config.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target in config.data['admins']:
                        config.data['admins'].remove(target)
                
                config.save()
                client.sendMessage(to, "✅ تم حذف Admin")
        
        elif text_lower == 'adminlist' and config.is_admin(sender):
            if config.data['admins']:
                admin_text = "╔═══ 👮 Admins ═══\n"
                for i, admin_mid in enumerate(config.data['admins'], 1):
                    try:
                        contact = client.getContact(admin_mid)
                        admin_text += f"║ {i}. {contact.displayName}\n"
                    except:
                        admin_text += f"║ {i}. {admin_mid[:20]}...\n"
                admin_text += "╚═══════════════════"
                client.sendMessage(to, admin_text)
            else:
                client.sendMessage(to, "❌ لا يوجد أدمنز")
        
        # ===== الحظر =====
        elif text_lower.startswith('ban ') and config.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if not config.is_owner(target) and target not in config.data['banned']:
                        config.data['banned'].append(target)
                
                config.save()
                client.sendMessage(to, "✅ تم الحظر")
        
        elif text_lower.startswith('unban ') and config.is_owner(sender):
            if 'MENTION' in msg.contentMetadata:
                import ast
                mentions = ast.literal_eval(msg.contentMetadata['MENTION'])
                
                for mention in mentions['MENTIONEES']:
                    target = mention['M']
                    if target in config.data['banned']:
                        config.data['banned'].remove(target)
                
                config.save()
                client.sendMessage(to, "✅ تم إلغاء الحظر")
        
        elif text_lower == 'banlist' and config.is_admin(sender):
            if config.data['banned']:
                ban_text = "╔═══ 🚫 Banned ═══\n"
                for i, banned_mid in enumerate(config.data['banned'][:20], 1):
                    ban_text += f"║ {i}. {banned_mid[:20]}...\n"
                ban_text += f"╚═══ Total: {len(config.data['banned'])} ═══"
                client.sendMessage(to, ban_text)
            else:
                client.sendMessage(to, "✅ لا يوجد محظورين")
        
        # ===== إدارة الرابط =====
        elif text_lower == 'openqr' and config.is_admin(sender) and is_group:
            group = client.getGroup(to)
            group.preventedJoinByTicket = False
            client.updateGroup(group)
            client.sendMessage(to, "🔓 تم فتح رابط المجموعة")
        
        elif text_lower == 'closeqr' and config.is_admin(sender) and is_group:
            group = client.getGroup(to)
            group.preventedJoinByTicket = True
            client.updateGroup(group)
            client.sendMessage(to, "🔒 تم إغلاق رابط المجموعة")
        
        elif text_lower == 'getqr' and config.is_admin(sender) and is_group:
            try:
                ticket = client.reissueGroupTicket(to)
                client.sendMessage(to, f"🔗 رابط المجموعة:\nhttps://line.me/R/ti/g/{ticket}")
            except:
                client.sendMessage(to, "❌ الرابط مغلق!\nاستخدم: openqr")
        
        # ===== المغادرة =====
        elif text_lower == 'leave' and config.is_admin(sender) and is_group:
            client.sendMessage(to, "👋 وداعاً!")
            time.sleep(1)
            client.leaveGroup(to)
        
        # ===== الإعدادات التلقائية =====
        elif text_lower == 'autoadd on' and config.is_owner(sender):
            config.data['auto']['add'] = True
            config.save()
            client.sendMessage(to, "✅ الإضافة التلقائية مفعلة")
        
        elif text_lower == 'autoadd off' and config.is_owner(sender):
            config.data['auto']['add'] = False
            config.save()
            client.sendMessage(to, "❌ الإضافة التلقائية معطلة")
        
        elif text_lower == 'autojoin on' and config.is_owner(sender):
            config.data['auto']['join'] = True
            config.save()
            client.sendMessage(to, "✅ الانضمام التلقائي مفعل")
        
        elif text_lower == 'autojoin off' and config.is_owner(sender):
            config.data['auto']['join'] = False
            config.save()
            client.sendMessage(to, "❌ الانضمام التلقائي معطل")
        
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

# ========== Main Loop ==========
print("\n🚀 البوت يعمل الآن...")
print("💡 اضغط Ctrl+C للإيقاف")
print("="*60 + "\n")

last_save = time.time()

try:
