#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
🛡️ LINE Protection Bot - ProtectPy3
بوت حماية الجروبات من الطرد والمخالفات

⚠️ تحذير: استخدام غير رسمي - قد يؤدي لحظر حسابك
"""

from LINEPY import *
from akad.ttypes import *
import time
import json
import sys

# ═══════════════════════════════════════════════
# 📁 تحميل الإعدادات
# ═══════════════════════════════════════════════

def load_settings():
    """تحميل إعدادات البوت من ملف JSON"""
    try:
        with open('st2__b.json', 'r') as f:
            return json.load(f)
    except:
        # الإعدادات الافتراضية
        return {
            "protect": True,
            "qrprotect": True,
            "inviteprotect": True, 
            "cancelprotect": True,
            "blacklist": {},
            "autoJoin": True,
            "autoAdd": False,
            "autoLeave": False,
            "lang": "AR",
            "keyCommand": ".",
            "owner": [],
            "admin": [],
            "staff": [],
            "bots": []
        }

def save_settings(settings):
    """حفظ الإعدادات في ملف JSON"""
    try:
        with open('st2__b.json', 'w') as f:
            json.dump(settings, w, indent=4)
    except Exception as e:
        print(f"❌ خطأ في حفظ الإعدادات: {e}")

# تحميل الإعدادات
settings = load_settings()

# ═══════════════════════════════════════════════
# 🔐 تسجيل الدخول
# ═══════════════════════════════════════════════

print("""
╔═══════════════════════════════════════════════╗
║     🛡️  LINE PROTECTION BOT - ProtectPy3      ║
║              بوت حماية الجروبات               ║
╚═══════════════════════════════════════════════╝
""")

print("🔑 اختر طريقة تسجيل الدخول:\n")
print("1. Email + Password")
print("2. Token (Auth Token)")
print("3. QR Code (قد لا يعمل)")

choice = input("\nالخيار [1/2/3]: ").strip()

try:
    if choice == "1":
        # تسجيل دخول بالإيميل والباسورد
        email = input("\n📧 الإيميل: ")
        password = input("🔒 الباسورد: ")
        
        print("\n⏳ جاري تسجيل الدخول...")
        cl = LINE(email, password)
        
    elif choice == "2":
        # تسجيل دخول بالتوكن
        token = input("\n🎫 Token: ")
        
        print("\n⏳ جاري تسجيل الدخول...")
        cl = LINE(authToken=token)
        
    elif choice == "3":
        # تسجيل دخول بـ QR Code
        print("\n📱 افتح LINE على جوالك وامسح الـ QR Code...")
        cl = LINE(qr=True)
    
    else:
        print("❌ خيار غير صحيح!")
        sys.exit()
    
    print("\n✅ تم تسجيل الدخول بنجاح!")
    
except Exception as e:
    print(f"\n❌ فشل تسجيل الدخول: {e}")
    print("\n💡 جرب:")
    print("1. تأكد من الإيميل والباسورد")
    print("2. استخدم Token بدلاً من Email")
    print("3. فعّل VPN وحاول مرة أخرى")
    sys.exit()

# ═══════════════════════════════════════════════
# 👤 معلومات الحساب
# ═══════════════════════════════════════════════

try:
    profile = cl.getProfile()
    
    print("\n" + "═" * 50)
    print(f"👤 الاسم: {profile.displayName}")
    print(f"🆔 MID: {profile.mid}")
    print(f"💬 الحالة: {profile.statusMessage}")
    print("═" * 50)
    
    # إضافة الحساب كمالك تلقائياً إذا كانت القائمة فارغة
    if not settings.get('owner'):
        settings['owner'] = [profile.mid]
        save_settings(settings)
        print("\n✅ تم إضافتك كمالك للبوت")
    
except Exception as e:
    print(f"⚠️ تحذير: لم نتمكن من جلب معلومات الحساب: {e}")

# ═══════════════════════════════════════════════
# 🔧 دوال مساعدة
# ═══════════════════════════════════════════════

def is_owner(mid):
    """التحقق من المالك"""
    return mid in settings.get('owner', [])

def is_admin(mid):
    """التحقق من الأدمن"""
    return mid in settings.get('admin', []) or is_owner(mid)

def is_staff(mid):
    """التحقق من الموظف"""
    return mid in settings.get('staff', []) or is_admin(mid)

def is_bot(mid):
    """التحقق من البوت"""
    return mid in settings.get('bots', [])

def is_blacklisted(mid):
    """التحقق من القائمة السوداء"""
    return mid in settings.get('blacklist', {})

def add_blacklist(mid):
    """إضافة للقائمة السوداء"""
    if 'blacklist' not in settings:
        settings['blacklist'] = {}
    settings['blacklist'][mid] = True
    save_settings(settings)

def remove_blacklist(mid):
    """حذف من القائمة السوداء"""
    if mid in settings.get('blacklist', {}):
        del settings['blacklist'][mid]
        save_settings(settings)

def send_message(to, text):
    """إرسال رسالة"""
    try:
        cl.sendMessage(to, text)
    except Exception as e:
        print(f"❌ خطأ في إرسال رسالة: {e}")

def kick_member(group_id, member_id):
    """طرد عضو من الجروب"""
    try:
        cl.kickoutFromGroup(group_id, [member_id])
        return True
    except Exception as e:
        print(f"❌ خطأ في الطرد: {e}")
        return False

# ═══════════════════════════════════════════════
# 📝 معالجة الأوامر
# ═══════════════════════════════════════════════

def handle_command(msg):
    """معالجة الأوامر النصية"""
    
    text = msg.text
    sender = msg._from
    to = msg.to
    
    # التحقق من بداية الأمر
    cmd_key = settings.get('keyCommand', '.')
    if not text.startswith(cmd_key):
        return
    
    # استخراج الأمر
    cmd = text[len(cmd_key):].strip().lower()
    
    # ═════════════════════════════════════════
    # 📋 أمر المساعدة
    # ═════════════════════════════════════════
    
    if cmd in ['مساعدة', 'help', 'h']:
        help_text = """🤖 أوامر البوت:

