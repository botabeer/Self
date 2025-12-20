# -*- coding: utf-8 -*-
class Callback(object):

    def __init__(self, callback):
        self.callback = callback

    def PinVerified(self, pin):
        self.callback("أدخل رمز PIN هذا '" + pin + "' في تطبيق LINE على هاتفك خلال دقيقتين")

    def QrUrl(self, url, showQr=True):
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
        self.callback(str)
