# -*- coding: utf-8 -*-
from linepy import LINE, OEPoll
from datetime import datetime
from bs4 import BeautifulSoup
from humanfriendly import format_timespan
import time, json, codecs, random, re, ast, pytz, urllib.parse, requests

botStart = time.time()

# Initialize Bots
nadya = LINE()
ki = LINE()
ki2 = LINE()
ki3 = LINE()
ki4 = LINE()

KAC = [nadya, ki, ki2, ki3, ki4]
nadyaMID = nadya.profile.mid
kiMID = ki.profile.mid
ki2MID = ki2.profile.mid
ki3MID = ki3.profile.mid
ki4MID = ki4.profile.mid
Bots = [nadyaMID, kiMID, ki2MID, ki3MID, ki4MID]

responsename = nadya.getProfile().displayName
responsename2 = ki.getProfile().displayName
responsename3 = ki2.getProfile().displayName
responsename4 = ki3.getProfile().displayName
responsename5 = ki4.getProfile().displayName

oepoll = OEPoll(nadya)
oepoll1 = OEPoll(ki)
oepoll2 = OEPoll(ki2)
oepoll3 = OEPoll(ki3)
oepoll4 = OEPoll(ki4)

nadyaProfile = nadya.getProfile()
myProfile = {
    "displayName": nadyaProfile.displayName,
    "statusMessage": nadyaProfile.statusMessage,
    "pictureStatus": nadyaProfile.pictureStatus
}

with open('Owner.json', 'r') as fp:
    Owner = json.load(fp)
with open('admin.json', 'r') as fp:
    admin = json.load(fp)

settings = {
    "protect": True, "qrprotect": True, "inviteprotect": True, "cancelprotect": True,
    "autoJoin": True, "autoAdd": True, "autoLeave": False, "autoJoinTicket": True,
    "changePicture": False, "changeGroupPicture": [], "blacklist": {},
    "wblacklist": False, "dblacklist": False, "keyCommand": "."
}

def backupData():
    try:
        with codecs.open('Owner.json', 'w', 'utf-8') as f:
            json.dump(Owner, f, sort_keys=True, indent=4, ensure_ascii=False)
        with codecs.open('admin.json', 'w', 'utf-8') as f:
            json.dump(admin, f, sort_keys=True, indent=4, ensure_ascii=False)
        return True
    except: return False

def sendMessageWithMention(to, mid):
    try:
        aa = '{"S":"0","E":"3","M":' + json.dumps(mid) + '}'
        nadya.sendMessage(to, '@x ', contentMetadata={'MENTION':'{"MENTIONEES":['+aa+']}'}, contentType=0)
    except: pass

def getCurrentTime():
    tz = pytz.timezone("Asia/Riyadh")
    timeNow = datetime.now(tz=tz)
    day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    hari = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    bulan = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    hr = timeNow.strftime("%A")
    bln = timeNow.strftime("%m")
    for i in range(len(day)):
        if hr == day[i]: hasil = hari[i]
    for k in range(0, len(bulan)):
        if bln == str(k): bln = bulan[k-1]
    return hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\n⏰ الساعة: [ " + timeNow.strftime('%H:%M:%S') + " ]"

