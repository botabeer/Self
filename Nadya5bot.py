# -*- coding: utf-8 -*-
from linepy import *
from datetime import datetime
from time import sleep
import time, random, sys, json, codecs, threading, os

botStart = time.time()

# تهيئة البوتات
nadya = LINE()
nadyaMID = nadya.profile.mid

ki = LINE()
kiMID = ki.profile.mid

ki2 = LINE()
ki2MID = ki2.profile.mid

ki3 = LINE()
ki3MID = ki3.profile.mid

ki4 = LINE()
ki4MID = ki4.profile.mid

KAC = [nadya, ki, ki2, ki3, ki4]
Bots = [nadyaMID, kiMID, ki2MID, ki3MID, ki4MID]

# تحميل الإعدادات
with open('Owner.json', 'r') as fp:
    Owner = json.load(fp)
    
with open('admin.json', 'r') as fp:
    admin = json.load(fp)

settingsOpen = codecs.open("temp.json", "r", "utf-8")
settings = json.load(settingsOpen)

# إعداد OEPoll
oepoll = OEPoll(nadya)
oepoll1 = OEPoll(ki)
oepoll2 = OEPoll(ki2)
oepoll3 = OEPoll(ki3)
oepoll4 = OEPoll(ki4)

def backupData():
    try:
        with codecs.open('temp.json', 'w', 'utf-8') as f:
            json.dump(settings, f, sort_keys=True, indent=4, ensure_ascii=False)
        return True
    except Exception as error:
        print(f"[ERROR] {error}")
        return False

def logError(text):
    print(f"[ERROR] {text}")
    with open("errorLog.txt", "a") as error:
        error.write(f"\n[{datetime.now()}] {text}")

