# -*- coding: utf-8 -*-

def loggedIn(func):
    """مُزخرِف للتحقق من تسجيل الدخول قبل تنفيذ الدالة"""
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other('You want to call the function, you must login to LINE')
    return checkLogin

class Channel(object):
    """فئة القناة للتعامل مع قنوات LINE"""
    isLogin = False
    channelId     = None
    channelResult = None

    def __init__(self, client, channelId, showSuccess=True):
        """
        تهيئة القناة
        
        المعاملات:
            client: عميل LINE
            channelId: معرف القناة
            showSuccess: عرض رسالة النجاح (افتراضي: True)
        """
        self.client = client
        self.channelId = channelId
        self.showSuccess = showSuccess
        self.__loginChannel()

    def __logChannel(self, text):
        """
        تسجيل رسالة تسجيل الدخول إلى القناة
        
        المعاملات:
            text: اسم القناة
        """
        self.client.log('[%s] : Success login to %s' % (self.client.profile.displayName, text))

    def __loginChannel(self):
        """تسجيل الدخول إلى القناة وإنشاء الجلسة"""
        self.isLogin = True
        self.channelResult  = self.approveChannelAndIssueChannelToken(self.channelId)
        self.__createChannelSession()

    @loggedIn
    def getChannelResult(self):
        """
        الحصول على نتيجة القناة
        
        العائد:
            نتيجة تسجيل الدخول إلى القناة
        """
        return self.channelResult

    def __createChannelSession(self):
        """إنشاء جلسة القناة وعرض رسالة النجاح"""
        channelInfo = self.getChannelInfo(self.channelId)
        if self.showSuccess:
            self.__logChannel(channelInfo.name)

    @loggedIn
    def approveChannelAndIssueChannelToken(self, channelId):
        """
        الموافقة على القناة وإصدار رمز القناة
        
        المعاملات:
            channelId: معرف القناة
        
        العائد:
            رمز القناة المُصدَر
        """
        return self.client.approveChannelAndIssueChannelToken(channelId)

    @loggedIn
    def issueChannelToken(self, channelId):
        """
        إصدار رمز القناة
        
        المعاملات:
            channelId: معرف القناة
        
        العائد:
            رمز القناة المُصدَر
        """
        return self.client.issueChannelToken(channelId)

    @loggedIn
    def getChannelInfo(self, channelId, locale='EN'):
        """
        الحصول على معلومات القناة
        
        المعاملات:
            channelId: معرف القناة
            locale: اللغة (افتراضي: 'EN')
        
        العائد:
            معلومات القناة
        """
        return self.client.getChannelInfo(channelId, locale)

    @loggedIn
    def revokeChannel(self, channelId):
        """
        إلغاء صلاحيات القناة
        
        المعاملات:
            channelId: معرف القناة
        
        العائد:
            نتيجة الإلغاء
        """
        return self.client.revokeChannel(channelId)