def helpMessage():
    return """╔═══════════════════
║ ♥ ✿✿✿ BOT PROTECT ✿✿✿ ♥
║
║ ══✪〖 Protection 〗✪═══
║ ➥ protect on/off
║ ➥ qrprotect on/off
║ ➥ inviteprotect on/off
║ ➥ cancelprotect on/off
║ ➥ setpro on/off
║
║ ══✪〖 Settings 〗✪══════
║ ➥ autoadd on/off
║ ➥ autojoin on/off
║ ➥ autoleave on/off
║ ➥ autojoinlink on/off
║
║ ══✪〖 Admin 〗✪═════════
║ ➥ adminadd [mention]
║ ➥ admindel [mention]
║ ➥ adminlist
║ ➥ owneradd [mention]
║ ➥ ownerdel [mention]
║ ➥ ownerlist
║
║ ══✪〖 Ban System 〗✪════
║ ➥ bancontact
║ ➥ unbancontact
║ ➥ banlist
║ ➥ clearban
║
║ ══✪〖 Self 〗✪══════════
║ ➥ me | mymid | myname
║ ➥ mybio | mypicture
║ ➥ myvideoprofile | mycover
║ ➥ cpp (تغيير الصورة)
║
║ ══✪〖 Steal 〗✪═════════
║ ➥ stealcontact [mention]
║ ➥ stealmid [mention]
║ ➥ stealname [mention]
║ ➥ stealbio [mention]
║ ➥ stealpicture [mention]
║ ➥ stealvideoprofile [mention]
║ ➥ stealcover [mention]
║ ➥ cloneprofile [mention]
║ ➥ restoreprofile
║
║ ══✪〖 Group 〗✪═════════
║ ➥ groupcreator | groupid
║ ➥ groupname | grouppicture
║ ➥ groupticket | groupticket on/off
║ ➥ groupinfo | grouplist
║ ➥ memberlist | mention
║ ➥ cgp (تغيير صورة القروب)
║ ➥ kick [mention] | kickall
║ ➥ invite [mention]
║ ➥ joinall | byeall
║
║ ══✪〖 Bot Info 〗✪══════
║ ➥ time | about | status
║ ➥ speed | runtime | restart
║ ➥ respon | absen
║
║ ══✪〖 Other 〗✪═════════
║ ➥ invgroupcall
║ ➥ removeallchat
║ ➥ rejectall
║
╚═══════════════════"""

def protectKick(op):
    try:
        if op.param3 in Bots:
            if op.param2 not in admin and op.param2 not in Owner:
                G = random.choice(KAC).getGroup(op.param1)
                G.preventedJoinByTicket = False
                random.choice(KAC).updateGroup(G)
                Ticket = random.choice(KAC).reissueGroupTicket(op.param1)
                for bot in KAC:
                    try: bot.acceptGroupInvitationByTicket(op.param1, Ticket)
                    except: pass
                G.preventedJoinByTicket = True
                random.choice(KAC).updateGroup(G)
                random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                settings["blacklist"][op.param2] = True
                nadya.sendMessage(op.param1, "⚠️ تم طرد المعتدي تلقائياً")
    except: pass

def protectInvite(op):
    try:
        if op.param2 not in admin and op.param2 not in Owner and op.param2 not in Bots:
            if settings["inviteprotect"]:
                random.choice(KAC).cancelGroupInvitation(op.param1, [op.param3])
                random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                settings["blacklist"][op.param2] = True
                nadya.sendMessage(op.param1, "⚠️ دعوة غير مصرح بها - تم الطرد")
    except: pass

def protectQR(op):
    try:
        if op.param2 not in admin and op.param2 not in Owner and op.param2 not in Bots:
            if settings["qrprotect"]:
                G = random.choice(KAC).getGroup(op.param1)
                G.preventedJoinByTicket = True
                random.choice(KAC).updateGroup(G)
                random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                settings["blacklist"][op.param2] = True
                nadya.sendMessage(op.param1, "⚠️ تم إغلاق الرابط وطرد المعتدي")
    except: pass

