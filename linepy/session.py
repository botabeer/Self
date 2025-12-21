# -*- coding: utf-8 -*-
from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol
from akad import AuthService, TalkService, ChannelService, CallService, SquareService

class Session:
    """
    فئة الجلسة لإنشاء اتصالات Thrift مع خدمات LINE المختلفة
    """

    def __init__(self, url, headers, path=''):
        """
        تهيئة الجلسة
        
        المعاملات:
            url: رابط الخادم
            headers: رؤوس الطلب
            path: المسار الإضافي (اختياري)
        """
        self.host = url + path
        self.headers = headers

    def Auth(self, isopen=True):
        """
        إنشاء جلسة المصادقة
        
        المعاملات:
            isopen: فتح الاتصال تلقائياً (افتراضي: True)
        
        العائد:
            عميل خدمة المصادقة
        """
        self.transport = THttpClient.THttpClient(self.host)
        self.transport.setCustomHeaders(self.headers)
        
        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self._auth  = AuthService.Client(self.protocol)
        
        if isopen:
            self.transport.open()

        return self._auth

    def Talk(self, isopen=True):
        """
        إنشاء جلسة المحادثة
        
        المعاملات:
            isopen: فتح الاتصال تلقائياً (افتراضي: True)
        
        العائد:
            عميل خدمة المحادثة
        """
        self.transport = THttpClient.THttpClient(self.host)
        self.transport.setCustomHeaders(self.headers)
        
        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self._talk  = TalkService.Client(self.protocol)
        
        if isopen:
            self.transport.open()

        return self._talk

    def Channel(self, isopen=True):
        """
        إنشاء جلسة القناة
        
        المعاملات:
            isopen: فتح الاتصال تلقائياً (افتراضي: True)
        
        العائد:
            عميل خدمة القناة
        """
        self.transport = THttpClient.THttpClient(self.host)
        self.transport.setCustomHeaders(self.headers)

        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self._channel  = ChannelService.Client(self.protocol)
        
        if isopen:
            self.transport.open()

        return self._channel

    def Call(self, isopen=True):
        """
        إنشاء جلسة المكالمة
        
        المعاملات:
            isopen: فتح الاتصال تلقائياً (افتراضي: True)
        
        العائد:
            عميل خدمة المكالمة
        """
        self.transport = THttpClient.THttpClient(self.host)
        self.transport.setCustomHeaders(self.headers)

        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self._call  = CallService.Client(self.protocol)
        
        if isopen:
            self.transport.open()

        return self._call

    def Square(self, isopen=True):
        """
        إنشاء جلسة المربع (Square)
        
        المعاملات:
            isopen: فتح الاتصال تلقائياً (افتراضي: True)
        
        العائد:
            عميل خدمة المربع
        """
        self.transport = THttpClient.THttpClient(self.host)
        self.transport.setCustomHeaders(self.headers)

        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self._square  = SquareService.Client(self.protocol)
        
        if isopen:
            self.transport.open()

        return self._square
