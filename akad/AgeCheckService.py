#
# خدمة التحقق من العمر - LINE Messaging API v3
# معرب مع أوامر بالإنجليزية
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys, logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport

الهياكل_كاملة = []

class واجهة(object):
    """واجهة خدمة التحقق من عمر المستخدم"""
    
    def checkUserAge(self, carrier, sessionId, verifier, standardAge):
        """التحقق من عمر المستخدم"""
        pass

    def checkUserAgeWithDocomo(self, openIdRedirectUrl, standardAge, verifier):
        """التحقق من العمر عبر Docomo"""
        pass

    def retrieveOpenIdAuthUrlWithDocomo(self):
        """استرجاع رابط مصادقة OpenID مع Docomo"""
        pass

    def retrieveRequestToken(self, carrier):
        """استرجاع رمز الطلب"""
        pass


class عميل(واجهة):
    """عميل خدمة التحقق من العمر"""
    
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def checkUserAge(self, c, sid, v, age):
        self._ارسل_تحقق_عمر(c, sid, v, age)
        return self._استقبل_تحقق_عمر()

    def _ارسل_تحقق_عمر(self, c, sid, v, age):
        self._oprot.writeMessageBegin('checkUserAge', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تحقق_عمر()
        معاملات.carrier = c
        معاملات.sessionId = sid
        معاملات.verifier = v
        معاملات.standardAge = age
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تحقق_عمر(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تحقق_عمر()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل التحقق من العمر")

    def checkUserAgeWithDocomo(self, url, age, v):
        self._ارسل_تحقق_عمر_دوكومو(url, age, v)
        return self._استقبل_تحقق_عمر_دوكومو()

    def _ارسل_تحقق_عمر_دوكومو(self, url, age, v):
        self._oprot.writeMessageBegin('checkUserAgeWithDocomo', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تحقق_عمر_دوكومو()
        معاملات.openIdRedirectUrl = url
        معاملات.standardAge = age
        معاملات.verifier = v
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تحقق_عمر_دوكومو(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تحقق_عمر_دوكومو()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل التحقق من العمر عبر دوكومو")

    def retrieveOpenIdAuthUrlWithDocomo(self):
        self._ارسل_استرجاع_رابط_دوكومو()
        return self._استقبل_استرجاع_رابط_دوكومو()

    def _ارسل_استرجاع_رابط_دوكومو(self):
        self._oprot.writeMessageBegin('retrieveOpenIdAuthUrlWithDocomo', TMessageType.CALL, self._seqid)
        معاملات = معاملات_استرجاع_رابط_دوكومو()
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_استرجاع_رابط_دوكومو(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_استرجاع_رابط_دوكومو()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل استرجاع رابط دوكومو")

    def retrieveRequestToken(self, carrier):
        self._ارسل_استرجاع_رمز(carrier)
        return self._استقبل_استرجاع_رمز()

    def _ارسل_استرجاع_رمز(self, c):
        self._oprot.writeMessageBegin('retrieveRequestToken', TMessageType.CALL, self._seqid)
        معاملات = معاملات_استرجاع_رمز()
        معاملات.carrier = c
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_استرجاع_رمز(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_استرجاع_رمز()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل استرجاع الرمز")


class معالج(واجهة, TProcessor):
    """معالج طلبات الخدمة"""
    
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "checkUserAge": معالج.process_checkUserAge,
            "checkUserAgeWithDocomo": معالج.process_checkUserAgeWithDocomo,
            "retrieveOpenIdAuthUrlWithDocomo": معالج.process_retrieveOpenIdAuthUrlWithDocomo,
            "retrieveRequestToken": معالج.process_retrieveRequestToken
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

    def process_checkUserAge(self, seqid, iprot, oprot):
        معاملات = معاملات_تحقق_عمر()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تحقق_عمر()
        try:
            نتيجة.success = self._handler.checkUserAge(معاملات.carrier, معاملات.sessionId, معاملات.verifier, معاملات.standardAge)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TalkException as e:
            msg_type = TMessageType.REPLY
            نتيجة.e = e
        except TApplicationException as ex:
            logging.exception('استثناء TApplication في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = ex
        except Exception:
            logging.exception('استثناء غير متوقع في المعالج')
            msg_type = TMessageType.EXCEPTION
            نتيجة = TApplicationException(TApplicationException.INTERNAL_ERROR, 'خطأ داخلي')
        oprot.writeMessageBegin("checkUserAge", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_checkUserAgeWithDocomo(self, seqid, iprot, oprot):
        معاملات = معاملات_تحقق_عمر_دوكومو()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تحقق_عمر_دوكومو()
        try:
            نتيجة.success = self._handler.checkUserAgeWithDocomo(معاملات.openIdRedirectUrl, معاملات.standardAge, معاملات.verifier)
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
        oprot.writeMessageBegin("checkUserAgeWithDocomo", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_retrieveOpenIdAuthUrlWithDocomo(self, seqid, iprot, oprot):
        معاملات = معاملات_استرجاع_رابط_دوكومو()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_استرجاع_رابط_دوكومو()
        try:
            نتيجة.success = self._handler.retrieveOpenIdAuthUrlWithDocomo()
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
        oprot.writeMessageBegin("retrieveOpenIdAuthUrlWithDocomo", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_retrieveRequestToken(self, seqid, iprot, oprot):
        معاملات = معاملات_استرجاع_رمز()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_استرجاع_رمز()
        try:
            نتيجة.success = self._handler.retrieveRequestToken(معاملات.carrier)
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
        oprot.writeMessageBegin("retrieveRequestToken", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()


# الهياكل المساعدة
class معاملات_تحقق_عمر(object):
    def __init__(self, carrier=None, sessionId=None, verifier=None, standardAge=None):
        self.carrier = carrier
        self.sessionId = sessionId
        self.verifier = verifier
        self.standardAge = standardAge

    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 2 and ftype == TType.I32: self.carrier = iprot.readI32()
            elif fid == 3 and ftype == TType.STRING: self.sessionId = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            elif fid == 4 and ftype == TType.STRING: self.verifier = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
            elif fid == 5 and ftype == TType.I32: self.standardAge = iprot.readI32()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('checkUserAge_args')
        if self.carrier is not None:
            oprot.writeFieldBegin('carrier', TType.I32, 2)
            oprot.writeI32(self.carrier)
            oprot.writeFieldEnd()
        if self.sessionId is not None:
            oprot.writeFieldBegin('sessionId', TType.STRING, 3)
            oprot.writeString(self.sessionId.encode('utf-8') if sys.version_info[0] == 2 else self.sessionId)
            oprot.writeFieldEnd()
        if self.verifier is not None:
            oprot.writeFieldBegin('verifier', TType.STRING, 4)
            oprot.writeString(self.verifier.encode('utf-8') if sys.version_info[0] == 2 else self.verifier)
            oprot.writeFieldEnd()
        if self.standardAge is not None:
            oprot.writeFieldBegin('standardAge', TType.I32, 5)
            oprot.writeI32(self.standardAge)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_تحقق_عمر(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_تحقق_عمر_دوكومو(object):
    def __init__(self, openIdRedirectUrl=None, standardAge=None, verifier=None):
        self.openIdRedirectUrl = openIdRedirectUrl
        self.standardAge = standardAge
        self.verifier = verifier

class نتيجة_تحقق_عمر_دوكومو(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_استرجاع_رابط_دوكومو(object):
    def read(self, iprot):
        if iprot._fast_decode: return iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()
    
    def write(self, oprot):
        if oprot._fast_encode: return oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
        oprot.writeStructBegin('retrieveOpenIdAuthUrlWithDocomo_args')
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_استرجاع_رابط_دوكومو(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_استرجاع_رمز(object):
    def __init__(self, carrier=None):
        self.carrier = carrier

class نتيجة_استرجاع_رمز(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

الهياكل_كاملة.extend([معاملات_تحقق_عمر, نتيجة_تحقق_عمر, معاملات_تحقق_عمر_دوكومو, نتيجة_تحقق_عمر_دوكومو, معاملات_استرجاع_رابط_دوكومو, نتيجة_استرجاع_رابط_دوكومو, معاملات_استرجاع_رمز, نتيجة_استرجاع_رمز])
fix_spec(الهياكل_كاملة)
del الهياكل_كاملة
