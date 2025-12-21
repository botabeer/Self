#
# خدمة القروبات والحماية - LINE Messaging API v3
# معرب مع أوامر إنجليزية
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys, logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport

الهياكل = []

class واجهة(object):
    """واجهة خدمة القروبات والحماية"""
    
    def getGroup(self, groupId):
        """جلب معلومات القروب"""
        pass

    def getGroups(self, groupIds):
        """جلب قائمة القروبات"""
        pass

    def getGroupsV2(self, groupIds):
        """جلب قائمة القروبات v2"""
        pass

    def getCompactGroup(self, groupId):
        """جلب معلومات مختصرة للقروب"""
        pass

    def createGroup(self, seq, name, memberMids):
        """إنشاء قروب"""
        pass

    def inviteIntoGroup(self, reqSeq, groupId, contactIds):
        """دعوة أعضاء للقروب"""
        pass

    def acceptGroupInvitation(self, reqSeq, groupId):
        """قبول دعوة القروب"""
        pass

    def acceptGroupInvitationByTicket(self, reqSeq, groupId, ticketId):
        """قبول دعوة القروب بالتذكرة"""
        pass

    def cancelGroupInvitation(self, reqSeq, groupId, contactIds):
        """إلغاء دعوة القروب"""
        pass

    def kickoutFromGroup(self, reqSeq, groupId, contactIds):
        """طرد من القروب"""
        pass

    def leaveGroup(self, reqSeq, groupId):
        """مغادرة القروب"""
        pass

    def updateGroup(self, reqSeq, group):
        """تحديث بيانات القروب"""
        pass

    def updateGroupPreferenceAttribute(self, reqSeq, groupId, updatedAttrs):
        """تحديث إعدادات القروب"""
        pass

    def reissueGroupTicket(self, groupId):
        """إعادة إصدار رابط القروب"""
        pass

    def findGroupByTicket(self, ticketId):
        """البحث عن قروب بالرابط"""
        pass

    def getGroupWithoutMembers(self, groupId):
        """جلب القروب بدون قائمة الأعضاء"""
        pass


