# -*- coding: utf-8 -*-
from .config import Config
import json, requests, urllib

class Server(Config):
    """
    فئة الخادم للتعامل مع طلبات HTTP وإدارة الرؤوس
    """
    _session        = requests.session()
    timelineHeaders = {}
    Headers         = {}

    def __init__(self):
        """تهيئة الخادم والرؤوس"""
        self.Headers = {}
        self.channelHeaders = {}
        Config.__init__(self)

    def parseUrl(self, path):
        """
        تحليل المسار وإرجاع URL الكامل
        
        المعاملات:
            path: المسار النسبي
        
        العائد:
            URL الكامل
        """
        return self.LINE_HOST_DOMAIN + path

    def urlEncode(self, url, path, params=[]):
        """
        ترميز URL مع المعاملات
        
        المعاملات:
            url: الرابط الأساسي
            path: المسار
            params: قائمة المعاملات
        
        العائد:
            URL المرمز بالكامل
        """
        return url + path + '?' + urllib.parse.urlencode(params)

    def getJson(self, url, allowHeader=False):
        """
        جلب محتوى JSON من URL
        
        المعاملات:
            url: الرابط المستهدف
            allowHeader: السماح باستخدام الرؤوس (افتراضي: False)
        
        العائد:
            البيانات بصيغة JSON
        """
        if allowHeader is False:
            return json.loads(self._session.get(url).text)
        else:
            return json.loads(self._session.get(url, headers=self.Headers).text)

    def setHeadersWithDict(self, headersDict):
        """
        تعيين الرؤوس من قاموس
        
        المعاملات:
            headersDict: قاموس الرؤوس
        """
        self.Headers.update(headersDict)

    def setHeaders(self, argument, value):
        """
        تعيين رأس محدد
        
        المعاملات:
            argument: مفتاح الرأس
            value: قيمة الرأس
        """
        self.Headers[argument] = value

    def setTimelineHeadersWithDict(self, headersDict):
        """
        تعيين رؤوس الجدول الزمني من قاموس
        
        المعاملات:
            headersDict: قاموس الرؤوس
        """
        self.timelineHeaders.update(headersDict)

    def setTimelineHeaders(self, argument, value):
        """
        تعيين رأس محدد للجدول الزمني
        
        المعاملات:
            argument: مفتاح الرأس
            value: قيمة الرأس
        """
        self.timelineHeaders[argument] = value

    def additionalHeaders(self, source, newSource):
        """
        دمج رؤوس إضافية
        
        المعاملات:
            source: الرؤوس الأصلية
            newSource: الرؤوس الجديدة
        
        العائد:
            قاموس الرؤوس المدمجة
        """
        headerList={}
        headerList.update(source)
        headerList.update(newSource)
        return headerList

    def optionsContent(self, url, data=None, headers=None):
        """
        إرسال طلب OPTIONS
        
        المعاملات:
            url: الرابط المستهدف
            data: البيانات (اختياري)
            headers: الرؤوس (اختياري)
        
        العائد:
            كائن الاستجابة
        """
        if headers is None:
            headers=self.Headers
        return self._session.options(url, headers=headers, data=data)

    def postContent(self, url, data=None, files=None, headers=None):
        """
        إرسال طلب POST
        
        المعاملات:
            url: الرابط المستهدف
            data: البيانات (اختياري)
            files: الملفات (اختياري)
            headers: الرؤوس (اختياري)
        
        العائد:
            كائن الاستجابة
        """
        if headers is None:
            headers=self.Headers
        return self._session.post(url, headers=headers, data=data, files=files)

    def getContent(self, url, headers=None):
        """
        إرسال طلب GET
        
        المعاملات:
            url: الرابط المستهدف
            headers: الرؤوس (اختياري)
        
        العائد:
            كائن الاستجابة مع دفق البيانات
        """
        if headers is None:
            headers=self.Headers
        return self._session.get(url, headers=headers, stream=True)

    def deleteContent(self, url, data=None, headers=None):
        """
        إرسال طلب DELETE
        
        المعاملات:
            url: الرابط المستهدف
            data: البيانات (اختياري)
            headers: الرؤوس (اختياري)
        
        العائد:
            كائن الاستجابة
        """
        if headers is None:
            headers=self.Headers
        return self._session.delete(url, headers=headers, data=data)

    def putContent(self, url, data=None, headers=None):
        """
        إرسال طلب PUT
        
        المعاملات:
            url: الرابط المستهدف
            data: البيانات (اختياري)
            headers: الرؤوس (اختياري)
        
        العائد:
            كائن الاستجابة
        """
        if headers is None:
            headers=self.Headers
        return self._session.put(url, headers=headers, data=data)
