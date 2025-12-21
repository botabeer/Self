# -*- coding: utf-8 -*-
from akad.ttypes import Message
from random import randint

import json, ntpath

def loggedIn(func):
    """مُزخرِف للتحقق من تسجيل الدخول قبل تنفيذ الدالة"""
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other('You want to call the function, you must login to LINE')
    return checkLogin

class Talk(object):
    """
    فئة المحادثة الرئيسية للتعامل مع الرسائل والمستخدمين والمجموعات
    """
    isLogin = False
    _messageReq = {}
    _unsendMessageReq = 0

    def __init__(self):
        """تهيئة فئة المحادثة"""
        self.isLogin = True

    """وظائف المستخدم"""

    @loggedIn
    def acquireEncryptedAccessToken(self, featureType=2):
        """
        الحصول على رمز وصول مشفر
        
        المعاملات:
            featureType: نوع الميزة (افتراضي: 2)
        
        العائد:
            رمز الوصول المشفر
        """
        return self.talk.getChatRoomAnnouncements(chatRoomMid)

    @loggedIn
    def createChatRoomAnnouncement(self, chatRoomMid, type, contents):
        """
        إنشاء إعلان في غرفة محادثة
        
        المعاملات:
            chatRoomMid: معرف غرفة المحادثة
            type: نوع الإعلان
            contents: محتوى الإعلان
        
        العائد:
            نتيجة الإنشاء
        """
        return self.talk.createChatRoomAnnouncement(0, chatRoomMid, type, contents)

    @loggedIn
    def removeChatRoomAnnouncement(self, chatRoomMid, announcementSeq):
        """
        حذف إعلان من غرفة محادثة
        
        المعاملات:
            chatRoomMid: معرف غرفة المحادثة
            announcementSeq: تسلسل الإعلان
        
        العائد:
            نتيجة الحذف
        """
        return self.talk.removeChatRoomAnnouncement(0, chatRoomMid, announcementSeq)

    @loggedIn
    def getGroupWithoutMembers(self, groupId):
        """
        الحصول على معلومات مجموعة بدون الأعضاء
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            كائن المجموعة
        """
        return self.talk.getGroupWithoutMembers(groupId)
    
    @loggedIn
    def findGroupByTicket(self, ticketId):
        """
        البحث عن مجموعة بواسطة التذكرة
        
        المعاملات:
            ticketId: معرف التذكرة
        
        العائد:
            كائن المجموعة
        """
        return self.talk.findGroupByTicket(ticketId)

    @loggedIn
    def acceptGroupInvitation(self, groupId):
        """
        قبول دعوة مجموعة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            نتيجة القبول
        """
        return self.talk.acceptGroupInvitation(0, groupId)

    @loggedIn
    def acceptGroupInvitationByTicket(self, groupId, ticketId):
        """
        قبول دعوة مجموعة بواسطة التذكرة
        
        المعاملات:
            groupId: معرف المجموعة
            ticketId: معرف التذكرة
        
        العائد:
            نتيجة القبول
        """
        return self.talk.acceptGroupInvitationByTicket(0, groupId, ticketId)

    @loggedIn
    def cancelGroupInvitation(self, groupId, contactIds):
        """
        إلغاء دعوة مجموعة
        
        المعاملات:
            groupId: معرف المجموعة
            contactIds: قائمة معرفات جهات الاتصال
        
        العائد:
            نتيجة الإلغاء
        """
        return self.talk.cancelGroupInvitation(0, groupId, contactIds)

    @loggedIn
    def createGroup(self, name, midlist):
        """
        إنشاء مجموعة جديدة
        
        المعاملات:
            name: اسم المجموعة
            midlist: قائمة معرفات الأعضاء
        
        العائد:
            كائن المجموعة الجديدة
        """
        return self.talk.createGroup(0, name, midlist)

    @loggedIn
    def getGroup(self, groupId):
        """
        الحصول على معلومات مجموعة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            كائن المجموعة
        """
        return self.talk.getGroup(groupId)

    @loggedIn
    def getGroups(self, groupIds):
        """
        الحصول على معلومات عدة مجموعات
        
        المعاملات:
            groupIds: قائمة معرفات المجموعات
        
        العائد:
            قائمة كائنات المجموعات
        """
        return self.talk.getGroups(groupIds)

    @loggedIn
    def getGroupsV2(self, groupIds):
        """
        الحصول على معلومات عدة مجموعات (الإصدار 2)
        
        المعاملات:
            groupIds: قائمة معرفات المجموعات
        
        العائد:
            قائمة كائنات المجموعات
        """
        return self.talk.getGroupsV2(groupIds)

    @loggedIn
    def getCompactGroup(self, groupId):
        """
        الحصول على معلومات مجموعة مختصرة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            كائن المجموعة المختصر
        """
        return self.talk.getCompactGroup(groupId)

    @loggedIn
    def getCompactRoom(self, roomId):
        """
        الحصول على معلومات غرفة مختصرة
        
        المعاملات:
            roomId: معرف الغرفة
        
        العائد:
            كائن الغرفة المختصر
        """
        return self.talk.getCompactRoom(roomId)

    @loggedIn
    def getGroupIdsByName(self, groupName):
        """
        الحصول على معرفات المجموعات بواسطة الاسم
        
        المعاملات:
            groupName: اسم المجموعة
        
        العائد:
            قائمة معرفات المجموعات
        """
        gIds = []
        for gId in self.getGroupIdsJoined():
            g = self.getCompactGroup(gId)
            if groupName in g.name:
                gIds.append(gId)
        return gIds

    @loggedIn
    def getGroupIdsInvited(self):
        """
        الحصول على معرفات المجموعات المدعو إليها
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getGroupIdsInvited()

    @loggedIn
    def getGroupIdsJoined(self):
        """
        الحصول على معرفات المجموعات المنضم إليها
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getGroupIdsJoined()

    @loggedIn
    def updateGroupPreferenceAttribute(self, groupMid, updatedAttrs):
        """
        تحديث خصائص تفضيلات المجموعة
        
        المعاملات:
            groupMid: معرف المجموعة
            updatedAttrs: الخصائص المحدثة
        
        العائد:
            نتيجة التحديث
        """
        return self.talk.updateGroupPreferenceAttribute(0, groupMid, updatedAttrs)

    @loggedIn
    def inviteIntoGroup(self, groupId, midlist):
        """
        دعوة أشخاص إلى المجموعة
        
        المعاملات:
            groupId: معرف المجموعة
            midlist: قائمة معرفات المدعوين
        
        العائد:
            نتيجة الدعوة
        """
        return self.talk.inviteIntoGroup(0, groupId, midlist)

    @loggedIn
    def kickoutFromGroup(self, groupId, midlist):
        """
        طرد أعضاء من المجموعة
        
        المعاملات:
            groupId: معرف المجموعة
            midlist: قائمة معرفات الأعضاء
        
        العائد:
            نتيجة الطرد
        """
        return self.talk.kickoutFromGroup(0, groupId, midlist)

    @loggedIn
    def leaveGroup(self, groupId):
        """
        مغادرة مجموعة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            نتيجة المغادرة
        """
        return self.talk.leaveGroup(0, groupId)

    @loggedIn
    def rejectGroupInvitation(self, groupId):
        """
        رفض دعوة مجموعة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            نتيجة الرفض
        """
        return self.talk.rejectGroupInvitation(0, groupId)

    @loggedIn
    def reissueGroupTicket(self, groupId):
        """
        إعادة إصدار تذكرة المجموعة
        
        المعاملات:
            groupId: معرف المجموعة
        
        العائد:
            التذكرة الجديدة
        """
        return self.talk.reissueGroupTicket(groupId)

    @loggedIn
    def updateGroup(self, groupObject):
        """
        تحديث معلومات المجموعة
        
        المعاملات:
            groupObject: كائن المجموعة المحدث
        
        العائد:
            نتيجة التحديث
        """
        return self.talk.updateGroup(0, groupObject)

    """وظائف الغرف"""

    @loggedIn
    def createRoom(self, midlist):
        """
        إنشاء غرفة محادثة جديدة
        
        المعاملات:
            midlist: قائمة معرفات الأعضاء
        
        العائد:
            كائن الغرفة الجديدة
        """
        return self.talk.createRoom(0, midlist)

    @loggedIn
    def getRoom(self, roomId):
        """
        الحصول على معلومات غرفة
        
        المعاملات:
            roomId: معرف الغرفة
        
        العائد:
            كائن الغرفة
        """
        return self.talk.getRoom(roomId)

    @loggedIn
    def inviteIntoRoom(self, roomId, midlist):
        """
        دعوة أشخاص إلى الغرفة
        
        المعاملات:
            roomId: معرف الغرفة
            midlist: قائمة معرفات المدعوين
        
        العائد:
            نتيجة الدعوة
        """
        return self.talk.inviteIntoRoom(0, roomId, midlist)

    @loggedIn
    def leaveRoom(self, roomId):
        """
        مغادرة غرفة
        
        المعاملات:
            roomId: معرف الغرفة
        
        العائد:
            نتيجة المغادرة
        """
        return self.talk.leaveRoom(0, roomId)

    """وظائف المكالمات"""
        
    @loggedIn
    def acquireCallTalkRoute(self, to):
        """
        الحصول على مسار المكالمة
        
        المعاملات:
            to: معرف المستلم
        
        العائد:
            معلومات مسار المكالمة
        """
        return self.talk.acquireCallRoute(to)
    
    """وظائف الإبلاغ"""

    @loggedIn
    def reportSpam(self, chatMid, memberMids=[], spammerReasons=[], senderMids=[], spamMessageIds=[], spamMessages=[]):
        """
        الإبلاغ عن رسائل مزعجة
        
        المعاملات:
            chatMid: معرف المحادثة
            memberMids: قائمة معرفات الأعضاء
            spammerReasons: أسباب الإزعاج
            senderMids: معرفات المرسلين
            spamMessageIds: معرفات الرسائل المزعجة
            spamMessages: الرسائل المزعجة
        
        العائد:
            نتيجة الإبلاغ
        """
        return self.talk.reportSpam(chatMid, memberMids, spammerReasons, senderMids, spamMessageIds, spamMessages)
        
    @loggedIn
    def reportSpammer(self, spammerMid, spammerReasons=[], spamMessageIds=[]):
        """
        الإبلاغ عن مستخدم مزعج
        
        المعاملات:
            spammerMid: معرف المستخدم المزعج
            spammerReasons: أسباب الإزعاج
            spamMessageIds: معرفات الرسائل المزعجة
        
        العائد:
            نتيجة الإبلاغ
        """
        return self.talk.reportSpammer(spammerMid, spammerReasons, spamMessageIds)acquireEncryptedAccessToken(featureType)

    @loggedIn
    def getProfile(self):
        """
        الحصول على الملف الشخصي للمستخدم الحالي
        
        العائد:
            كائن الملف الشخصي
        """
        return self.talk.getProfile()

    @loggedIn
    def getSettings(self):
        """
        الحصول على إعدادات الحساب
        
        العائد:
            كائن الإعدادات
        """
        return self.talk.getSettings()

    @loggedIn
    def getUserTicket(self):
        """
        الحصول على تذكرة المستخدم
        
        العائد:
            كائن التذكرة
        """
        return self.talk.getUserTicket()

    @loggedIn
    def updateProfile(self, profileObject):
        """
        تحديث الملف الشخصي
        
        المعاملات:
            profileObject: كائن الملف الشخصي الجديد
        
        العائد:
            نتيجة التحديث
        """
        return self.talk.updateProfile(0, profileObject)

    @loggedIn
    def updateSettings(self, settingObject):
        """
        تحديث الإعدادات
        
        المعاملات:
            settingObject: كائن الإعدادات الجديد
        
        العائد:
            نتيجة التحديث
        """
        return self.talk.updateSettings(0, settingObject)

    @loggedIn
    def updateProfileAttribute(self, attrId, value):
        """
        تحديث خاصية في الملف الشخصي
        
        المعاملات:
            attrId: معرف الخاصية
            value: القيمة الجديدة
        
        العائد:
            نتيجة التحديث
        """
        return self.talk.updateProfileAttribute(0, attrId, value)

    """وظائف العمليات"""

    @loggedIn
    def fetchOperation(self, revision, count):
        """
        جلب العمليات من الخادم
        
        المعاملات:
            revision: رقم المراجعة
            count: عدد العمليات
        
        العائد:
            قائمة العمليات
        """
        return self.talk.fetchOperations(revision, count)

    @loggedIn
    def getLastOpRevision(self):
        """
        الحصول على آخر رقم مراجعة للعمليات
        
        العائد:
            رقم المراجعة
        """
        return self.talk.getLastOpRevision()

    """وظائف الرسائل"""

    @loggedIn
    def sendMessage(self, to, text, contentMetadata={}, contentType=0):
        """
        إرسال رسالة نصية
        
        المعاملات:
            to: معرف المستلم (مجموعة أو مستخدم)
            text: نص الرسالة
            contentMetadata: بيانات المحتوى الإضافية (افتراضي: {})
            contentType: نوع المحتوى (افتراضي: 0)
        
        العائد:
            كائن الرسالة المرسلة
        """
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)
    
    @loggedIn
    def sendMessageWithMention(self, to, text='', dataMid=[]):
        """
        إرسال رسالة مع الإشارة إلى مستخدمين (Mention)
        
        المعاملات:
            to: معرف المستلم
            text: نص الرسالة
            dataMid: قائمة معرفات المستخدمين للإشارة إليهم
        
        العائد:
            كائن الرسالة المرسلة
        """
        arr = []
        list_text=''
        if '[list]' in text.lower():
            i=0
            for l in dataMid:
                list_text+='\n@[list-'+str(i)+']'
                i=i+1
            text=text.replace('[list]', list_text)
        elif '[list-' in text.lower():
            text=text
        else:
            i=0
            for l in dataMid:
                list_text+=' @[list-'+str(i)+']'
                i=i+1
            text=text+list_text
        i=0
        for l in dataMid:
            mid=l
            name='@[list-'+str(i)+']'
            ln_text=text.replace('\n',' ')
            if ln_text.find(name):
                line_s=int(ln_text.index(name))
                line_e=(int(line_s)+int(len(name)))
            arrData={'S': str(line_s), 'E': str(line_e), 'M': mid}
            arr.append(arrData)
            i=i+1
        contentMetadata={'MENTION':str('{"MENTIONEES":' + json.dumps(arr).replace(' ','') + '}')}
        return self.sendMessage(to, text, contentMetadata)

    @loggedIn
    def sendSticker(self, to, packageId, stickerId):
        """
        إرسال ملصق
        
        المعاملات:
            to: معرف المستلم
            packageId: معرف حزمة الملصقات
            stickerId: معرف الملصق
        
        العائد:
            كائن الرسالة المرسلة
        """
        contentMetadata = {
            'STKVER': '100',
            'STKPKGID': packageId,
            'STKID': stickerId
        }
        return self.sendMessage(to, '', contentMetadata, 7)
        
    @loggedIn
    def sendContact(self, to, mid):
        """
        إرسال جهة اتصال
        
        المعاملات:
            to: معرف المستلم
            mid: معرف جهة الاتصال
        
        العائد:
            كائن الرسالة المرسلة
        """
        contentMetadata = {'mid': mid}
        return self.sendMessage(to, '', contentMetadata, 13)

    @loggedIn
    def sendGift(self, to, productId, productType):
        """
        إرسال هدية
        
        المعاملات:
            to: معرف المستلم
            productId: معرف المنتج
            productType: نوع المنتج ('theme' أو 'sticker')
        
        العائد:
            كائن الرسالة المرسلة
        """
        if productType not in ['theme','sticker']:
            raise Exception('Invalid productType value')
        contentMetadata = {
            'MSGTPL': str(randint(0, 12)),
            'PRDTYPE': productType.upper(),
            'STKPKGID' if productType == 'sticker' else 'PRDID': productId
        }
        return self.sendMessage(to, '', contentMetadata, 9)

    @loggedIn
    def sendMessageAwaitCommit(self, to, text, contentMetadata={}, contentType=0):
        """
        إرسال رسالة مع انتظار التأكيد
        
        المعاملات:
            to: معرف المستلم
            text: نص الرسالة
            contentMetadata: بيانات المحتوى الإضافية (افتراضي: {})
            contentType: نوع المحتوى (افتراضي: 0)
        
        العائد:
            كائن الرسالة المرسلة
        """
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessageAwaitCommit(self._messageReq[to], msg)

    @loggedIn
    def unsendMessage(self, messageId):
        """
        إلغاء إرسال رسالة
        
        المعاملات:
            messageId: معرف الرسالة
        
        العائد:
            نتيجة الإلغاء
        """
        self._unsendMessageReq += 1
        return self.talk.unsendMessage(self._unsendMessageReq, messageId)

    @loggedIn
    def requestResendMessage(self, senderMid, messageId):
        """
        طلب إعادة إرسال رسالة
        
        المعاملات:
            senderMid: معرف المرسل
            messageId: معرف الرسالة
        
        العائد:
            نتيجة الطلب
        """
        return self.talk.requestResendMessage(0, senderMid, messageId)

    @loggedIn
    def respondResendMessage(self, receiverMid, originalMessageId, resendMessage, errorCode):
        """
        الرد على طلب إعادة إرسال رسالة
        
        المعاملات:
            receiverMid: معرف المستلم
            originalMessageId: معرف الرسالة الأصلية
            resendMessage: الرسالة المعاد إرسالها
            errorCode: كود الخطأ
        
        العائد:
            نتيجة الرد
        """
        return self.talk.respondResendMessage(0, receiverMid, originalMessageId, resendMessage, errorCode)

    @loggedIn
    def removeMessage(self, messageId):
        """
        حذف رسالة
        
        المعاملات:
            messageId: معرف الرسالة
        
        العائد:
            نتيجة الحذف
        """
        return self.talk.removeMessage(messageId)
    
    @loggedIn
    def removeAllMessages(self, lastMessageId):
        """
        حذف جميع الرسائل حتى رسالة معينة
        
        المعاملات:
            lastMessageId: معرف آخر رسالة
        
        العائد:
            نتيجة الحذف
        """
        return self.talk.removeAllMessages(0, lastMessageId)

    @loggedIn
    def removeMessageFromMyHome(self, messageId):
        """
        حذف رسالة من صفحتي الرئيسية
        
        المعاملات:
            messageId: معرف الرسالة
        
        العائد:
            نتيجة الحذف
        """
        return self.talk.removeMessageFromMyHome(messageId)

    @loggedIn
    def destroyMessage(self, chatId, messageId):
        """
        إتلاف رسالة نهائياً
        
        المعاملات:
            chatId: معرف المحادثة
            messageId: معرف الرسالة
        
        العائد:
            نتيجة الإتلاف
        """
        return self.talk.destroyMessage(0, chatId, messageId, sessionId)
    
    @loggedIn
    def sendChatChecked(self, consumer, messageId):
        """
        تعليم المحادثة كمقروءة
        
        المعاملات:
            consumer: معرف المستهلك
            messageId: معرف الرسالة
        
        العائد:
            نتيجة العملية
        """
        return self.talk.sendChatChecked(0, consumer, messageId)

    @loggedIn
    def sendEvent(self, messageObject):
        """
        إرسال حدث
        
        المعاملات:
            messageObject: كائن الرسالة
        
        العائد:
            نتيجة الإرسال
        """
        return self.talk.sendEvent(0, messageObject)

    @loggedIn
    def getLastReadMessageIds(self, chatId):
        """
        الحصول على معرفات آخر رسائل مقروءة
        
        المعاملات:
            chatId: معرف المحادثة
        
        العائد:
            قائمة معرفات الرسائل
        """
        return self.talk.getLastReadMessageIds(0, chatId)

    @loggedIn
    def getPreviousMessagesV2WithReadCount(self, messageBoxId, endMessageId, messagesCount=50):
        """
        الحصول على الرسائل السابقة مع عدد القراءة (الإصدار 2)
        
        المعاملات:
            messageBoxId: معرف صندوق الرسائل
            endMessageId: معرف الرسالة النهائية
            messagesCount: عدد الرسائل (افتراضي: 50)
        
        العائد:
            قائمة الرسائل مع عدد القراءة
        """
        return self.talk.getPreviousMessagesV2WithReadCount(messageBoxId, endMessageId, messagesCount)

    """وظائف الكائنات - إرسال الوسائط"""

    @loggedIn
    def sendImage(self, to, path):
        """
        إرسال صورة
        
        المعاملات:
            to: معرف المستلم
            path: مسار الصورة
        
        العائد:
            نتيجة الإرسال
        """
        objectId = self.sendMessage(to=to, text=None, contentType = 1).id
        return self.uploadObjTalk(path=path, type='image', returnAs='bool', objId=objectId)

    @loggedIn
    def sendImageWithURL(self, to, url):
        """
        إرسال صورة من URL
        
        المعاملات:
            to: معرف المستلم
            url: رابط الصورة
        
        العائد:
            نتيجة الإرسال
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendImage(to, path)
        return self.deleteFile(path)

    @loggedIn
    def sendGIF(self, to, path):
        """
        إرسال GIF
        
        المعاملات:
            to: معرف المستلم
            path: مسار ملف GIF
        
        العائد:
            نتيجة الإرسال
        """
        return self.uploadObjTalk(path=path, type='gif', returnAs='bool', to=to)

    @loggedIn
    def sendGIFWithURL(self, to, url):
        """
        إرسال GIF من URL
        
        المعاملات:
            to: معرف المستلم
            url: رابط GIF
        
        العائد:
            نتيجة الإرسال
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendGIF(to, path)
        return self.deleteFile(path)

    @loggedIn
    def sendVideo(self, to, path):
        """
        إرسال فيديو
        
        المعاملات:
            to: معرف المستلم
            path: مسار الفيديو
        
        العائد:
            نتيجة الإرسال
        """
        objectId = self.sendMessage(to=to, text=None, contentMetadata={'VIDLEN': '60000','DURATION': '60000'}, contentType = 2).id
        return self.uploadObjTalk(path=path, type='video', returnAs='bool', objId=objectId)

    @loggedIn
    def sendVideoWithURL(self, to, url):
        """
        إرسال فيديو من URL
        
        المعاملات:
            to: معرف المستلم
            url: رابط الفيديو
        
        العائد:
            نتيجة الإرسال
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendVideo(to, path)
        return self.deleteFile(path)

    @loggedIn
    def sendAudio(self, to, path):
        """
        إرسال ملف صوتي
        
        المعاملات:
            to: معرف المستلم
            path: مسار الملف الصوتي
        
        العائد:
            نتيجة الإرسال
        """
        objectId = self.sendMessage(to=to, text=None, contentType = 3).id
        return self.uploadObjTalk(path=path, type='audio', returnAs='bool', objId=objectId)

    @loggedIn
    def sendAudioWithURL(self, to, url):
        """
        إرسال ملف صوتي من URL
        
        المعاملات:
            to: معرف المستلم
            url: رابط الملف الصوتي
        
        العائد:
            نتيجة الإرسال
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendAudio(to, path)
        return self.deleteFile(path)

    @loggedIn
    def sendFile(self, to, path, file_name=''):
        """
        إرسال ملف
        
        المعاملات:
            to: معرف المستلم
            path: مسار الملف
            file_name: اسم الملف (اختياري)
        
        العائد:
            نتيجة الإرسال
        """
        if file_name == '':
            file_name = ntpath.basename(path)
        file_size = len(open(path, 'rb').read())
        objectId = self.sendMessage(to=to, text=None, contentMetadata={'FILE_NAME': str(file_name),'FILE_SIZE': str(file_size)}, contentType = 14).id
        return self.uploadObjTalk(path=path, type='file', returnAs='bool', objId=objectId)

    @loggedIn
    def sendFileWithURL(self, to, url, fileName=''):
        """
        إرسال ملف من URL
        
        المعاملات:
            to: معرف المستلم
            url: رابط الملف
            fileName: اسم الملف (اختياري)
        
        العائد:
            نتيجة الإرسال
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendFile(to, path, fileName)
        return self.deleteFile(path)

    """وظائف جهات الاتصال"""
        
    @loggedIn
    def blockContact(self, mid):
        """
        حظر جهة اتصال
        
        المعاملات:
            mid: معرف جهة الاتصال
        
        العائد:
            نتيجة الحظر
        """
        return self.talk.blockContact(0, mid)

    @loggedIn
    def unblockContact(self, mid):
        """
        إلغاء حظر جهة اتصال
        
        المعاملات:
            mid: معرف جهة الاتصال
        
        العائد:
            نتيجة إلغاء الحظر
        """
        return self.talk.unblockContact(0, mid)

    @loggedIn
    def findAndAddContactByMetaTag(self, userid, reference):
        """
        البحث وإضافة جهة اتصال بواسطة الوسم
        
        المعاملات:
            userid: معرف المستخدم
            reference: المرجع
        
        العائد:
            نتيجة الإضافة
        """
        return self.talk.findAndAddContactByMetaTag(0, userid, reference)

    @loggedIn
    def findAndAddContactsByMid(self, mid):
        """
        البحث وإضافة جهات اتصال بواسطة المعرف
        
        المعاملات:
            mid: معرف المستخدم
        
        العائد:
            نتيجة الإضافة
        """
        return self.talk.findAndAddContactsByMid(0, mid, 0, '')

    @loggedIn
    def findAndAddContactsByEmail(self, emails=[]):
        """
        البحث وإضافة جهات اتصال بواسطة البريد الإلكتروني
        
        المعاملات:
            emails: قائمة عناوين البريد الإلكتروني
        
        العائد:
            نتيجة الإضافة
        """
        return self.talk.findAndAddContactsByEmail(0, emails)

    @loggedIn
    def findAndAddContactsByUserid(self, userid):
        """
        البحث وإضافة جهات اتصال بواسطة معرف المستخدم
        
        المعاملات:
            userid: معرف المستخدم
        
        العائد:
            نتيجة الإضافة
        """
        return self.talk.findAndAddContactsByUserid(0, userid)

    @loggedIn
    def findContactsByUserid(self, userid):
        """
        البحث عن جهات اتصال بواسطة معرف المستخدم
        
        المعاملات:
            userid: معرف المستخدم
        
        العائد:
            معلومات جهة الاتصال
        """
        return self.talk.findContactByUserid(userid)

    @loggedIn
    def findContactByTicket(self, ticketId):
        """
        البحث عن جهة اتصال بواسطة التذكرة
        
        المعاملات:
            ticketId: معرف التذكرة
        
        العائد:
            معلومات جهة الاتصال
        """
        return self.talk.findContactByUserTicket(ticketId)

    @loggedIn
    def getAllContactIds(self):
        """
        الحصول على جميع معرفات جهات الاتصال
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getAllContactIds()

    @loggedIn
    def getBlockedContactIds(self):
        """
        الحصول على معرفات جهات الاتصال المحظورة
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getBlockedContactIds()

    @loggedIn
    def getContact(self, mid):
        """
        الحصول على معلومات جهة اتصال
        
        المعاملات:
            mid: معرف جهة الاتصال
        
        العائد:
            كائن جهة الاتصال
        """
        return self.talk.getContact(mid)

    @loggedIn
    def getContacts(self, midlist):
        """
        الحصول على معلومات عدة جهات اتصال
        
        المعاملات:
            midlist: قائمة المعرفات
        
        العائد:
            قائمة كائنات جهات الاتصال
        """
        return self.talk.getContacts(midlist)

    @loggedIn
    def getFavoriteMids(self):
        """
        الحصول على معرفات جهات الاتصال المفضلة
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getFavoriteMids()

    @loggedIn
    def getHiddenContactMids(self):
        """
        الحصول على معرفات جهات الاتصال المخفية
        
        العائد:
            قائمة المعرفات
        """
        return self.talk.getHiddenContactMids()

    @loggedIn
    def tryFriendRequest(self, midOrEMid, friendRequestParams, method=1):
        """
        محاولة إرسال طلب صداقة
        
        المعاملات:
            midOrEMid: معرف المستخدم
            friendRequestParams: معاملات طلب الصداقة
            method: طريقة الإرسال (افتراضي: 1)
        
        العائد:
            نتيجة الطلب
        """
        return self.talk.tryFriendRequest(midOrEMid, method, friendRequestParams)

    @loggedIn
    def makeUserAddMyselfAsContact(self, contactOwnerMid):
        """
        جعل المستخدم يضيفني كجهة اتصال
        
        المعاملات:
            contactOwnerMid: معرف مالك جهة الاتصال
        
        العائد:
            نتيجة العملية
        """
        return self.talk.makeUserAddMyselfAsContact(contactOwnerMid)

    @loggedIn
    def getContactWithFriendRequestStatus(self, id):
        """
        الحصول على جهة اتصال مع حالة طلب الصداقة
        
        المعاملات:
            id: معرف المستخدم
        
        العائد:
            معلومات جهة الاتصال وحالة الطلب
        """
        return self.talk.getContactWithFriendRequestStatus(id)

    @loggedIn
    def reissueUserTicket(self, expirationTime=100, maxUseCount=100):
        """
        إعادة إصدار تذكرة المستخدم
        
        المعاملات:
            expirationTime: وقت انتهاء الصلاحية (افتراضي: 100)
            maxUseCount: الحد الأقصى للاستخدام (افتراضي: 100)
        
        العائد:
            التذكرة الجديدة
        """
        return self.talk.reissueUserTicket(expirationTime, maxUseCount)
    
    @loggedIn
    def cloneContactProfile(self, mid):
        """
        نسخ الملف الشخصي لجهة اتصال
        
        المعاملات:
            mid: معرف جهة الاتصال
        
        العائد:
            نتيجة النسخ
        """
        contact = self.getContact(mid)
        profile = self.profile
        profile.displayName = contact.displayName
        profile.statusMessage = contact.statusMessage
        profile.pictureStatus = contact.pictureStatus
        if self.getProfileCoverId(mid) is not None:
            self.updateProfileCoverById(self.getProfileCoverId(mid))
        self.updateProfileAttribute(8, profile.pictureStatus)
        return self.updateProfile(profile)

    """وظائف المجموعات"""

    @loggedIn
    def getChatRoomAnnouncementsBulk(self, chatRoomMids):
        """
        الحصول على إعلانات عدة غرف محادثة
        
        المعاملات:
            chatRoomMids: قائمة معرفات غرف المحادثة
        
        العائد:
            قائمة الإعلانات
        """
        return self.talk.getChatRoomAnnouncementsBulk(chatRoomMids)

    @loggedIn
    def getChatRoomAnnouncements(self, chatRoomMid):
        """
        الحصول على إعلانات غرفة محادثة
        
        المعاملات:
            chatRoomMid: معرف غرفة المحادثة
        
        العائد:
            قائمة الإعلانات
        """
        return self.talk.