def lineBot(op):
    try:
        if op.type == 5:
            if settings["autoAdd"]:
                contact = nadya.getContact(op.param1)
                nadya.sendMessage(op.param1, f"مرحباً {contact.displayName} 👋\nشكراً لإضافتك لي")
        
        if op.type == 13:
            if settings["autoJoin"]: nadya.acceptGroupInvitation(op.param1)
            protectInvite(op)
        
        if op.type == 17:
            if op.param2 in admin or op.param2 in Owner:
                nadya.sendMessage(op.param1, f"مرحباً بالأدمن: {nadya.getContact(op.param2).displayName} 🌟")
        
        if op.type == 19: protectKick(op)
        if op.type == 24:
            if settings["autoLeave"]: nadya.leaveRoom(op.param1)
        if op.type == 11: protectQR(op)
        
        if op.type == 26:
            msg = op.message
            text = msg.text
            sender = msg._from
            to = msg.to if msg.toType == 2 else sender
            msg_id = msg.id
            
            if text is None:
                if msg.contentType == 13:
                    if settings.get("wblacklist"):
                        settings["blacklist"][msg.contentMetadata["mid"]] = True
                        settings["wblacklist"] = False
                        nadya.sendMessage(to, "✅ تم إضافته للقائمة السوداء")
                    elif settings.get("dblacklist"):
                        if msg.contentMetadata["mid"] in settings["blacklist"]:
                            del settings["blacklist"][msg.contentMetadata["mid"]]
                            nadya.sendMessage(to, "✅ تم إزالته من القائمة السوداء")
                        settings["dblacklist"] = False
                elif msg.contentType == 1:
                    if settings["changePicture"]:
                        path = nadya.downloadObjectMsg(msg_id)
                        settings["changePicture"] = False
                        nadya.updateProfilePicture(path)
                        nadya.sendMessage(to, "✅ تم تغيير صورة الملف الشخصي")
                    if msg.toType == 2:
                        if to in settings["changeGroupPicture"]:
                            path = nadya.downloadObjectMsg(msg_id)
                            settings["changeGroupPicture"].remove(to)
                            nadya.updateGroupPicture(to, path)
                            nadya.sendMessage(to, "✅ تم تغيير صورة المجموعة")
                return
            
            text_lower = text.lower()
            
            if '/ti/g/' in text:
                if settings["autoJoinTicket"]:
                    link_re = re.compile('(?:line\:\/|line\.me\/R)\/ti\/g\/([a-zA-Z0-9_-]+)?')
                    for ticket_id in link_re.findall(text):
                        try:
                            group = nadya.findGroupByTicket(ticket_id)
                            nadya.acceptGroupInvitationByTicket(group.id, ticket_id)
                            nadya.sendMessage(to, f"✅ تم الانضمام للمجموعة: {group.name}")
                        except: pass
            
            if text_lower == 'help': nadya.sendMessage(to, helpMessage())
            elif text_lower == 'time': nadya.sendMessage(to, "🕐 الوقت الحالي:\n" + getCurrentTime())
            elif text_lower == 'about':
                try:
                    contact = nadya.getContact(nadyaMID)
                    grouplist = nadya.getGroupIdsJoined()
                    contactlist = nadya.getAllContactIds()
                    blockedlist = nadya.getBlockedContactIds()
                    nadya.sendMessage(to, f"""╔═══[ About Bot ]
║ 📱 الاسم: {contact.displayName}
║ 👥 المجموعات: {len(grouplist)}
║ 👤 الأصدقاء: {len(contactlist)}
║ 🚫 المحظورين: {len(blockedlist)}
║ ⚡ النسخة: Premium
║ 👨‍💻 المطور: NADYA_TJ
╚═══════════════""")
                except: pass
            elif text_lower == 'respon':
                nadya.sendMessage(to, f"1️⃣ {responsename}")
                ki.sendMessage(to, f"2️⃣ {responsename2}")
                ki2.sendMessage(to, f"3️⃣ {responsename3}")
                ki3.sendMessage(to, f"4️⃣ {responsename4}")
                ki4.sendMessage(to, f"5️⃣ {responsename5}")
            elif text_lower == 'absen':
                if sender in Owner:
                    for mid in [nadyaMID, kiMID, ki2MID, ki3MID, ki4MID]:
                        nadya.sendContact(to, mid)
            elif text_lower == 'invgroupcall':
                if msg.toType == 2 and (sender in admin or sender in Owner):
                    try:
                        group = nadya.getGroup(to)
                        members = [mem.mid for mem in group.members]
                        nadya.acquireGroupCallRoute(to)
                        nadya.inviteIntoGroupCall(to, contactIds=members)
                        nadya.sendMessage(to, "📞 تم دعوة الجميع للمكالمة")
                    except: pass
            elif text_lower == 'removeallchat':
                if sender in Owner:
                    try:
                        nadya.removeAllMessages(op.param2)
                        nadya.sendMessage(to, "✅ تم حذف جميع المحادثات")
                    except: pass
            elif text_lower == 'rejectall':
                if sender in Owner:
                    ginvited = nadya.getGroupIdsInvited()
                    if ginvited:
                        for gid in ginvited: nadya.rejectGroupInvitation(gid)
                        nadya.sendMessage(to, f"✅ تم رفض {len(ginvited)} دعوة")
            elif text_lower == 'protect on':
                if sender in Owner:
                    settings["protect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل الحماية")
            elif text_lower == 'protect off':
                if sender in Owner:
                    settings["protect"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف الحماية")
            elif text_lower == 'qrprotect on':
                if sender in Owner:
                    settings["qrprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية الرابط")
            elif text_lower == 'qrprotect off':
                if sender in Owner:
                    settings["qrprotect"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف حماية الرابط")
            elif text_lower == 'inviteprotect on':
                if sender in Owner:
                    settings["inviteprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية الدعوة")
            elif text_lower == 'inviteprotect off':
                if sender in Owner:
                    settings["inviteprotect"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف حماية الدعوة")
            elif text_lower == 'cancelprotect on':
                if sender in Owner:
                    settings["cancelprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية إلغاء الدعوة")
            elif text_lower == 'cancelprotect off':
                if sender in Owner:
                    settings["cancelprotect"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف حماية إلغاء الدعوة")
            elif text_lower == 'setpro on':
                if sender in Owner:
                    settings["protect"] = settings["qrprotect"] = settings["inviteprotect"] = settings["cancelprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل جميع أنواع الحماية")
            elif text_lower == 'setpro off':
                if sender in Owner:
                    settings["protect"] = settings["qrprotect"] = settings["inviteprotect"] = settings["cancelprotect"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف جميع أنواع الحماية")
            elif text_lower == 'autoadd on':
                settings["autoAdd"] = True
                nadya.sendMessage(to, "✅ تم تفعيل الإضافة التلقائية")
            elif text_lower == 'autoadd off':
                settings["autoAdd"] = False
                nadya.sendMessage(to, "❌ تم إيقاف الإضافة التلقائية")
            elif text_lower == 'autojoin on':
                if sender in Owner:
                    settings["autoJoin"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل الانضمام التلقائي")
            elif text_lower == 'autojoin off':
                if sender in Owner:
                    settings["autoJoin"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف الانضمام التلقائي")
            elif text_lower == 'autoleave on':
                if sender in Owner:
                    settings["autoLeave"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل المغادرة التلقائية")
            elif text_lower == 'autoleave off':
                if sender in Owner:
                    settings["autoLeave"] = False
                    nadya.sendMessage(to, "❌ تم إيقاف المغادرة التلقائية")
            elif text_lower == 'autojoinlink on':
                settings["autoJoinTicket"] = True
                nadya.sendMessage(to, "✅ تم تفعيل الانضمام بالرابط")
            elif text_lower == 'autojoinlink off':
                settings["autoJoinTicket"] = False
                nadya.sendMessage(to, "❌ تم إيقاف الانضمام بالرابط")
            elif text_lower.startswith("adminadd"):
                if sender in Owner and 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']: admin[user['M']] = True
                    backupData()
                    nadya.sendMessage(to, "✅ تمت إضافة أدمن جديد")
            elif text_lower.startswith("admindel"):
                if sender in Owner and 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        if user['M'] in admin: del admin[user['M']]
                    backupData()
                    nadya.sendMessage(to, "✅ تم حذف الأدمن")
            elif text_lower == 'adminlist':
                if sender in Owner:
                    if not admin: nadya.sendMessage(to, "❌ لا يوجد أدمنز")
                    else:
                        msg_text = "╔═══[ Admin List ]\n"
                        for mid in admin:
                            msg_text += f"║ ✪ {nadya.getContact(mid).displayName}\n"
                        nadya.sendMessage(to, msg_text + "╚═══════════════")
            elif text_lower.startswith("owneradd"):
                if sender in Owner and 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']: Owner[user['M']] = True
                    backupData()
                    nadya.sendMessage(to, "✅ تمت إضافة مالك جديد")
            elif text_lower.startswith("ownerdel"):
                if sender in Owner and 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        if user['M'] in Owner: del Owner[user['M']]
                    backupData()
                    nadya.sendMessage(to, "✅ تم حذف المالك")
            elif text_lower == 'ownerlist':
                if sender in Owner:
                    if not Owner: nadya.sendMessage(to, "❌ لا يوجد مالكين")
                    else:
                        msg_text = "╔═══[ Owner List ]\n"
                        for mid in Owner:
                            msg_text += f"║ ✪ {nadya.getContact(mid).displayName}\n"
                        nadya.sendMessage(to, msg_text + "╚═══════════════")
            elif text_lower == 'bancontact':
                if sender in Owner:
                    settings["wblacklist"] = True
                    nadya.sendMessage(to, "📤 أرسل جهة الاتصال للحظر")
            elif text_lower == 'unbancontact':
                if sender in Owner:
                    settings["dblacklist"] = True
                    nadya.sendMessage(to, "📤 أرسل جهة الاتصال لإلغاء الحظر")
            elif text_lower == 'banlist':
                if sender in Owner:
                    if not settings["blacklist"]: nadya.sendMessage(to, "❌ قائمة الحظر فارغة")
                    else:
                        msg_text = "╔═══[ Ban List ]\n"
                        num = 1
                        for mid in settings["blacklist"]:
                            msg_text += f"║ [{num}] {nadya.getContact(mid).displayName}\n"
                            num += 1
                        nadya.sendMessage(to, msg_text + f"╚═══[ Total: {len(settings['blacklist'])} ]")
            elif text_lower == 'clearban':
                if sender in Owner:
                    settings["blacklist"] = {}
                    nadya.sendMessage(to, "✅ تم مسح قائمة الحظر")
            elif text_lower == 'me':
                sendMessageWithMention(to, nadyaMID)
                nadya.sendContact(to, nadyaMID)
            elif text_lower == 'mymid':
                nadya.sendMessage(to, f"📱 معرفي:\n{nadyaMID}")
            elif text_lower == 'myname':
                nadya.sendMessage(to, f"👤 اسمي:\n{nadya.getContact(nadyaMID).displayName}")
            elif text_lower == 'mybio':
                nadya.sendMessage(to, f"📝 حالتي:\n{nadya.getContact(nadyaMID).statusMessage}")
            elif text_lower == 'mypicture':
                me = nadya.getContact(nadyaMID)
                nadya.sendImageWithURL(to, f"http://dl.profile.line-cdn.net/{me.pictureStatus}")
            elif text_lower == 'myvideoprofile':
                me = nadya.getContact(nadyaMID)
                nadya.sendVideoWithURL(to, f"http://dl.profile.line-cdn.net/{me.pictureStatus}/vp")
            elif text_lower == 'mycover':
                nadya.sendImageWithURL(to, nadya.getProfileCoverURL(nadyaMID))
            elif text_lower == 'cpp':
                settings["changePicture"] = True
                nadya.sendMessage(to, "📸 أرسل الصورة الجديدة")
            elif text_lower.startswith("stealcontact"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        nadya.sendContact(to, user['M'])
            elif text_lower.startswith("stealmid"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    ret_ = "📱 [ Mid User ]\n"
                    for user in mention['MENTIONEES']:
                        ret_ += f"{user['M']}\n"
                    nadya.sendMessage(to, ret_)
            elif text_lower.startswith("stealname"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        nadya.sendMessage(to, f"👤 [ Display Name ]\n{nadya.getContact(user['M']).displayName}")
            elif text_lower.startswith("stealbio"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        nadya.sendMessage(to, f"📝 [ Status Message ]\n{nadya.getContact(user['M']).statusMessage}")
            elif text_lower.startswith("stealpicture"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        path = f"http://dl.profile.line-cdn.net/{nadya.getContact(user['M']).pictureStatus}"
                        nadya.sendImageWithURL(to, path)
            elif text_lower.startswith("stealvideoprofile"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        path = f"http://dl.profile.line-cdn.net/{nadya.getContact(user['M']).pictureStatus}/vp"
                        nadya.sendVideoWithURL(to, path)
            elif text_lower.startswith("stealcover"):
                if 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        nadya.sendImageWithURL(to, nadya.getProfileCoverURL(user['M']))
            elif text_lower.startswith("cloneprofile"):
                if sender in Owner and 'MENTION' in msg.contentMetadata.keys():
                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                    for user in mention['MENTIONEES']:
                        try:
                            nadya.cloneContactProfile(user['M'])
                            nadya.sendMessage(to, "✅ تم الاستنساخ - انتظر تحديث الملف الشخصي")
                        except:
                            nadya.sendMessage(to, "❌ فشل الاسترجاع")
            elif text_lower == 'groupcreator':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    if group.creator: nadya.sendContact(to, group.creator.mid)
            elif text_lower == 'groupid':
                if msg.toType == 2:
                    nadya.sendMessage(to, f"🆔 معرف المجموعة:\n{nadya.getGroup(to).id}")
            elif text_lower == 'groupname':
                if msg.toType == 2:
                    nadya.sendMessage(to, f"📝 اسم المجموعة:\n{nadya.getGroup(to).name}")
            elif text_lower == 'grouppicture':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    nadya.sendImageWithURL(to, f"http://dl.profile.line-cdn.net/{group.pictureStatus}")
            elif text_lower == 'groupticket':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    if not group.preventedJoinByTicket:
                        ticket = nadya.reissueGroupTicket(to)
                        nadya.sendMessage(to, f"🔗 رابط المجموعة:\nhttps://line.me/R/ti/g/{ticket}")
                    else:
                        nadya.sendMessage(to, "❌ الرابط مغلق\nاستخدم: groupticket on")
            elif text_lower == 'groupticket on':
                if msg.toType == 2 and (sender in admin or sender in Owner):
                    group = nadya.getGroup(to)
                    group.preventedJoinByTicket = False
                    nadya.updateGroup(group)
                    nadya.sendMessage(to, "✅ تم فتح رابط المجموعة")
            elif text_lower == 'groupticket off':
                if msg.toType == 2 and (sender in admin or sender in Owner):
                    group = nadya.getGroup(to)
                    group.preventedJoinByTicket = True
                    nadya.updateGroup(group)
                    nadya.sendMessage(to, "✅ تم إغلاق رابط المجموعة")
            elif text_lower == 'cgp':
                if msg.toType == 2:
                    settings["changeGroupPicture"].append(to)
                    nadya.sendMessage(to, "📸 أرسل صورة المجموعة الجديدة")
            elif text_lower == 'mention':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    k = len(group.members) // 100
                    for a in range(k + 1):
                        txt = ''
                        s = 0
                        b = []
                        for i in group.members[a*100:(a+1)*100]:
                            b.append({"S": str(s), "E": str(s+6), "M": i.mid})
                            s += 7
                            txt += '@x \n'
                        nadya.sendMessage(to, text=txt, contentMetadata={'MENTION': json.dumps({'MENTIONEES': b})}, contentType=0)
                    nadya.sendMessage(to, f"📢 تم منشن {len(group.members)} عضو")
            elif text_lower == 'groupinfo':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    gCreator = group.creator.displayName if group.creator else "غير معروف"
                    gPending = "0" if group.invitee is None else str(len(group.invitee))
                    gQr = "مغلق" if group.preventedJoinByTicket else "مفتوح"
                    gTicket = "لا يوجد" if group.preventedJoinByTicket else f"https://line.me/R/ti/g/{nadya.reissueGroupTicket(group.id)}"
                    nadya.sendMessage(to, f"""╔═══[ Group Info ]
║ 📝 الاسم: {group.name}
║ 🆔 المعرف: {group.id}
║ 👤 المنشئ: {gCreator}
║ 👥 الأعضاء: {len(group.members)}
║ ⏳ المعلقين: {gPending}
║ 🔗 الرابط: {gQr}
║ 🌐 التذكرة: {gTicket}
╚═══════════════""")
                    nadya.sendImageWithURL(to, f"http://dl.profile.line-cdn.net/{group.pictureStatus}")
            elif text_lower == 'memberlist':
                if msg.toType == 2:
                    group = nadya.getGroup(to)
                    msg_text = "╔═══[ Member List ]\n"
                    for num, member in enumerate(group.members, 1):
                        msg_text += f"║ {num}. {member.displayName}\n"
                    nadya.sendMessage(to, msg_text + f"╚═══[ Total: {len(group.members)} ]")
            elif text_lower == 'grouplist':
                groups = nadya.getGroupIdsJoined()
                msg_text = "╔═══[ Group List ]\n"
                for num, gid in enumerate(groups, 1):
                    group = nadya.getGroup(gid)
                    msg_text += f"║ {num}. {group.name} | {len(group.members)}\n"
                nadya.sendMessage(to, msg_text + f"╚═══[ Total: {len(groups)} ]")
            elif text_lower.startswith("kick"):
                if sender in admin or sender in Owner:
                    if 'MENTION' in msg.contentMetadata.keys():
                        mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                        for user in mention['MENTIONEES']:
                            if user['M'] not in Bots and user['M'] not in Owner:
                                random.choice(KAC).kickoutFromGroup(to, [user['M']])
                        nadya.sendMessage(to, "✅ تم طرد العضو")
            elif text_lower == 'kickall':
                if sender in Owner and msg.toType == 2:
                    for member in nadya.getGroup(to).members:
                        if member.mid not in Bots and member.mid not in Owner and member.mid not in admin:
                            try:
                                random.choice(KAC).kickoutFromGroup(to, [member.mid])
                                time.sleep(0.5)
                            except: pass
                    nadya.sendMessage(to, "✅ تم طرد جميع الأعضاء")
            elif text_lower == 'joinall':
                if sender in Owner and msg.toType == 2:
                    G = nadya.getGroup(to)
                    G.preventedJoinByTicket = False
                    nadya.updateGroup(G)
                    Ticket = nadya.reissueGroupTicket(to)
                    for bot in [ki, ki2, ki3, ki4]:
                        try: bot.acceptGroupInvitationByTicket(to, Ticket)
                        except: pass
                    G.preventedJoinByTicket = True
                    nadya.updateGroup(G)
                    nadya.sendMessage(to, "✅ تم انضمام جميع البوتات")
            elif text_lower == 'byeall':
                if sender in Owner:
                    for bot in [ki, ki2, ki3, ki4]:
                        try: bot.leaveGroup(to)
                        except: pass
                    nadya.sendMessage(to, "👋 المساعدين غادروا المجموعة")
            elif text_lower == 'status':
                nadya.sendMessage(to, f"""╔═══[ Status ]
║ Protect: {'✅' if settings['protect'] else '❌'}
║ QR Protect: {'✅' if settings['qrprotect'] else '❌'}
║ Invite Protect: {'✅' if settings['inviteprotect'] else '❌'}
║ Cancel Protect: {'✅' if settings['cancelprotect'] else '❌'}
║ Auto Add: {'✅' if settings['autoAdd'] else '❌'}
║ Auto Join: {'✅' if settings['autoJoin'] else '❌'}
║ Auto Leave: {'✅' if settings['autoLeave'] else '❌'}
║ Auto Join Link: {'✅' if settings['autoJoinTicket'] else '❌'}
╚═══════════════""")
            elif text_lower == 'speed':
                start = time.time()
                nadya.sendMessage(to, "⏱️ جاري القياس...")
                nadya.sendMessage(to, f"⚡ السرعة: {time.time() - start:.3f}s")
            elif text_lower == 'runtime':
                nadya.sendMessage(to, f"⏰ وقت التشغيل:\n{format_timespan(time.time() - botStart)}")
            elif text_lower == 'restart':
                if sender in Owner:
                    nadya.sendMessage(to, "🔄 جاري إعادة التشغيل...")
                    time.sleep(3)
                    backupData()
                    import os, sys
                    os.execl(sys.executable, sys.executable, *sys.argv)
        
        backupData()
    except Exception as error:
        print(f"Error: {error}")

print("╔═══════════════════════════════════╗")
print("║   BOT STARTED SUCCESSFULLY ✅      ║")
print("╚═══════════════════════════════════╝")

while True:
    try:
        ops = oepoll.singleTrace(count=50)
        if ops:
            for op in ops:
                lineBot(op)
                oepoll.setRevision(op.revision)
    except KeyboardInterrupt:
        print("\n👋 Bot Stopped")
        backupData()
        break
    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(1)ستنساخ")
                        break
            elif text_lower == 'restoreprofile':
                if sender in Owner:
                    try:
                        nadyaProfile.displayName = myProfile["displayName"]
                        nadyaProfile.statusMessage = myProfile["statusMessage"]
                        nadyaProfile.pictureStatus = myProfile["pictureStatus"]
                        nadya.updateProfileAttribute(8, nadyaProfile.pictureStatus)
                        nadya.updateProfile(nadyaProfile)
                        nadya.sendMessage(to, "✅ تم استرجاع الملف الشخصي")
                    except:
                        nadya.sendMessage(to, "❌ فشل الا
