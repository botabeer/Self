# -*- coding: utf-8 -*-
class Callback(object):
    """فئة الاستدعاءات للتعامل مع رسائل المصادقة"""

    def __init__(self, callback):
        """
        تهيئة فئة الاستدعاءات
        
        المعاملات:
            callback: دالة الاستدعاء المخصصة
        """
        self.callback = callback

    def PinVerified(self, pin):
        """
        عرض رسالة التحقق من رمز PIN
        
        المعاملات:
            pin: رمز PIN المطلوب إدخاله
        """
        self.callback("أدخل رمز PIN هذا '" + pin + "' في تطبيق LINE على هاتفك خلال دقيقتين")

    def QrUrl(self, url, showQr=True):
        """
        عرض رابط رمز QR مع خيار عرض الرمز
        
        المعاملات:
            url: رابط رمز QR
            showQr: عرض رمز QR (افتراضي: True)
        """
        if showQr:
            notice='أو امسح رمز QR هذا '
        else:
            notice=''
        self.callback('افتح هذا الرابط ' + notice + 'في تطبيق LINE على هاتفك خلال دقيقتين\n' + url)
        if showQr:
            try:
                import pyqrcode
                url = pyqrcode.create(url)
                self.callback(url.terminal('green', 'white', 1))
            except:
                pass

    def default(self, str):
        """
        دالة الاستدعاء الافتراضية
        
        المعاملات:
            str: النص المراد عرضه
        """
        self.callback(str)