def lineBot(op):
    try:
        # نهاية العملية
        if op.type == 0:
            return
            
        # طرد عضو - الحماية الرئيسية
        if op.type == 19:
            try:
                # حماية البوتات من الطرد
                if op.param3 in Bots:
                    if op.param2 not in Bots and op.param2 not in admin and op.param2 not in Owner:
                        # إعادة دعوة البوت المطرود
                        G = nadya.getGroup(op.param1)
                        G.preventedJoinByTicket = False
                        nadya.updateGroup(G)
                        
                        Ticket = nadya.reissueGroupTicket(op.param1)
                        
                        # إعادة جميع البوتات
                        for bot in KAC:
                            try:
                                bot.acceptGroupInvitationByTicket(op.param1, Ticket)
                            except:
                                pass
                        
                        # إغلاق الدعوة
                        G.preventedJoinByTicket = True
                        nadya.updateGroup(G)
                        
                        # طرد الشخص الذي طرد البوت
                        random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                        
                        # إضافته للقائمة السوداء
                        if settings["protect"]:
                            settings["blacklist"][op.param2] = True
                            backupData()
                            
                # حماية الأعضاء العاديين
                elif op.param2 not in Bots and op.param2 not in admin and op.param2 not in Owner:
                    if settings["protect"]:
                        # طرد من قام بالطرد
                        random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                        # إعادة دعوة العضو المطرود
                        random.choice(KAC).inviteIntoGroup(op.param1, [op.param3])
                        # إضافة للقائمة السوداء
                        settings["blacklist"][op.param2] = True
                        backupData()
            except Exception as e:
                logError(e)
                
        # حماية من الدعوات
        if op.type == 13:
            if settings["inviteprotect"]:
                if op.param2 not in Bots and op.param2 not in admin and op.param2 not in Owner:
                    try:
                        # إلغاء الدعوة
                        random.choice(KAC).cancelGroupInvitation(op.param1, [op.param3])
                        # طرد من قام بالدعوة
                        random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                        # القائمة السوداء
                        settings["blacklist"][op.param2] = True
                        backupData()
                    except:
                        pass
                        
        # حماية QR Code
        if op.type == 11:
            if settings["qrprotect"]:
                if op.param2 not in Bots and op.param2 not in admin and op.param2 not in Owner:
                    try:
                        G = nadya.getGroup(op.param1)
                        G.preventedJoinByTicket = True
                        nadya.updateGroup(G)
                        random.choice(KAC).kickoutFromGroup(op.param1, [op.param2])
                        settings["blacklist"][op.param2] = True
                        backupData()
                    except:
                        pass
                        
        # حماية من إلغاء الدعوات
        if op.type == 14:
            if settings["cancelprotect"]:
                if op.param2 not in Bots and op.param2 not in admin and op.param2 not in Owner:
                    try:
                        random.choice(KAC).cancelGroupInvitation(op.param1, [op.param3])
                        settings["blacklist"][op.param2] = True
                        backupData()
                    except:
                        pass
                        
        # معالجة الأوامر
        if op.type == 26:
            msg = op.message
            text = msg.text
            sender = msg._from
            to = msg.to if msg.toType == 2 else sender
            
            if text and sender in Owner:
                # تفعيل/تعطيل الحماية
                if text.lower() == 'protect on':
                    settings["protect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل الحماية الكاملة")
                    backupData()
                    
                elif text.lower() == 'protect off':
                    settings["protect"] = False
                    nadya.sendMessage(to, "❌ تم تعطيل الحماية الكاملة")
                    backupData()
                    
                elif text.lower() == 'qrprotect on':
                    settings["qrprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية QR")
                    backupData()
                    
                elif text.lower() == 'qrprotect off':
                    settings["qrprotect"] = False
                    nadya.sendMessage(to, "❌ تم تعطيل حماية QR")
                    backupData()
                    
                elif text.lower() == 'inviteprotect on':
                    settings["inviteprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية الدعوات")
                    backupData()
                    
                elif text.lower() == 'inviteprotect off':
                    settings["inviteprotect"] = False
                    nadya.sendMessage(to, "❌ تم تعطيل حماية الدعوات")
                    backupData()
                    
                elif text.lower() == 'cancelprotect on':
                    settings["cancelprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل حماية إلغاء الدعوات")
                    backupData()
                    
                elif text.lower() == 'cancelprotect off':
                    settings["cancelprotect"] = False
                    nadya.sendMessage(to, "❌ تم تعطيل حماية إلغاء الدعوات")
                    backupData()
                    
                elif text.lower() == 'setpro on':
                    settings["protect"] = True
                    settings["qrprotect"] = True
                    settings["inviteprotect"] = True
                    settings["cancelprotect"] = True
                    nadya.sendMessage(to, "✅ تم تفعيل جميع أنواع الحماية")
                    backupData()
                    
                elif text.lower() == 'setpro off':
                    settings["protect"] = False
                    settings["qrprotect"] = False
                    settings["inviteprotect"] = False
                    settings["cancelprotect"] = False
                    nadya.sendMessage(to, "❌ تم تعطيل جميع أنواع الحماية")
                    backupData()
                    
                elif text.lower() == 'status':
                    ret_ = "═══ حالة الحماية ═══\n"
                    ret_ += f"🛡️ الحماية الكاملة: {'✅' if settings['protect'] else '❌'}\n"
                    ret_ += f"🔐 حماية QR: {'✅' if settings['qrprotect'] else '❌'}\n"
                    ret_ += f"📩 حماية الدعوات: {'✅' if settings['inviteprotect'] else '❌'}\n"
                    ret_ += f"🚫 حماية إلغاء الدعوات: {'✅' if settings['cancelprotect'] else '❌'}\n"
                    ret_ += f"📋 القائمة السوداء: {len(settings.get('blacklist', {}))}"
                    nadya.sendMessage(to, ret_)
                    
                elif text.lower() == 'clearban':
                    settings["blacklist"] = {}
                    nadya.sendMessage(to, "✅ تم مسح القائمة السوداء")
                    backupData()
                    
        backupData()
        
    except Exception as error:
        logError(error)

# حلقة البوت الرئيسية
while True:
    try:
        ops = oepoll.singleTrace(count=50)
        if ops is not None:
            for op in ops:
                lineBot(op)
                oepoll.setRevision(op.revision)
    except KeyboardInterrupt:
        print("\n[INFO] تم إيقاف البوت")
        break
    except Exception as e:
        logError(e)
        time.sleep(3)