👑 للمالك:
• .أدمن @mention - إضافة أدمن
• .حذف أدمن @mention - حذف أدمن
• .بوت @mention - إضافة بوت

🛡️ للأدمن:
• .بلاك @mention - بلاك ليست
• .حذف بلاك @mention - حذف من البلاك
• .طرد @mention - طرد عضو
• .حماية on/off - تفعيل الحماية

📊 معلومات:
• .معلومات - معلومات البوت
• .الإعدادات - الإعدادات الحالية
• .السرعة - سرعة الاستجابة"""
        
        send_message(to, help_text)
    
    # ═════════════════════════════════════════
    # ℹ️ معلومات البوت
    # ═════════════════════════════════════════
    
    elif cmd in ['معلومات', 'info', 'i']:
        info_text = f"""ℹ️ معلومات البوت:

🛡️ الحماية: {'✅ مفعلة' if settings['protect'] else '❌ معطلة'}
🚫 حماية QR: {'✅ مفعلة' if settings['qrprotect'] else '❌ معطلة'}
📩 حماية الدعوات: {'✅ مفعلة' if settings['inviteprotect'] else '❌ معطلة'}
🌐 اللغة: {settings['lang']}
⌨️ رمز الأوامر: {settings['keyCommand']}

👑 المالكين: {len(settings.get('owner', []))}
🛡️ الأدمن: {len(settings.get('admin', []))}
🚫 البلاك ليست: {len(settings.get('blacklist', {}))}"""
        
        send_message(to, info_text)
    
    # ═════════════════════════════════════════
    # ⚡ السرعة
    # ═════════════════════════════════════════
    
    elif cmd in ['سرعة', 'speed', 'sp']:
        start = time.time()
        send_message(to, "⏱️ جاري القياس...")
        end = time.time()
        speed = round((end - start) * 1000, 2)
        send_message(to, f"⚡ السرعة: {speed}ms")
    
    # ═════════════════════════════════════════
    # 👑 أوامر المالك
    # ═════════════════════════════════════════
    
    elif is_owner(sender):
        
        # إضافة أدمن
        if cmd.startswith('أدمن') or cmd.startswith('admin'):
            if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    mid = mention['M']
                    if mid not in settings['admin']:
                        settings['admin'].append(mid)
                save_settings(settings)
                send_message(to, "✅ تم إضافة الأدمن")
        
        # حذف أدمن
        elif cmd.startswith('حذف أدمن'):
            if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    mid = mention['M']
                    if mid in settings['admin']:
                        settings['admin'].remove(mid)
                save_settings(settings)
                send_message(to, "✅ تم حذف الأدمن")
    
    # ═════════════════════════════════════════
    # 🛡️ أوامر الأدمن
    # ═════════════════════════════════════════
    
    elif is_admin(sender):
        
        # إضافة للبلاك ليست
        if cmd.startswith('بلاك') or cmd.startswith('black'):
            if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    mid = mention['M']
                    add_blacklist(mid)
                    # طرد من الجروب
                    kick_member(to, mid)
                send_message(to, "✅ تم إضافة للقائمة السوداء وطرده")
        
        # حذف من البلاك ليست
        elif cmd.startswith('حذف بلاك'):
            if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    mid = mention['M']
                    remove_blacklist(mid)
                send_message(to, "✅ تم حذف من القائمة السوداء")
        
        # طرد عضو
        elif cmd.startswith('طرد') or cmd.startswith('kick'):
            if msg.contentMetadata and 'MENTION' in msg.contentMetadata:
                mentions = json.loads(msg.contentMetadata['MENTION'])
                for mention in mentions['MENTIONEES']:
                    mid = mention['M']
                    kick_member(to, mid)
                send_message(to, "✅ تم طرد العضو")
        
        # تفعيل الحماية
        elif cmd == 'حماية on' or cmd == 'protect on':
            settings['protect'] = True
            save_settings(settings)
            send_message(to, "🛡️ تم تفعيل الحماية")
        
        # إيقاف الحماية
        elif cmd == 'حماية off' or cmd == 'protect off':
            settings['protect'] = False
            save_settings(settings)
            send_message(to, "⚠️ تم إيقاف الحماية")
        
        # حماية QR
        elif cmd == 'qr on':
            settings['qrprotect'] = True
            save_settings(settings)
            send_message(to, "✅ تم تفعيل حماية QR")
        
        elif cmd == 'qr off':
            settings['qrprotect'] = False
            save_settings(settings)
            send_message(to, "❌ تم إيقاف حماية QR")

# ═══════════════════════════════════════════════
# 🎭 معالجة الأحداث (Operations)
# ═══════════════════════════════════════════════

def handle_operation(op):
    """معالجة أحداث LINE"""
    
    try:
        # ════════════════════════════════════
        # 💬 رسالة جديدة
        # ════════════════════════════════════
        
        if op.type == 26:  # RECEIVE_MESSAGE
            msg = op.message
            
            # معالجة الرسائل النصية فقط
            if msg.contentType == 0:
                handle_command(msg)
        
        # ════════════════════════════════════
        # 👥 عضو جديد انضم
        # ════════════════════════════════════
        
        elif op.type == 17:  # NOTIFIED_ADD_CONTACT
            if not settings['protect']:
                return
            
            group_id = op.param1
            members = op.param3.split('\x1e')
            
            for member_id in members:
                # التحقق من القائمة السوداء
                if is_blacklisted(member_id):
                    print(f"🚫 طرد {member_id} - في القائمة السوداء")
                    kick_member(group_id, member_id)
                    send_message(group_id, "⚠️ تم طرد عضو من القائمة السوداء")
        
        # ════════════════════════════════════
        # 🚫 عضو تم طرده
        # ════════════════════════════════════
        
        elif op.type == 19:  # NOTIFIED_KICKOUT_FROM_GROUP
            if not settings['protect']:
                return
            
            group_id = op.param1
            kicker = op.param2  # من طرد
            kicked = op.param3  # المطرود
            
            # تجاهل إذا كان الطارد بوت أو أدمن
            if is_bot(kicker) or is_admin(kicker):
                return
            
            # إضافة الطارد للبلاك ليست وطرده
            print(f"⚔️ {kicker} طرد {kicked} - سيتم معاقبته!")
            add_blacklist(kicker)
            kick_member(group_id, kicker)
            send_message(group_id, "⚠️ تم طرد شخص قام بطرد عضو!")
        
        # ════════════════════════════════════
        # 📩 دعوة لجروب
        # ════════════════════════════════════
        
        elif op.type == 13:  # NOTIFIED_INVITE_INTO_GROUP
            if settings['autoJoin']:
                group_id = op.param1
                try:
                    cl.acceptGroupInvitation(group_id)
                    print(f"✅ تم قبول دعوة الجروب: {group_id}")
                except:
                    pass
    
    except Exception as e:
        print(f"❌ خطأ في معالجة الحدث: {e}")

# ═══════════════════════════════════════════════
# 🔄 البوت الرئيسي - الاستماع للأحداث
# ═══════════════════════════════════════════════

print("\n🤖 البوت يعمل الآن...")
print("📱 جاهز للحماية!")
print("⚠️ لا تغلق هذه النافذة\n")
print("═" * 50)

# متغير الـ revision
oepoll = OEPoll(cl)

while True:
    try:
        # الحصول على العمليات الجديدة
        operations = oepoll.singleTrace(count=50)
        
        if operations:
            for op in operations:
                # معالجة كل عملية
                handle_operation(op)
                
    except KeyboardInterrupt:
        print("\n\n👋 إيقاف البوت...")
        print("✅ تم حفظ الإعدادات")
        save_settings(settings)
        break
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        time.sleep(3)
        # إعادة المحاولة

print("\n🔚 البوت متوقف.")
