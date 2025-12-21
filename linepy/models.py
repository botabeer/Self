# -*- coding: utf-8 -*-
from datetime import datetime
from .object import Object
from random import randint

import json, shutil, time, os, base64, tempfile
    
class Models(Object):
    """
    فئة النماذج التي توفر وظائف مساعدة لإدارة الملفات والمولدات
    """
        
    def __init__(self):
        """تهيئة فئة النماذج"""
        Object.__init__(self)

    """وظائف النصوص"""

    def log(self, text):
        """
        تسجيل رسالة مع الطابع الزمني
        
        المعاملات:
            text: النص المراد تسجيله
        """
        print("[%s] %s" % (str(datetime.now()), text))

    """وظائف الملفات"""

    def saveFile(self, path, raw):
        """
        حفظ ملف من البيانات الخام
        
        المعاملات:
            path: مسار الملف
            raw: البيانات الخام
        """
        with open(path, 'wb') as f:
            shutil.copyfileobj(raw, f)

    def deleteFile(self, path):
        """
        حذف ملف من المسار المحدد
        
        المعاملات:
            path: مسار الملف
        
        العائد:
            True إذا تم الحذف بنجاح، False إذا لم يكن الملف موجوداً
        """
        if os.path.exists(path):
            os.remove(path)
            return True
        else:
            return False

    def downloadFileURL(self, fileUrl, returnAs='path', saveAs='', headers=None):
        """
        تنزيل ملف من رابط URL
        
        المعاملات:
            fileUrl: رابط الملف
            returnAs: نوع الإرجاع ('path', 'bool', 'bin')
            saveAs: مسار الحفظ (اختياري)
            headers: رؤوس HTTP (اختياري)
        
        العائد:
            المسار، منطقي، أو البيانات الثنائية حسب returnAs
        """
        if returnAs not in ['path','bool','bin']:
            raise Exception('Invalid returnAs value')
        if saveAs == '':
            saveAs = self.genTempFile()
        r = self.server.getContent(fileUrl, headers=headers)
        if r.status_code != 404:
            self.saveFile(saveAs, r.raw)
            if returnAs == 'path':
                return saveAs
            elif returnAs == 'bool':
                return True
            elif returnAs == 'bin':
                return r.raw
        else:
            raise Exception('Download file failure.')

    """وظائف المولدات"""

    def genTempFile(self, returnAs='path'):
        """
        إنشاء ملف مؤقت
        
        المعاملات:
            returnAs: نوع الإرجاع ('file' أو 'path')
        
        العائد:
            اسم الملف أو مساره الكامل
        """
        try:
            if returnAs not in ['file','path']:
                raise Exception('Invalid returnAs value')
            fName, fPath = 'linepy-%s-%i.bin' % (int(time.time()), randint(0, 9)), tempfile.gettempdir()
            if returnAs == 'file':
                return fName
            elif returnAs == 'path':
                return os.path.join(fPath, fName)
        except:
            raise Exception('tempfile is required')

    def genOBSParams(self, newList, returnAs='json'):
        """
        إنشاء معاملات OBS (Object Storage)
        
        المعاملات:
            newList: القاموس الجديد للمعاملات
            returnAs: نوع الإرجاع ('json', 'b64', 'default')
        
        العائد:
            المعاملات بالصيغة المطلوبة
        """
        oldList = {'name': self.genTempFile('file'),'ver': '1.0'}
        if returnAs not in ['json','b64','default']:
            raise Exception('Invalid parameter returnAs')
        oldList.update(newList)
        if 'range' in oldList:
            new_range='bytes 0-%s\/%s' % ( str(oldList['range']-1), str(oldList['range']) )
            oldList.update({'range': new_range})
        if returnAs == 'json':
            oldList=json.dumps(oldList)
            return oldList
        elif returnAs == 'b64':
            oldList=json.dumps(oldList)
            return base64.b64encode(oldList.encode('utf-8'))
        elif returnAs == 'default':
            return oldList
