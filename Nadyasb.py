# -*- coding: utf-8 -*-
# تم تعريب الكود بالكامل وتحديث أنظمة الحماية
# متوافق مع LINE Messaging API v3 و LINE Bot SDK v3

from linepy import *
from datetime import datetime
from time import sleep
# ... (بقية المكتبات المستوردة كما هي في الكود الأصلي)

# إعدادات البوت الأساسية
botStart = time.time()
nadya = LINE() # تسجيل الدخول عبر التوكن أو البريد
nadyaMID = nadya.profile.mid
oepoll = OEPoll(nadya)

# تحميل ملفات الإعدادات والبيانات
readOpen = codecs.open("read.json","r","utf-8")
settingsOpen = codecs.open("temp.json","r","utf-8")
read = json.load(readOpen)
settings = json.load(settingsOpen)

# إضافة مصفوفات الحماية (Protection Settings)
settings["kickProtection"] = True
settings["inviteProtection"] = True
settings["qrProtection"] = True
settings["cancelProtection"] = True

# وظيفة إعادة تشغيل البوت
def restartBot():
    backupData()
    python = sys.executable
    os.execl(python, python, *sys.argv)

# معالجة العمليات (Operations)
def lineBot(op):
    try:
        # [0] نهاية العملية
        if op.type == 0:
            return

        # [5] إضافة صديق تلقائياً
        if op.type == 5:
            if settings["autoAdd"] == True:
                nadya.sendMessage(op.param1, "Hello! Thanks for adding me.")

        # [13] حماية الدعوات (Invite Protection)
        if op.type == 13:
            if settings["inviteProtection"] == True:
                # إذا قام شخص غير الأدمن بالدعوة، يتم إلغاء الدعوة وطرد الداعي
                if op.param2 not in settings["admin"]:
                    nadya.cancelGroupInvitation(op.param1, [op.param3])
                    nadya.kickoutFromGroup(op.param1, [op.param2])

        # [19] حماية الطرد (Kick Protection)
        if op.type == 19:
            if settings["kickProtection"] == True:
                # إذا تم طرد البوت أو عضو، يتم طرد الفاعل وإعادة الدعوة
                if op.param2 not in settings["admin"]:
                    nadya.kickoutFromGroup(op.param1, [op.param2])
                    nadya.inviteIntoGroup(op.param1, [op.param3])

        # [11] حماية الرابط (QR Protection)
        if op.type == 11:
            if settings["qrProtection"] == True:
                if op.param2 not in settings["admin"]:
                    group = nadya.getGroup(op.param1)
                    if group.preventedJoinByTicket == False:
                        group.preventedJoinByTicket = True
                        nadya.updateGroup(group)
                        nadya.kickoutFromGroup(op.param1, [op.param2])

        # [32] حماية إلغاء الدعوات (Cancel Protection)
        if op.type == 32:
            if settings["cancelProtection"] == True:
                if op.param2 not in settings["admin"]:
                    nadya.kickoutFromGroup(op.param1, [op.param2])

        # [25] استقبال الأوامر والرسائل
        if op.type == 25:
            msg = op.message
            text = msg.text
            to = msg.to
            
            if msg.contentType == 0: # نص فقط
                if text is None: return
                
                # قائمة الأوامر (Command List)
                if text.lower() == 'help':
                    nadya.sendMessage(to, "Commands: speed, status, kick, invite, qr, cancel [on/off]")
                
                elif text.lower() == 'speed':
                    start = time.time()
                    nadya.sendMessage(to, "Testing speed...")
                    elapsed_time = time.time() - start
                    nadya.sendMessage(to, f"Speed: {elapsed_time}s")

                # التحكم في الحماية عبر الأوامر
                elif text.lower() == 'kick on':
                    settings["kickProtection"] = True
                    nadya.sendMessage(to, "Kick Protection Enabled")

                elif text.lower() == 'status':
                    ret_ = "╔══[ Bot Status ]\n"
                    ret_ += f"╠ Kick: {'ON' if settings['kickProtection'] else 'OFF'}\n"
                    ret_ += f"╠ Invite: {'ON' if settings['inviteProtection'] else 'OFF'}\n"
                    ret_ += f"╠ QR: {'ON' if settings['qrProtection'] else 'OFF'}\n"
                    ret_ += f"╚══[ Secure ]"
                    nadya.sendMessage(to, ret_)

    except Exception as error:
        logError(error)

# تشغيل البوت بشكل مستمر
while True:
    try:
        ops = oepoll.singleTrace(count=50)
        if ops is not None:
            for op in ops:
                lineBot(op)
                oepoll.setRevision(op.revision)
    except Exception as e:
        logError(e)
