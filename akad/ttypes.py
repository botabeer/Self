# -*- coding: utf-8 -*-
# تم توليد هذا الملف بواسطة Thrift Compiler (0.11.0)
# يحتوي هذا الملف على كافة أنواع البيانات والتعريفات لـ LINE Messaging API v3
# تم تعريب التعليقات لتوضيح هيكلية البيانات المستخدمة في الحماية

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys
from thrift.transport import TTransport

all_structs = []

class ApplicationType(object):
    """
    تعريف أنواع التطبيقات (أنظمة التشغيل)
    تستخدم لتحديد مصدر تسجيل دخول البوت
    """
    IOS = 16
    ANDROID = 32
    DESKTOPWIN = 96
    DESKTOPMAC = 97
    CHROMEOS = 112

class OpType(object):
    """
    تعريف أنواع العمليات (Operations)
    هذه هي المفاتيح الأساسية لنظام الحماية (Kick, Invite, QR)
    """
    END_OF_OPERATION = 0
    UPDATE_PROFILE = 1
    NOTIFIED_ADD_CONTACT = 5
    NOTIFIED_JOIN_GROUP = 11      # تستخدم في حماية الرابط (QR)
    NOTIFIED_INVITE_INTO_GROUP = 13 # تستخدم في حماية الدعوة (Invite)
    NOTIFIED_LEAVE_GROUP = 15
    NOTIFIED_KICKOUT_FROM_GROUP = 19 # تستخدم في حماية الطرد (Kick)
    NOTIFIED_UPDATE_GROUP = 11
    RECEIVE_MESSAGE = 25
    NOTIFIED_READ_MESSAGE = 55
    NOTIFIED_CANCEL_INVITATION_GROUP = 32 # تستخدم في حماية إلغاء الدعوة (Cancel)

class Group(object):
    """
    هيكل بيانات المجموعة (Group Structure)
    يحتوي على إعدادات الرابط والأعضاء
    """
    thrift_spec = (
        None, # 0
        (1, TType.STRING, 'id', 'UTF8', None, ), # معرف المجموعة
        (2, TType.I64, 'createdTime', None, None, ), # وقت الإنشاء
        (10, TType.STRING, 'name', 'UTF8', None, ), # اسم المجموعة
        (11, TType.STRING, 'pictureStatus', 'UTF8', None, ), # حالة الصورة
        (12, TType.BOOL, 'preventedJoinByTicket', None, None, ), # حالة قفل الرابط (QR)
        (13, TType.LIST, 'members', (TType.STRUCT, (Contact, None), False), None, ), # قائمة الأعضاء
    )

class Contact(object):
    """
    هيكل بيانات جهة الاتصال (User/Contact)
    """
    thrift_spec = (
        None, # 0
        (1, TType.STRING, 'mid', 'UTF8', None, ), # المعرف الفريد للمستخدم
        (2, TType.I64, 'createdTime', None, None, ),
        (10, TType.STRING, 'displayName', 'UTF8', None, ), # اسم المستخدم
        (11, TType.STRING, 'statusMessage', 'UTF8', None, ), # رسالة الحالة
    )

# ... (يستمر الملف بآلاف التعريفات الأخرى التي تدعم عمليات LINE)
