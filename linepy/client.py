# -*- coding: utf-8 -*-
from akad.ttypes import Message
from .auth import Auth
from .models import Models
from .talk import Talk
from .square import Square
from .call import Call
from .timeline import Timeline

class LINE(Auth, Models, Talk, Square, Call, Timeline):
    """
    الفئة الرئيسية لمكتبة LINE Python
    تجمع جميع الوظائف من المصادقة، النماذج، المحادثة، المربعات، المكالمات، والجدول الزمني
    """

    def __init__(self, idOrAuthToken=None, passwd=None, certificate=None, systemName=None, appName=None, showQr=False, keepLoggedIn=True):
        """
        تهيئة عميل LINE
        
        المعاملات:
            idOrAuthToken: البريد الإلكتروني/معرف المستخدم أو رمز المصادقة
            passwd: كلمة المرور (اختياري إذا تم استخدام رمز المصادقة)
            certificate: الشهادة (اختياري)
            systemName: اسم النظام (اختياري)
            appName: اسم التطبيق (اختياري)
            showQr: عرض رمز QR (افتراضي: False)
            keepLoggedIn: الحفاظ على تسجيل الدخول (افتراضي: True)
        """
        
        Auth.__init__(self)
        # تسجيل الدخول باستخدام رمز QR إذا لم يتم تقديم بيانات الاعتماد
        if not (idOrAuthToken or idOrAuthToken and passwd):
            self.loginWithQrCode(keepLoggedIn=keepLoggedIn, systemName=systemName, appName=appName, showQr=showQr)
        # تسجيل الدخول باستخدام الهوية وكلمة المرور
        if idOrAuthToken and passwd:
            self.loginWithCredential(_id=idOrAuthToken, passwd=passwd, certificate=certificate, systemName=systemName, appName=appName, keepLoggedIn=keepLoggedIn)
        # تسجيل الدخول باستخدام رمز المصادقة فقط
        elif idOrAuthToken and not passwd:
            self.loginWithAuthToken(authToken=idOrAuthToken, appName=appName)

        self.__initAll()

    def __initAll(self):
        """
        تهيئة جميع الوحدات بعد تسجيل الدخول بنجاح
        يحمل الملف الشخصي والمجموعات ويهيئ جميع الفئات
        """

        self.profile    = self.talk.getProfile()
        self.groups     = self.talk.getGroupIdsJoined()

        Models.__init__(self)
        Talk.__init__(self)
        Square.__init__(self)
        Call.__init__(self)
        Timeline.__init__(self)
