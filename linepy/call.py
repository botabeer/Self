# -*- coding: utf-8 -*-
from akad.ttypes import MediaType

def loggedIn(func):
    """
    مُزخرِف للتحقق من تسجيل الدخول قبل تنفيذ الدالة
    """
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other('يجب تسجيل الدخول إلى LINE لاستخدام هذه الوظيفة')
    return checkLogin
    
class Call(object):
    """فئة المكالمات للتعامل مع وظائف الاتصال في LINE"""
    isLogin = False

    def __init__(self):
        """تهيئة فئة المكالمات"""
        self.isLogin = True
        
    @loggedIn
    def acquireCallRoute(self, to):
        """
        الحصول على مسار المكالمة لمحادثة فردية
        
        المعاملات:
            to: معرف المستخدم المستهدف
        
        العائد:
            معلومات مسار المكالمة
        """
        return self.call.acquireCallRoute(to)
        
    @loggedIn
    def acquireGroupCallRoute(self, groupId, mediaType=MediaType.AUDIO):
        """
        الحصول على مسار المكالمة للمجموعة
        
        المعاملات:
            groupId: معرف المجموعة
            mediaType: نوع الوسائط (افتراضي: AUDIO)
        
        العائد:
            معلومات مسار المكالمة للمجموعة
        """
        return self.call.acquireGroupCallRoute(groupId, mediaType)

    @loggedIn
    def getGroupCall(self, ChatMid):
        """
        الحصول على معلومات المكالمة الجماعية
        
        المعاملات:
            ChatMid: معرف المحادثة
        
        العائد:
            معلومات المكالمة الجماعية
        """
        return self.call.getGroupCall(ChatMid)
        
    @loggedIn
    def inviteIntoGroupCall(self, chatId, contactIds=[], mediaType=MediaType.AUDIO):
        """
        دعوة جهات اتصال إلى المكالمة الجماعية
        
        المعاملات:
            chatId: معرف المحادثة
            contactIds: قائمة معرفات جهات الاتصال (افتراضي: [])
            mediaType: نوع الوسائط (افتراضي: AUDIO)
        
        العائد:
            نتيجة الدعوة
        """
        return self.call.inviteIntoGroupCall(chatId, contactIds, mediaType)
