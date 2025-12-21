# -*- coding: utf-8 -*-
from akad.ttypes import *
from random import randint

def loggedIn(func):
    """مُزخرِف للتحقق من تسجيل الدخول ودعم المربعات (Squares)"""
    def checkLogin(*args, **kwargs):
        if args[0].isSupportSquare:
            if args[0].isLogin:
                return func(*args, **kwargs)
            else:
                args[0].callback.other('You want to call the function, you must login to LINE')
        else:
            args[0].callback.other('Your LINE account is not support Square')
    return checkLogin

class Square(object):
    """
    فئة المربعات (Squares) للتعامل مع مجتمعات LINE Square
    """
    isSupportSquare = False
    isLogin = False

    def __init__(self):
        """تهيئة فئة المربعات والتحقق من الدعم"""
        self.isLogin = True
        try:
            self.isSupportSquare = True
            self.squares    = self.getJoinedSquares().squares
            self.squareObsToken = self.acquireEncryptedAccessToken(2).split('\x1e')[1]
        except:
            self.isSupportSquare = False
            self.log('Your LINE account is not support Square')

    """وظائف الكائنات - إرسال الوسائط"""

    @loggedIn
    def getJoinedSquares(self, continuationToken=None, limit=50):
        """
        الحصول على المربعات المنضم إليها
        
        المعاملات:
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = GetJoinedSquaresRequest()
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.getJoinedSquares(rq)

    @loggedIn
    def getJoinedSquareChats(self, continuationToken=None, limit=50):
        """
        الحصول على محادثات المربع المنضم إليها
        
        المعاملات:
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = GetJoinedSquareChatsRequest()
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.getJoinedSquareChats(rq)
        
    @loggedIn
    def getJoinableSquareChats(self, squareMid, continuationToken=None, limit=50):
        """
        الحصول على محادثات المربع القابلة للانضمام
        
        المعاملات:
            squareMid: معرف المربع
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = GetJoinableSquareChatsRequest()
        rq.squareMid = squareMid
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.getJoinableSquareChats(rq)
        
    @loggedIn
    def getInvitationTicketUrl(self, mid):
        """
        الحصول على رابط تذكرة الدعوة
        
        المعاملات:
            mid: معرف المربع
        """
        rq = GetInvitationTicketUrlRequest()
        rq.mid = mid
        return self.square.getInvitationTicketUrl(rq)
        
    @loggedIn
    def getSquareStatus(self, squareMid):
        """
        الحصول على حالة المربع
        
        المعاملات:
            squareMid: معرف المربع
        """
        rq = GetSquareStatusRequest()
        rq.squareMid = squareMid
        return self.square.getSquareStatus(rq)
        
    @loggedIn
    def getNoteStatus(self, squareMid):
        """
        الحصول على حالة الملاحظة
        
        المعاملات:
            squareMid: معرف المربع
        """
        rq = GetNoteStatusRequest()
        rq.squareMid = squareMid
        return self.square.getNoteStatus(rq)
        
    @loggedIn
    def searchSquares(self, query, continuationToken=None, limit=50):
        """
        البحث عن المربعات
        
        المعاملات:
            query: نص البحث
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = SearchSquaresRequest()
        rq.query = query
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.searchSquares(rq)
        
    @loggedIn
    def refreshSubscriptions(self, subscriptions=[]):
        """
        تحديث الاشتراكات
        
        المعاملات:
            subscriptions: قائمة الاشتراكات
        """
        rq = RefreshSubscriptionsRequest()
        rq.subscriptions = subscriptions
        return self.square.refreshSubscriptions(rq)
        
    @loggedIn
    def removeSubscriptions(self, unsubscriptions=[]):
        """
        إزالة الاشتراكات
        
        المعاملات:
            unsubscriptions: قائمة الاشتراكات المراد إزالتها
        """
        rq = RemoveSubscriptionsRequest()
        rq.unsubscriptions = unsubscriptions
        return self.square.removeSubscriptions(rq) sendSquareImage(self, squareChatMid, path):
        """
        إرسال صورة إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            path: مسار الصورة
        """
        return self.uploadObjSquare(squareChatMid=squareChatMid, path=path, type='image', returnAs='bool')

    @loggedIn
    def sendSquareImageWithURL(self, squareChatMid, url):
        """
        إرسال صورة من URL إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            url: رابط الصورة
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendSquareImage(squareChatMid, path)

    @loggedIn
    def sendSquareGIF(self, squareChatMid, path):
        """
        إرسال GIF إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            path: مسار ملف GIF
        """
        return self.uploadObjSquare(squareChatMid=squareChatMid, path=path, type='gif', returnAs='bool')

    @loggedIn
    def sendSquareGIFWithURL(self, squareChatMid, url):
        """
        إرسال GIF من URL إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            url: رابط GIF
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendSquareGIF(squareChatMid, path)

    @loggedIn
    def sendSquareVideo(self, squareChatMid, path):
        """
        إرسال فيديو إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            path: مسار الفيديو
        """
        return self.uploadObjSquare(squareChatMid=squareChatMid, path=path, type='video', returnAs='bool')

    @loggedIn
    def sendSquareVideoWithURL(self, squareChatMid, url):
        """
        إرسال فيديو من URL إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            url: رابط الفيديو
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendSquareVideo(squareChatMid, path)

    @loggedIn
    def sendSquareAudio(self, squareChatMid, path):
        """
        إرسال ملف صوتي إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            path: مسار الملف الصوتي
        """
        return self.uploadObjSquare(squareChatMid=squareChatMid, path=path, type='audio', returnAs='bool')

    @loggedIn
    def sendSquareAudioWithURL(self, squareChatMid, url):
        """
        إرسال ملف صوتي من URL إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            url: رابط الملف الصوتي
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendSquareAudio(squareChatMid, path)

    @loggedIn
    def sendSquareFile(self, squareChatMid, path):
        """
        إرسال ملف إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            path: مسار الملف
        """
        return self.uploadObjSquare(squareChatMid=squareChatMid, path=path, type='file', returnAs='bool')

    @loggedIn
    def sendSquareFileWithURL(self, squareChatMid, url, fileName=''):
        """
        إرسال ملف من URL إلى محادثة المربع (قيد التطوير)
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            url: رابط الملف
            fileName: اسم الملف (اختياري)
        """
        path = self.downloadFileURL(url, 'path')
        return self.sendSquareFile(squareChatMid, path, fileName)

    """وظائف الرسائل في المربع"""
        
    @loggedIn
    def sendSquareMessage(self, squareChatMid, text, contentMetadata={}, contentType=0):
        """
        إرسال رسالة إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            text: نص الرسالة
            contentMetadata: بيانات المحتوى الإضافية (افتراضي: {})
            contentType: نوع المحتوى (افتراضي: 0)
        
        العائد:
            نتيجة إرسال الرسالة
        """
        rq = SendMessageRequest()
        rq.squareChatMid = squareChatMid
        rq.squareMessage = SquareMessage()
        msg = Message()
        msg.to = squareChatMid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        rq.squareMessage.message = msg
        rq.squareMessage.fromType = 4
        if squareChatMid not in self._messageReq:
            self._messageReq[squareChatMid] = -1
        self._messageReq[squareChatMid] += 1
        rq.squareMessage.squareMessageRevision = self._messageReq[squareChatMid]
        return self.square.sendMessage(rq)

    @loggedIn
    def sendSquareSticker(self, squareChatMid, packageId, stickerId):
        """
        إرسال ملصق إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            packageId: معرف حزمة الملصقات
            stickerId: معرف الملصق
        """
        contentMetadata = {
            'STKVER': '100',
            'STKPKGID': packageId,
            'STKID': stickerId
        }
        return self.sendSquareMessage(squareChatMid, '', contentMetadata, 7)
        
    @loggedIn
    def sendSquareContact(self, squareChatMid, mid):
        """
        إرسال جهة اتصال إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            mid: معرف جهة الاتصال
        """
        contentMetadata = {'mid': mid}
        return self.sendSquareMessage(squareChatMid, '', contentMetadata, 13)

    @loggedIn
    def sendSquareGift(self, squareChatMid, productId, productType):
        """
        إرسال هدية إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            productId: معرف المنتج
            productType: نوع المنتج ('theme' أو 'sticker')
        """
        if productType not in ['theme','sticker']:
            raise Exception('Invalid productType value')
        contentMetadata = {
            'MSGTPL': str(randint(0, 10)),
            'PRDTYPE': productType.upper(),
            'STKPKGID' if productType == 'sticker' else 'PRDID': productId
        }
        return self.sendSquareMessage(squareChatMid, '', contentMetadata, 9)
        
    @loggedIn
    def destroySquareMessage(self, squareChatMid, messageId):
        """
        حذف رسالة من محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            messageId: معرف الرسالة
        """
        rq = DestroyMessageRequest()
        rq.squareChatMid = squareChatMid
        rq.messageId = messageId
        return self.square.destroyMessage(rq)

    """وظائف المربعات"""
        
    @loggedIn
    def searchSquareMembers(self, squareMid, continuationToken=None, limit=50):
        """
        البحث عن أعضاء المربع
        
        المعاملات:
            squareMid: معرف المربع
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = SearchSquareMembersRequest()
        rq.squareMid = squareMid
        rq.searchOption = SquareMemberSearchOption()
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.searchSquareMembers(rq)
        
    @loggedIn
    def findSquareByInvitationTicket(self, invitationTicket):
        """
        البحث عن مربع بواسطة تذكرة الدعوة
        
        المعاملات:
            invitationTicket: تذكرة الدعوة
        """
        rq = FindSquareByInvitationTicketRequest()
        rq.invitationTicket = invitationTicket
        return self.square.findSquareByInvitationTicket(rq)
        
    @loggedIn
    def approveSquareMembers(self, squareMid, requestedMemberMids=[]):
        """
        الموافقة على أعضاء المربع
        
        المعاملات:
            squareMid: معرف المربع
            requestedMemberMids: قائمة معرفات الأعضاء المطلوب الموافقة عليهم
        """
        rq = ApproveSquareMembersRequest()
        rq.squareMid = squareMid
        rq.requestedMemberMids = requestedMemberMids
        return self.square.approveSquareMembers(rq)
        
    @loggedIn
    def deleteSquare(self, mid):
        """
        حذف مربع
        
        المعاملات:
            mid: معرف المربع
        """
        rq = DeleteSquareRequest()
        rq.mid = mid
        rq.revision = self.revision
        return self.square.deleteSquare(rq)

    @loggedIn
    def deleteSquareChat(self, squareChatMid):
        """
        حذف محادثة من المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
        """
        rq = DeleteSquareChatRequest()
        rq.squareChatMid = squareChatMid
        rq.revision = self.revision
        return self.square.deleteSquareChat(request)
        
    @loggedIn
    def createSquare(self, name, categoryID, welcomeMessage='', profileImageObsHash='', desc='', searchable=True, type=1, ableToUseInvitationTicket=True):
        """
        إنشاء مربع جديد
        
        المعاملات:
            name: اسم المربع
            categoryID: معرف الفئة
            welcomeMessage: رسالة الترحيب (اختياري)
            profileImageObsHash: hash صورة الملف الشخصي (اختياري)
            desc: الوصف (اختياري)
            searchable: قابل للبحث (افتراضي: True)
            type: نوع المربع (افتراضي: 1)
            ableToUseInvitationTicket: إمكانية استخدام تذكرة الدعوة (افتراضي: True)
        """
        rq = CreateSquareRequest()
        rq.square = Square()
        rq.square.name = name
        rq.square.categoryID = categoryID
        rq.square.welcomeMessage = welcomeMessage
        rq.square.profileImageObsHash = profileImageObsHash
        rq.square.desc = desc
        rq.square.searchable = searchable
        rq.square.type = type
        rq.square.ableToUseInvitationTicket = ableToUseInvitationTicket
        rq.creator = SquareMember()
        return self.square.createSquare(rq)
        
    @loggedIn
    def createSquareChat(self, squareMid, name, squareMemberMids):
        """
        إنشاء محادثة جديدة في المربع
        
        المعاملات:
            squareMid: معرف المربع
            name: اسم المحادثة
            squareMemberMids: قائمة معرفات الأعضاء
        """
        rq = CreateSquareChatRequest()
        rq.reqSeq = self.revision
        rq.squareChat = SquareChat()
        rq.squareChat.squareMid = squareMid
        rq.squareChat.name = name
        rq.squareMemberMids = squareMemberMids
        return self.square.createSquareChat(request)
        
    @loggedIn
    def fetchSquareChatEvents(self, squareChatMid, subscriptionId=0, syncToken='', limit=50, direction=2):
        """
        جلب أحداث محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            subscriptionId: معرف الاشتراك (افتراضي: 0)
            syncToken: رمز المزامنة (افتراضي: '')
            limit: الحد الأقصى للأحداث (افتراضي: 50)
            direction: اتجاه الجلب (افتراضي: 2)
        """
        rq = FetchSquareChatEventsRequest()
        rq.squareChatMid = squareChatMid
        rq.subscriptionId = subscriptionId
        rq.syncToken = syncToken
        rq.limit = limit
        rq.direction = direction
        return self.square.fetchSquareChatEvents(rq)
        
    @loggedIn
    def fetchMyEvents(self, subscriptionId=0, syncToken='', continuationToken=None, limit=50):
        """
        جلب الأحداث الخاصة بي
        
        المعاملات:
            subscriptionId: معرف الاشتراك (افتراضي: 0)
            syncToken: رمز المزامنة (افتراضي: '')
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للأحداث (افتراضي: 50)
        """
        rq = FetchMyEventsRequest()
        rq.subscriptionId = subscriptionId
        rq.syncToken = syncToken
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.fetchMyEvents(rq)
        
    @loggedIn
    def markAsRead(self, squareChatMid, messageId):
        """
        تعليم الرسالة كمقروءة
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            messageId: معرف الرسالة
        """
        rq = MarkAsReadRequest()
        rq.squareChatMid = squareChatMid
        rq.messageId = messageId
        return self.square.markAsRead(rq)
        
    @loggedIn
    def getSquareAuthority(self, squareMid):
        """
        الحصول على صلاحيات المربع
        
        المعاملات:
            squareMid: معرف المربع
        """
        rq = GetSquareAuthorityRequest()
        rq.squareMid = squareMid
        return self.square.getSquareAuthority(rq)

    @loggedIn
    def leaveSquare(self, squareMid):
        """
        مغادرة مربع
        
        المعاملات:
            squareMid: معرف المربع
        """
        rq = LeaveSquareRequest()
        rq.squareMid = squareMid
        return self.square.leaveSquare(rq)

    @loggedIn
    def leaveSquareChat(self, squareChatMid, squareChatMemberRevision, sayGoodbye=True):
        """
        مغادرة محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            squareChatMemberRevision: رقم مراجعة عضوية المحادثة
            sayGoodbye: إرسال رسالة وداع (افتراضي: True)
        """
        rq = LeaveSquareChatRequest()
        rq.squareChatMid = squareChatMid
        rq.sayGoodbye = sayGoodbye
        rq.squareChatMemberRevision = squareChatMemberRevision
        return self.square.leaveSquareChat(rq)
        
    @loggedIn
    def joinSquareChat(self, squareChatMid):
        """
        الانضمام إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
        """
        rq = JoinSquareChatRequest()
        rq.squareChatMid = squareChatMid
        return self.square.joinSquareChat(rq)
        
    @loggedIn
    def joinSquare(self, squareMid, displayName, profileImageObsHash):
        """
        الانضمام إلى مربع
        
        المعاملات:
            squareMid: معرف المربع
            displayName: الاسم المعروض
            profileImageObsHash: hash صورة الملف الشخصي
        """
        rq = JoinSquareRequest()
        rq.squareMid = squareMid
        rq.member = SquareMember()
        rq.member.squareMid = squareMid
        rq.member.displayName = displayName
        rq.member.profileImageObsHash = profileImageObsHash
        return self.square.joinSquare(rq)
        
    @loggedIn
    def inviteToSquare(self, squareMid, squareChatMid, invitees=[]):
        """
        دعوة أشخاص إلى المربع
        
        المعاملات:
            squareMid: معرف المربع
            squareChatMid: معرف محادثة المربع
            invitees: قائمة المدعوين
        """
        rq = InviteToSquareRequest()
        rq.squareMid = squareMid
        rq.invitees = invitees
        rq.squareChatMid = squareChatMid
        return self.square.inviteToSquare(rq)
        
    @loggedIn
    def inviteToSquareChat(self, squareChatMid, inviteeMids=[]):
        """
        دعوة أشخاص إلى محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            inviteeMids: قائمة معرفات المدعوين
        """
        rq = InviteToSquareChatRequest()
        rq.inviteeMids = inviteeMids
        rq.squareChatMid = squareChatMid
        return self.square.inviteToSquareChat(rq)
        
    @loggedIn
    def getSquareMember(self, squareMemberMid):
        """
        الحصول على معلومات عضو المربع
        
        المعاملات:
            squareMemberMid: معرف عضو المربع
        """
        rq = GetSquareMemberRequest()
        rq.squareMemberMid = squareMemberMid
        return self.square.getSquareMember(rq)
        
    @loggedIn
    def getSquareMembers(self, mids=[]):
        """
        الحصول على معلومات أعضاء المربع
        
        المعاملات:
            mids: قائمة المعرفات
        """
        rq = GetSquareMembersRequest()
        rq.mids = mids
        return self.square.getSquareMembers(rq)
        
    @loggedIn
    def getSquareMemberRelation(self, squareMid, targetSquareMemberMid):
        """
        الحصول على علاقة عضو المربع
        
        المعاملات:
            squareMid: معرف المربع
            targetSquareMemberMid: معرف العضو المستهدف
        """
        rq = GetSquareMemberRelationRequest()
        rq.squareMid = squareMid
        rq.targetSquareMemberMid = targetSquareMemberMid
        return self.square.getSquareMemberRelation(rq)
        
    @loggedIn
    def getSquareMemberRelations(self, state=1, continuationToken=None, limit=50):
        """
        الحصول على علاقات أعضاء المربع
        
        المعاملات:
            state: الحالة (1 لا شيء، 2 محظور) (افتراضي: 1)
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = GetSquareMemberRelationsRequest()
        rq.state = state  # 1 NONE, 2 BLOCKED
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.getSquareMemberRelations(rq)
        
    @loggedIn
    def getSquareChatMembers(self, squareChatMid, continuationToken=None, limit=50):
        """
        الحصول على أعضاء محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            continuationToken: رمز المتابعة (اختياري)
            limit: الحد الأقصى للنتائج (افتراضي: 50)
        """
        rq = GetSquareChatMembersRequest()
        rq.squareChatMid = squareChatMid
        rq.continuationToken = continuationToken
        rq.limit = limit
        return self.square.getSquareChatMembers(rq)
        
    @loggedIn
    def getSquareChatStatus(self, squareChatMid):
        """
        الحصول على حالة محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
        """
        rq = GetSquareChatStatusRequest()
        rq.squareChatMid = squareChatMid
        return self.square.getSquareChatStatus(rq)
        
    @loggedIn
    def getSquareChat(self, squareChatMid):
        """
        الحصول على معلومات محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
        """
        rq = GetSquareChatRequest()
        rq.squareChatMid = squareChatMid
        return self.square.getSquareChat(rq)
        
    @loggedIn
    def getSquare(self, mid):
        """
        الحصول على معلومات المربع
        
        المعاملات:
            mid: معرف المربع
        """
        rq = GetSquareRequest()
        rq.mid = mid
        return self.square.getSquare(rq)
        
    @loggedIn
    def getSquareChatAnnouncements(self, squareChatMid):
        """
        الحصول على إعلانات محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
        """
        rq = GetSquareChatAnnouncementsRequest()
        rq.squareChatMid = squareChatMid
        return self.square.getSquareChatAnnouncements(rq)
        
    @loggedIn
    def deleteSquareChatAnnouncement(self, squareChatMid, announcementSeq):
        """
        حذف إعلان من محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            announcementSeq: تسلسل الإعلان
        """
        rq = DeleteSquareChatAnnouncementRequest()
        rq.squareChatMid = squareChatMid
        rq.squareChatMid = announcementSeq
        return self.square.deleteSquareChatAnnouncement(rq)
        
    @loggedIn
    def createSquareChatAnnouncement(self, squareChatMid, text, messageId='', senderSquareMemberMid=''):
        """
        إنشاء إعلان في محادثة المربع
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            text: نص الإعلان
            messageId: معرف الرسالة (اختياري)
            senderSquareMemberMid: معرف المرسل (اختياري)
        """
        rq = CreateSquareChatAnnouncementRequest()
        rq.reqSeq = 0
        rq.squareChatMid = squareChatMid
        rq.squareChatAnnouncement = SquareChatAnnouncement()
        rq.squareChatAnnouncement.announcementSeq = 0
        rq.squareChatAnnouncement.type = 0
        rq.squareChatAnnouncement.contents = SquareChatAnnouncementContents()
        rq.squareChatAnnouncement.contents.textMessageAnnouncementContents = TextMessageAnnouncementContents()
        rq.squareChatAnnouncement.contents.textMessageAnnouncementContents.messageId = messageId
        rq.squareChatAnnouncement.contents.textMessageAnnouncementContents.text = text
        rq.squareChatAnnouncement.contents.textMessageAnnouncementContents.senderSquareMemberMid = senderSquareMemberMid
        return self.square.createSquareChatAnnouncement(rq)

    @loggedIn
    def
