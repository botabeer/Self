#
# خدمة البوت - LINE Messaging API v3
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
    """واجهة خدمة البوت"""
    
    def notifyLeaveGroup(self, groupMid):
        """إشعار بمغادرة المجموعة"""
        pass

    def notifyLeaveRoom(self, roomMid):
        """إشعار بمغادرة الغرفة"""
        pass

    def getBotUseInfo(self, botMid):
        """الحصول على معلومات استخدام البوت"""
        pass

    def sendChatCheckedByWatermark(self, seq, mid, watermark, sessionId):
        """إرسال تأكيد قراءة المحادثة"""
        pass


class عميل(واجهة):
    """عميل خدمة البوت"""
    
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def notifyLeaveGroup(self, gid):
        self._ارسل_مغادرة_مجموعة(gid)
        self._استقبل_مغادرة_مجموعة()

    def _ارسل_مغادرة_مجموعة(self, gid):
        self._oprot.writeMessageBegin('notifyLeaveGroup', TMessageType.CALL, self._seqid)
        معاملات = معاملات_مغادرة_مجموعة()
        معاملات.groupMid = gid
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_مغادرة_مجموعة(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_مغادرة_مجموعة()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def notifyLeaveRoom(self, rid):
        self._ارسل_مغادرة_غرفة(rid)
        self._استقبل_مغادرة_غرفة()

    def _ارسل_مغادرة_غرفة(self, rid):
        self._oprot.writeMessageBegin('notifyLeaveRoom', TMessageType.CALL, self._seqid)
        معاملات = معاملات_مغادرة_غرفة()
        معاملات.roomMid = rid
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_مغادرة_غرفة(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_مغادرة_غرفة()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def getBotUseInfo(self, bid):
        self._ارسل_معلومات_بوت(bid)
        return self._استقبل_معلومات_بوت()

    def _ارسل_معلومات_بوت(self, bid):
        self._oprot.writeMessageBegin('getBotUseInfo', TMessageType.CALL, self._seqid)
        معاملات = معاملات_معلومات_بوت()
        معاملات.botMid = bid
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_معلومات_بوت(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_معلومات_بوت()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل الحصول على معلومات البوت")

    def sendChatCheckedByWatermark(self, seq, mid, wm, sid):
        self._ارسل_تأكيد_قراءة(seq, mid, wm, sid)
        self._استقبل_تأكيد_قراءة()

    def _ارسل_تأكيد_قراءة(self, seq, mid, wm, sid):
        self._oprot.writeMessageBegin('sendChatCheckedByWatermark', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تأكيد_قراءة()
        معاملات.seq = seq
        معاملات.mid = mid
        معاملات.watermark = wm
        معاملات.sessionId = sid
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تأكيد_قراءة(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تأكيد_قراءة()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e


class معالج(واجهة, TProcessor):
    """معالج طلبات البوت"""
    
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "notifyLeaveGroup": معالج.process_notifyLeaveGroup,
            "notifyLeaveRoom": معالج.process_notifyLeaveRoom,
            "getBotUseInfo": معالج.process_getBotUseInfo,
            "sendChatCheckedByWatermark": معالج.process_sendChatCheckedByWatermark
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

    def process_notifyLeaveGroup(self, seqid, iprot, oprot):
        معاملات = معاملات_مغادرة_مجموعة()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_مغادرة_مجموعة()
        try:
            self._handler.notifyLeaveGroup(معاملات.groupMid)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            نتيجة.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("notifyLeaveGroup", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_notifyLeaveRoom(self, seqid, iprot, oprot):
        معاملات = معاملات_مغادرة_غرفة()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_مغادرة_غرفة()
        try:
            self._handler.notifyLeaveRoom(معاملات.roomMid)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            نتيجة.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("notifyLeaveRoom", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_getBotUseInfo(self, seqid, iprot, oprot):
        معاملات = معاملات_معلومات_بوت()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_معلومات_بوت()
        try:
            نتيجة.success = self._handler.getBotUseInfo(معاملات.botMid)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            نتيجة.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("getBotUseInfo", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_sendChatCheckedByWatermark(self, seqid, iprot, oprot):
        معاملات = معاملات_تأكيد_قراءة()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تأكيد_قراءة()
        try:
            self._handler.sendChatCheckedByWatermark(معاملات.seq, معاملات.mid, معاملات.watermark, معاملات.sessionId)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            نتيجة.e = e
        except Exception:
            logging.exception('خطأ في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("sendChatCheckedByWatermark", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()


# الهياكل المساعدة
class معاملات_مغادرة_مجموعة(object):
    def __init__(self, groupMid=None):
        self.groupMid = groupMid

    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 1 and ftype == TType.STRING:
                self.groupMid = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('notifyLeaveGroup_args')
        if self.groupMid is not None:
            oprot.writeFieldBegin('groupMid', TType.STRING, 1)
            oprot.writeString(self.groupMid.encode('utf-8') if sys.version_info[0] == 2 else self.groupMid)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_مغادرة_مجموعة(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_مغادرة_غرفة(object):
    def __init__(self, roomMid=None):
        self.roomMid = roomMid

    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 1 and ftype == TType.STRING:
                self.roomMid = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('notifyLeaveRoom_args')
        if self.roomMid is not None:
            oprot.writeFieldBegin('roomMid', TType.STRING, 1)
            oprot.writeString(self.roomMid.encode('utf-8') if sys.version_info[0] == 2 else self.roomMid)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_مغادرة_غرفة(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_معلومات_بوت(object):
    def __init__(self, botMid=None):
        self.botMid = botMid

    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 2 and ftype == TType.STRING:
                self.botMid = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('getBotUseInfo_args')
        if self.botMid is not None:
            oprot.writeFieldBegin('botMid', TType.STRING, 2)
            oprot.writeString(self.botMid.encode('utf-8') if sys.version_info[0] == 2 else self.botMid)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_معلومات_بوت(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_تأكيد_قراءة(object):
    def __init__(self, seq=None, mid=None, watermark=None, sessionId=None):
        self.seq = seq
        self.mid = mid
        self.watermark = watermark
        self.sessionId = sessionId

    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 1 and ftype == TType.I32: self.seq = iprot.readI32()
            elif fid == 2 and ftype == TType.STRING: self.mid = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            elif fid == 3 and ftype == TType.I64: self.watermark = iprot.readI64()
            elif fid == 4 and ftype == TType.BYTE: self.sessionId = iprot.readByte()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('sendChatCheckedByWatermark_args')
        if self.seq is not None:
            oprot.writeFieldBegin('seq', TType.I32, 1)
            oprot.writeI32(self.seq)
            oprot.writeFieldEnd()
        if self.mid is not None:
            oprot.writeFieldBegin('mid', TType.STRING, 2)
            oprot.writeString(self.mid.encode('utf-8') if sys.version_info[0] == 2 else self.mid)
            oprot.writeFieldEnd()
        if self.watermark is not None:
            oprot.writeFieldBegin('watermark', TType.I64, 3)
            oprot.writeI64(self.watermark)
            oprot.writeFieldEnd()
        if self.sessionId is not None:
            oprot.writeFieldBegin('sessionId', TType.BYTE, 4)
            oprot.writeByte(self.sessionId)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_تأكيد_قراءة(object):
    def __init__(self, e=None):
        self.e = e

الهياكل.extend([معاملات_مغادرة_مجموعة, نتيجة_مغادرة_مجموعة, معاملات_مغادرة_غرفة, نتيجة_مغادرة_غرفة, معاملات_معلومات_بوت, نتيجة_معلومات_بوت, معاملات_تأكيد_قراءة, نتيجة_تأكيد_قراءة])
fix_spec(الهياكل)
del الهياكل