class عميل(واجهة):
    """عميل خدمة القروبات"""
    
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def getGroup(self, gid):
        self._ارسل_جلب_قروب(gid)
        return self._استقبل_جلب_قروب()

    def _ارسل_جلب_قروب(self, gid):
        self._oprot.writeMessageBegin('getGroup', TMessageType.CALL, self._seqid)
        م = معاملات_جلب_قروب()
        م.groupId = gid
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_جلب_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_جلب_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.success is not None: return ن.success
        if ن.e is not None: raise ن.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل جلب القروب")

    def getGroups(self, gids):
        self._ارسل_جلب_قروبات(gids)
        return self._استقبل_جلب_قروبات()

    def _ارسل_جلب_قروبات(self, gids):
        self._oprot.writeMessageBegin('getGroups', TMessageType.CALL, self._seqid)
        م = معاملات_جلب_قروبات()
        م.groupIds = gids
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_جلب_قروبات(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_جلب_قروبات()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.success is not None: return ن.success
        if ن.e is not None: raise ن.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل جلب القروبات")

    def createGroup(self, seq, name, mids):
        self._ارسل_انشاء_قروب(seq, name, mids)
        return self._استقبل_انشاء_قروب()

    def _ارسل_انشاء_قروب(self, seq, name, mids):
        self._oprot.writeMessageBegin('createGroup', TMessageType.CALL, self._seqid)
        م = معاملات_انشاء_قروب()
        م.seq = seq
        م.name = name
        م.memberMids = mids
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_انشاء_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_انشاء_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.success is not None: return ن.success
        if ن.e is not None: raise ن.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل إنشاء القروب")

    def inviteIntoGroup(self, seq, gid, cids):
        self._ارسل_دعوة_قروب(seq, gid, cids)
        self._استقبل_دعوة_قروب()

    def _ارسل_دعوة_قروب(self, seq, gid, cids):
        self._oprot.writeMessageBegin('inviteIntoGroup', TMessageType.CALL, self._seqid)
        م = معاملات_دعوة_قروب()
        م.reqSeq = seq
        م.groupId = gid
        م.contactIds = cids
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_دعوة_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_دعوة_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.e is not None: raise ن.e

    def kickoutFromGroup(self, seq, gid, cids):
        self._ارسل_طرد_قروب(seq, gid, cids)
        self._استقبل_طرد_قروب()

    def _ارسل_طرد_قروب(self, seq, gid, cids):
        self._oprot.writeMessageBegin('kickoutFromGroup', TMessageType.CALL, self._seqid)
        م = معاملات_طرد_قروب()
        م.reqSeq = seq
        م.groupId = gid
        م.contactIds = cids
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_طرد_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_طرد_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.e is not None: raise ن.e

    def leaveGroup(self, seq, gid):
        self._ارسل_مغادرة_قروب(seq, gid)
        self._استقبل_مغادرة_قروب()

    def _ارسل_مغادرة_قروب(self, seq, gid):
        self._oprot.writeMessageBegin('leaveGroup', TMessageType.CALL, self._seqid)
        م = معاملات_مغادرة_قروب()
        م.reqSeq = seq
        م.groupId = gid
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_مغادرة_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_مغادرة_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.e is not None: raise ن.e

    def updateGroup(self, seq, grp):
        self._ارسل_تحديث_قروب(seq, grp)
        self._استقبل_تحديث_قروب()

    def _ارسل_تحديث_قروب(self, seq, grp):
        self._oprot.writeMessageBegin('updateGroup', TMessageType.CALL, self._seqid)
        م = معاملات_تحديث_قروب()
        م.reqSeq = seq
        م.group = grp
        م.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تحديث_قروب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        ن = نتيجة_تحديث_قروب()
        ن.read(iprot)
        iprot.readMessageEnd()
        if ن.e is not None: raise ن.e


class معالج(واجهة, TProcessor):
    """معالج طلبات القروبات"""
    
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "getGroup": معالج.process_getGroup,
            "getGroups": معالج.process_getGroups,
            "createGroup": معالج.process_createGroup,
            "inviteIntoGroup": معالج.process_inviteIntoGroup,
            "kickoutFromGroup": معالج.process_kickoutFromGroup,
            "leaveGroup": معالج.process_leaveGroup,
            "updateGroup": معالج.process_updateGroup
        }

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, f'دالة غير معروفة: {name}')
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        self._processMap[name](self, seqid, iprot, oprot)
        return True

    def process_getGroup(self, seqid, iprot, oprot):
        م = معاملات_جلب_قروب()
        م.read(iprot)
        iprot.readMessageEnd()
        ن = نتيجة_جلب_قروب()
        try:
            ن.success = self._handler.getGroup(م.groupId)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            ن.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            ن = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("getGroup", msg_type, seqid)
        ن.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_kickoutFromGroup(self, seqid, iprot, oprot):
        م = معاملات_طرد_قروب()
        م.read(iprot)
        iprot.readMessageEnd()
        ن = نتيجة_طرد_قروب()
        try:
            self._handler.kickoutFromGroup(م.reqSeq, م.groupId, م.contactIds)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            ن.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            ن = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("kickoutFromGroup", msg_type, seqid)
        ن.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()


# الهياكل المساعدة
class معاملات_جلب_قروب(object):
    def __init__(self, groupId=None):
        self.groupId = groupId

class نتيجة_جلب_قروب(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_جلب_قروبات(object):
    def __init__(self, groupIds=None):
        self.groupIds = groupIds

class نتيجة_جلب_قروبات(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_انشاء_قروب(object):
    def __init__(self, seq=None, name=None, memberMids=None):
        self.seq = seq
        self.name = name
        self.memberMids = memberMids

class نتيجة_انشاء_قروب(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_دعوة_قروب(object):
    def __init__(self, reqSeq=None, groupId=None, contactIds=None):
        self.reqSeq = reqSeq
        self.groupId = groupId
        self.contactIds = contactIds

class نتيجة_دعوة_قروب(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_طرد_قروب(object):
    def __init__(self, reqSeq=None, groupId=None, contactIds=None):
        self.reqSeq = reqSeq
        self.groupId = groupId
        self.contactIds = contactIds

class نتيجة_طرد_قروب(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_مغادرة_قروب(object):
    def __init__(self, reqSeq=None, groupId=None):
        self.reqSeq = reqSeq
        self.groupId = groupId

class نتيجة_مغادرة_قروب(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_تحديث_قروب(object):
    def __init__(self, reqSeq=None, group=None):
        self.reqSeq = reqSeq
        self.group = group

class نتيجة_تحديث_قروب(object):
    def __init__(self, e=None):
        self.e = e

الهياكل.extend([معاملات_جلب_قروب, نتيجة_جلب_قروب, معاملات_جلب_قروبات, نتيجة_جلب_قروبات, معاملات_انشاء_قروب, نتيجة_انشاء_قروب, معاملات_دعوة_قروب, نتيجة_دعوة_قروب, معاملات_طرد_قروب, نتيجة_طرد_قروب, معاملات_مغادرة_قروب, نتيجة_مغادرة_قروب, معاملات_تحديث_قروب, نتيجة_تحديث_قروب])
