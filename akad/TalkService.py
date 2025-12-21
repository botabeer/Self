# -*- coding: utf-8 -*-
# تم توليد هذا الملف بواسطة Thrift Compiler
# يحتوي هذا الملف على "خدمة التحدث" (TalkService) وهي المحرك الأساسي لعمليات البوت
# تم تعريب التعليقات لشرح الوظائف المسؤولة عن الحماية (Kick, Invite, QR, Cancel)

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys
import logging
from .ttypes import * # استيراد أنواع البيانات المعربة سابقاً

class Iface(object):
    """
    واجهة التحكم الأساسية (Interface)
    هنا يتم تعريف العمليات التي يستخدمها البوت لتنفيذ أوامر الحماية
    """

    def sendMessage(self, seq, message):
        """إرسال رسالة نصية أو وسائط"""
        pass

    def kickoutFromGroup(self, seq, groupMid, targetMids):
        """
        وظيفة الطرد (Kick):
        تستخدم في 'Kick Protection' لإزالة المخربين.
        """
        pass

    def inviteIntoGroup(self, seq, groupMid, targetMids):
        """
        وظيفة الدعوة (Invite):
        تستخدم لإعادة الأعضاء المطرودين ظلماً.
        """
        pass

    def cancelGroupInvitation(self, seq, groupMid, targetMids):
        """
        إلغاء الدعوة (Cancel):
        تستخدم في 'Invite/Cancel Protection' لمنع المخربين من ملء قائمة الانتظار.
        """
        pass

    def updateGroup(self, seq, group):
        """
        تحديث بيانات المجموعة:
        تستخدم في 'QR Protection' لإغلاق الرابط (preventedJoinByTicket = True).
        """
        pass

    def acceptGroupInvitation(self, seq, groupMid):
        """قبول دعوة الانضمام للمجموعة"""
        pass

# ... (يستمر الملف بآلاف السطور التي تتعامل مع تشفير وفك تشفير البيانات)

class Client(Iface):
    """
    العميل (Client): هو الجزء الذي يستدعيه كود الحماية في Nadyasb.py
    """
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        self._seqid = 0

    def kickoutFromGroup(self, seq, groupMid, targetMids):
        # إرسال طلب طرد إلى سيرفرات LINE
        self.send_kickoutFromGroup(seq, groupMid, targetMids)
        self.recv_kickoutFromGroup()

    def send_kickoutFromGroup(self, seq, groupMid, targetMids):
        self._oprot.writeMessageBegin('kickoutFromGroup', TMessageType.CALL, self._seqid)
        args = kickoutFromGroup_args()
        args.seq = seq
        args.groupMid = groupMid
        args.targetMids = targetMids
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
