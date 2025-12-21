# -*- coding: utf-8 -*-
from datetime import datetime
from .channel import Channel

import json, time, base64

def loggedIn(func):
    """مُزخرِف للتحقق من تسجيل الدخول قبل تنفيذ الدالة"""
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            args[0].callback.other('You want to call the function, you must login to LINE')
    return checkLogin
    
class Timeline(Channel):
    """
    فئة الجدول الزمني للتعامل مع المنشورات والألبومات في LINE
    """

    def __init__(self):
        """تهيئة فئة الجدول الزمني"""
        Channel.__init__(self, self.channel, self.server.CHANNEL_ID['LINE_TIMELINE'], False)
        self.tl = self.getChannelResult()
        self.__loginTimeline()
        
    def __loginTimeline(self):
        """إعداد رؤوس الجدول الزمني بعد تسجيل الدخول"""
        self.server.setTimelineHeadersWithDict({
            'Content-Type': 'application/json',
            'User-Agent': self.server.USER_AGENT,
            'X-Line-Mid': self.profile.mid,
            'X-Line-Carrier': self.server.CARRIER,
            'X-Line-Application': self.server.APP_NAME,
            'X-Line-ChannelToken': self.tl.channelAccessToken
        })
        self.profileDetail = self.getProfileDetail()

    """وظائف الجدول الزمني"""

    @loggedIn
    def getFeed(self, postLimit=10, commentLimit=1, likeLimit=1, order='TIME'):
        """
        الحصول على آخر المنشورات في الصفحة الرئيسية
        
        المعاملات:
            postLimit: الحد الأقصى للمنشورات (افتراضي: 10)
            commentLimit: الحد الأقصى للتعليقات (افتراضي: 1)
            likeLimit: الحد الأقصى للإعجابات (افتراضي: 1)
            order: ترتيب المنشورات (افتراضي: 'TIME')
        
        العائد:
            قائمة المنشورات
        """
        params = {'postLimit': postLimit, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'order': order}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v27/feed/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getHomeProfile(self, mid=None, postLimit=10, commentLimit=1, likeLimit=1):
        """
        الحصول على منشورات الصفحة الشخصية
        
        المعاملات:
            mid: معرف المستخدم (افتراضي: المستخدم الحالي)
            postLimit: الحد الأقصى للمنشورات (افتراضي: 10)
            commentLimit: الحد الأقصى للتعليقات (افتراضي: 1)
            likeLimit: الحد الأقصى للإعجابات (افتراضي: 1)
        
        العائد:
            قائمة منشورات الصفحة الشخصية
        """
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'postLimit': postLimit, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'LINE_PROFILE_COVER'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v27/post/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getProfileDetail(self, mid=None):
        """
        الحصول على تفاصيل الملف الشخصي
        
        المعاملات:
            mid: معرف المستخدم (افتراضي: المستخدم الحالي)
        
        العائد:
            تفاصيل الملف الشخصي
        """
        if mid is None:
            mid = self.profile.mid
        params = {'userMid': mid}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v1/userpopup/getDetail.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def updateProfileCoverById(self, objId):
        """
        تحديث صورة الغلاف بواسطة معرف الكائن
        
        المعاملات:
            objId: معرف الكائن
        
        العائد:
            نتيجة التحديث
        """
        params = {'coverImageId': objId}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v39/home/updateCover.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def getProfileCoverId(self, mid=None):
        """
        الحصول على معرف صورة الغلاف
        
        المعاملات:
            mid: معرف المستخدم (افتراضي: المستخدم الحالي)
        
        العائد:
            معرف صورة الغلاف
        """
        if mid is None:
            mid = self.profile.mid
        home = self.getProfileDetail(mid)
        return home['result']['objectId']

    @loggedIn
    def getProfileCoverURL(self, mid=None):
        """
        الحصول على رابط صورة الغلاف
        
        المعاملات:
            mid: معرف المستخدم (افتراضي: المستخدم الحالي)
        
        العائد:
            رابط صورة الغلاف
        """
        if mid is None:
            mid = self.profile.mid
        home = self.getProfileDetail(mid)
        params = {'userid': mid, 'oid': home['result']['objectId']}
        return self.server.urlEncode(self.server.LINE_OBS_DOMAIN, '/myhome/c/download.nhn', params)

    """وظائف المنشورات"""

    @loggedIn
    def createPost(self, text, holdingTime=None):
        """
        إنشاء منشور جديد
        
        المعاملات:
            text: نص المنشور
            holdingTime: وقت النشر المؤجل (اختياري)
        
        العائد:
            نتيجة الإنشاء
        """
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/post/create.json', params)
        payload = {'postInfo': {'readPermission': {'type': 'ALL'}}, 'sourceType': 'TIMELINE', 'contents': {'text': text}}
        if holdingTime != None:
            payload["postInfo"]["holdingTime"] = holdingTime
        data = json.dumps(payload)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def sendPostToTalk(self, mid, postId):
        """
        إرسال منشور إلى محادثة
        
        المعاملات:
            mid: معرف المستلم
            postId: معرف المنشور
        
        العائد:
            نتيجة الإرسال
        """
        if mid is None:
            mid = self.profile.mid
        params = {'receiveMid': mid, 'postId': postId}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/post/sendPostToTalk.json', params)
        r = self.server.getContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def createComment(self, mid, postId, text):
        """
        إنشاء تعليق على منشور
        
        المعاملات:
            mid: معرف المستخدم
            postId: معرف المنشور
            text: نص التعليق
        
        العائد:
            نتيجة الإنشاء
        """
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/comment/create.json', params)
        data = {'commentText': text, 'activityExternalId': postId, 'actorId': mid}
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def deleteComment(self, mid, postId, commentId):
        """
        حذف تعليق من منشور
        
        المعاملات:
            mid: معرف المستخدم
            postId: معرف المنشور
            commentId: معرف التعليق
        
        العائد:
            نتيجة الحذف
        """
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/comment/delete.json', params)
        data = {'commentId': commentId, 'activityExternalId': postId, 'actorId': mid}
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def likePost(self, mid, postId, likeType=1001):
        """
        الإعجاب بمنشور
        
        المعاملات:
            mid: معرف المستخدم
            postId: معرف المنشور
            likeType: نوع الإعجاب (1001-1006) (افتراضي: 1001)
        
        العائد:
            نتيجة الإعجاب
        """
        if mid is None:
            mid = self.profile.mid
        if likeType not in [1001,1002,1003,1004,1005,1006]:
            raise Exception('Invalid parameter likeType')
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/like/create.json', params)
        data = {'likeType': likeType, 'activityExternalId': postId, 'actorId': mid}
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def unlikePost(self, mid, postId):
        """
        إلغاء الإعجاب بمنشور
        
        المعاملات:
            mid: معرف المستخدم
            postId: معرف المنشور
        
        العائد:
            نتيجة الإلغاء
        """
        if mid is None:
            mid = self.profile.mid
        params = {'homeId': mid, 'sourceType': 'TIMELINE'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v33/like/cancel.json', params)
        data = {'activityExternalId': postId, 'actorId': mid}
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        return r.json()

    """وظائف منشورات المجموعة"""

    @loggedIn
    def createGroupPost(self, mid, text):
        """
        إنشاء منشور في مجموعة
        
        المعاملات:
            mid: معرف المجموعة
            text: نص المنشور
        
        العائد:
            نتيجة الإنشاء
        """
        payload = {'postInfo': {'readPermission': {'homeId': mid}}, 'sourceType': 'TIMELINE', 'contents': {'text': text}}
        data = json.dumps(payload)
        r = self.server.postContent(self.server.LINE_TIMELINE_API + '/v27/post/create.json', data=data, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def createGroupAlbum(self, mid, name):
        """
        إنشاء ألبوم في مجموعة
        
        المعاملات:
            mid: معرف المجموعة
            name: اسم الألبوم
        
        العائد:
            True عند النجاح
        """
        data = json.dumps({'title': name, 'type': 'image'})
        params = {'homeId': mid,'count': '1','auto': '0'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_MH, '/album/v3/album.json', params)
        r = self.server.postContent(url, data=data, headers=self.server.timelineHeaders)
        if r.status_code != 201:
            raise Exception('Create a new album failure.')
        return True

    @loggedIn
    def deleteGroupAlbum(self, mid, albumId):
        """
        حذف ألبوم من مجموعة
        
        المعاملات:
            mid: معرف المجموعة
            albumId: معرف الألبوم
        
        العائد:
            True عند النجاح
        """
        params = {'homeId': mid}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_MH, '/album/v3/album/%s' % albumId, params)
        r = self.server.deleteContent(url, headers=self.server.timelineHeaders)
        if r.status_code != 201:
            raise Exception('Delete album failure.')
        return True
    
    @loggedIn
    def getGroupPost(self, mid, postLimit=10, commentLimit=1, likeLimit=1):
        """
        الحصول على منشورات مجموعة
        
        المعاملات:
            mid: معرف المجموعة
            postLimit: الحد الأقصى للمنشورات (افتراضي: 10)
            commentLimit: الحد الأقصى للتعليقات (افتراضي: 1)
            likeLimit: الحد الأقصى للإعجابات (افتراضي: 1)
        
        العائد:
            قائمة المنشورات
        """
        params = {'homeId': mid, 'commentLimit': commentLimit, 'likeLimit': likeLimit, 'sourceType': 'TALKROOM'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_API, '/v27/post/list.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    """وظائف ألبومات المجموعة"""

    @loggedIn
    def getGroupAlbum(self, mid):
        """
        الحصول على ألبومات المجموعة
        
        المعاملات:
            mid: معرف المجموعة
        
        العائد:
            قائمة الألبومات
        """
        params = {'homeId': mid, 'type': 'g', 'sourceType': 'TALKROOM'}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_MH, '/album/v3/albums.json', params)
        r = self.server.getContent(url, headers=self.server.timelineHeaders)
        return r.json()

    @loggedIn
    def changeGroupAlbumName(self, mid, albumId, name):
        """
        تغيير اسم ألبوم المجموعة
        
        المعاملات:
            mid: معرف المجموعة
            albumId: معرف الألبوم
            name: الاسم الجديد
        
        العائد:
            True عند النجاح
        """
        data = json.dumps({'title': name})
        params = {'homeId': mid}
        url = self.server.urlEncode(self.server.LINE_TIMELINE_MH, '/album/v3/album/%s' % albumId, params)
        r = self.server.putContent(url, data=data, headers=self.server.timelineHeaders)
        if r.status_code != 201:
            raise Exception('Change album name failure.')
        return True

    @loggedIn
    def addImageToAlbum(self, mid, albumId, path):
        """
        إضافة صورة إلى ألبوم
        
        المعاملات:
            mid: معرف المجموعة
            albumId: معرف الألبوم
            path: مسار الصورة
        
        العائد:
            نتيجة الإضافة
        """
        file = open(path, 'rb').read()
        params = {
            'oid': int(time.time()),
            'quality': '90',
            'range': len(file),
            'type': 'image'
        }
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': 'image/jpeg',
            'X-Line-Mid': mid,
            'X-Line-Album': albumId,
            'x-obs-params': self.genOBSParams(params,'b64')
        })
        r = self.server.getContent(self.server.LINE_OBS_DOMAIN + '/album/a/upload.nhn', data=file, headers=hr)
        if r.status_code != 201:
            raise Exception('Add image to album failure.')
        return r.json()

    @loggedIn
    def getImageGroupAlbum(self, mid, albumId, objId, returnAs='path', saveAs=''):
        """
        الحصول على صورة من ألبوم المجموعة
        
        المعاملات:
            mid: معرف المجموعة
            albumId: معرف الألبوم
            objId: معرف الكائن
            returnAs: نوع الإرجاع ('path', 'bool', 'bin') (افتراضي: 'path')
            saveAs: مسار الحفظ (اختياري)
        
        العائد:
            المسار، منطقي، أو البيانات الثنائية حسب returnAs
        """
        if saveAs == '':
            saveAs = self.genTempFile('path')
        if returnAs not in ['path','bool','bin']:
            raise Exception('Invalid returnAs value')
        hr = self.server.additionalHeaders(self.server.timelineHeaders, {
            'Content-Type': 'image/jpeg',
            'X-Line-Mid': mid,
            'X-Line-Album': albumId
        })
        params = {'ver': '1.0', 'oid': objId}
        url = self.server.urlEncode(self.server.LINE_OBS_DOMAIN, '/album/a/download.nhn', params)
        r = self.server.getContent(url, headers=hr)
        if r.status_code == 200:
            self.saveFile(saveAs, r.raw)
            if returnAs == 'path':
                return saveAs
            elif returnAs == 'bool':
                return True
            elif returnAs == 'bin':
                return r.raw
        else:
            raise Exception('Download image album failure.')
