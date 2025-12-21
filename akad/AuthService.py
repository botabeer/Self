#
# خدمة المصادقة - LINE Messaging API v3
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
    """واجهة خدمة المصادقة والتسجيل"""
    
    def normalizePhoneNumber(self, countryCode, phoneNumber, countryCodeHint):
        """تطبيع رقم الهاتف"""
        pass

    def respondE2EELoginRequest(self, verifier, publicKey, encryptedKeyChain, hashKeyChain, errorCode):
        """الرد على طلب تسجيل دخول E2EE"""
        pass

    def confirmE2EELogin(self, verifier, deviceSecret):
        """تأكيد تسجيل دخول E2EE"""
        pass

    def logoutZ(self):
        """تسجيل الخروج"""
        pass

    def loginZ(self, loginRequest):
        """تسجيل الدخول"""
        pass

    def issueTokenForAccountMigrationSettings(self, enforce):
        """إصدار رمز لإعدادات نقل الحساب"""
        pass

    def issueTokenForAccountMigration(self, migrationSessionId):
        """إصدار رمز لنقل الحساب"""
        pass

    def verifyQrcodeWithE2EE(self, verifier, pinCode, errorCode, publicKey, encryptedKeyChain, hashKeyChain):
        """التحقق من رمز QR مع E2EE"""
        pass


class عميل(واجهة):
    """عميل خدمة المصادقة"""
    
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def normalizePhoneNumber(self, cc, pn, hint):
        self._ارسل_تطبيع_رقم(cc, pn, hint)
        return self._استقبل_تطبيع_رقم()

    def _ارسل_تطبيع_رقم(self, cc, pn, hint):
        self._oprot.writeMessageBegin('normalizePhoneNumber', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تطبيع_رقم()
        معاملات.countryCode = cc
        معاملات.phoneNumber = pn
        معاملات.countryCodeHint = hint
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تطبيع_رقم(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تطبيع_رقم()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل تطبيع الرقم")

    def respondE2EELoginRequest(self, v, pk, ekc, hkc, ec):
        self._ارسل_رد_E2EE(v, pk, ekc, hkc, ec)
        self._استقبل_رد_E2EE()

    def _ارسل_رد_E2EE(self, v, pk, ekc, hkc, ec):
        self._oprot.writeMessageBegin('respondE2EELoginRequest', TMessageType.CALL, self._seqid)
        معاملات = معاملات_رد_E2EE()
        معاملات.verifier = v
        معاملات.publicKey = pk
        معاملات.encryptedKeyChain = ekc
        معاملات.hashKeyChain = hkc
        معاملات.errorCode = ec
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_رد_E2EE(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_رد_E2EE()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def confirmE2EELogin(self, v, ds):
        self._ارسل_تأكيد_E2EE(v, ds)
        return self._استقبل_تأكيد_E2EE()

    def _ارسل_تأكيد_E2EE(self, v, ds):
        self._oprot.writeMessageBegin('confirmE2EELogin', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تأكيد_E2EE()
        معاملات.verifier = v
        معاملات.deviceSecret = ds
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تأكيد_E2EE(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تأكيد_E2EE()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل تأكيد E2EE")

    def logoutZ(self):
        self._ارسل_خروج()
        self._استقبل_خروج()

    def _ارسل_خروج(self):
        self._oprot.writeMessageBegin('logoutZ', TMessageType.CALL, self._seqid)
        معاملات = معاملات_خروج()
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_خروج(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_خروج()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def loginZ(self, req):
        self._ارسل_دخول(req)
        return self._استقبل_دخول()

    def _ارسل_دخول(self, req):
        self._oprot.writeMessageBegin('loginZ', TMessageType.CALL, self._seqid)
        معاملات = معاملات_دخول()
        معاملات.loginRequest = req
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_دخول(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_دخول()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل تسجيل الدخول")

    def issueTokenForAccountMigrationSettings(self, enforce):
        self._ارسل_رمز_اعدادات_نقل(enforce)
        return self._استقبل_رمز_اعدادات_نقل()

    def _ارسل_رمز_اعدادات_نقل(self, e):
        self._oprot.writeMessageBegin('issueTokenForAccountMigrationSettings', TMessageType.CALL, self._seqid)
        معاملات = معاملات_رمز_اعدادات_نقل()
        معاملات.enforce = e
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_رمز_اعدادات_نقل(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_رمز_اعدادات_نقل()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل إصدار رمز الإعدادات")

    def issueTokenForAccountMigration(self, sid):
        self._ارسل_رمز_نقل(sid)
        return self._استقبل_رمز_نقل()

    def _ارسل_رمز_نقل(self, sid):
        self._oprot.writeMessageBegin('issueTokenForAccountMigration', TMessageType.CALL, self._seqid)
        معاملات = معاملات_رمز_نقل()
        معاملات.migrationSessionId = sid
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_رمز_نقل(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_رمز_نقل()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل إصدار رمز النقل")

    def verifyQrcodeWithE2EE(self, v, pin, ec, pk, ekc, hkc):
        self._ارسل_تحقق_QR_E2EE(v, pin, ec, pk, ekc, hkc)
        return self._استقبل_تحقق_QR_E2EE()

    def _ارسل_تحقق_QR_E2EE(self, v, pin, ec, pk, ekc, hkc):
        self._oprot.writeMessageBegin('verifyQrcodeWithE2EE', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تحقق_QR_E2EE()
        معاملات.verifier = v
        معاملات.pinCode = pin
        معاملات.errorCode = ec
        معاملات.publicKey = pk
        معاملات.encryptedKeyChain = ekc
        معاملات.hashKeyChain = hkc
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تحقق_QR_E2EE(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تحقق_QR_E2EE()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل التحقق من QR")


class معالج(واجهة, TProcessor):
    """معالج طلبات المصادقة"""
    
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "normalizePhoneNumber": معالج.process_normalizePhoneNumber,
            "respondE2EELoginRequest": معالج.process_respondE2EELoginRequest,
            "confirmE2EELogin": معالج.process_confirmE2EELogin,
            "logoutZ": معالج.process_logoutZ,
            "loginZ": معالج.process_loginZ,
            "issueTokenForAccountMigrationSettings": معالج.process_issueTokenForAccountMigrationSettings,
            "issueTokenForAccountMigration": معالج.process_issueTokenForAccountMigration,
            "verifyQrcodeWithE2EE": معالج.process_verifyQrcodeWithE2EE
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

    def process_normalizePhoneNumber(self, seqid, iprot, oprot):
        معاملات = معاملات_تطبيع_رقم()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تطبيع_رقم()
        try:
            نتيجة.success = self._handler.normalizePhoneNumber(معاملات.countryCode, معاملات.phoneNumber, معاملات.countryCodeHint)
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
        oprot.writeMessageBegin("normalizePhoneNumber", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_respondE2EELoginRequest(self, seqid, iprot, oprot):
        معاملات = معاملات_رد_E2EE()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_رد_E2EE()
        try:
            self._handler.respondE2EELoginRequest(معاملات.verifier, معاملات.publicKey, معاملات.encryptedKeyChain, معاملات.hashKeyChain, معاملات.errorCode)
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
        oprot.writeMessageBegin("respondE2EELoginRequest", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_confirmE2EELogin(self, seqid, iprot, oprot):
        معاملات = معاملات_تأكيد_E2EE()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تأكيد_E2EE()
        try:
            نتيجة.success = self._handler.confirmE2EELogin(معاملات.verifier, معاملات.deviceSecret)
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
        oprot.writeMessageBegin("confirmE2EELogin", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_logoutZ(self, seqid, iprot, oprot):
        معاملات = معاملات_خروج()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_خروج()
        try:
            self._handler.logoutZ()
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
        oprot.writeMessageBegin("logoutZ", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_loginZ(self, seqid, iprot, oprot):
        معاملات = معاملات_دخول()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_دخول()
        try:
            نتيجة.success = self._handler.loginZ(معاملات.loginRequest)
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
        oprot.writeMessageBegin("loginZ", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_issueTokenForAccountMigrationSettings(self, seqid, iprot, oprot):
        معاملات = معاملات_رمز_اعدادات_نقل()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_رمز_اعدادات_نقل()
        try:
            نتيجة.success = self._handler.issueTokenForAccountMigrationSettings(معاملات.enforce)
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
        oprot.writeMessageBegin("issueTokenForAccountMigrationSettings", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_issueTokenForAccountMigration(self, seqid, iprot, oprot):
        معاملات = معاملات_رمز_نقل()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_رمز_نقل()
        try:
            نتيجة.success = self._handler.issueTokenForAccountMigration(معاملات.migrationSessionId)
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
        oprot.writeMessageBegin("issueTokenForAccountMigration", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_verifyQrcodeWithE2EE(self, seqid, iprot, oprot):
        معاملات = معاملات_تحقق_QR_E2EE()
        معاملات.read(iprot)
        iprot.readMessageEnd()
        نتيجة = نتيجة_تحقق_QR_E2EE()
        try:
            نتيجة.success = self._handler.verifyQrcodeWithE2EE(معاملات.verifier, معاملات.pinCode, معاملات.errorCode, معاملات.publicKey, معاملات.encryptedKeyChain, معاملات.hashKeyChain)
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
        oprot.writeMessageBegin("verifyQrcodeWithE2EE", msg_type, seqid)
        نتيجة.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()


# الهياكل المساعدة (مضغوطة)
class معاملات_تطبيع_رقم(object):
    def __init__(self, countryCode=None, phoneNumber=None, countryCodeHint=None):
        self.countryCode = countryCode
        self.phoneNumber = phoneNumber
        self.countryCodeHint = countryCodeHint

class نتيجة_تطبيع_رقم(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_رد_E2EE(object):
    def __init__(self, verifier=None, publicKey=None, encryptedKeyChain=None, hashKeyChain=None, errorCode=None):
        self.verifier = verifier
        self.publicKey = publicKey
        self.encryptedKeyChain = encryptedKeyChain
        self.hashKeyChain = hashKeyChain
        self.errorCode = errorCode

class نتيجة_رد_E2EE(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_تأكيد_E2EE(object):
    def __init__(self, verifier=None, deviceSecret=None):
        self.verifier = verifier
        self.deviceSecret = deviceSecret

class نتيجة_تأكيد_E2EE(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_خروج(object):
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
        oprot.writeStructBegin('logoutZ_args')
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_خروج(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_دخول(object):
    def __init__(self, loginRequest=None):
        self.loginRequest = loginRequest

class نتيجة_دخول(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_رمز_اعدادات_نقل(object):
    def __init__(self, enforce=None):
        self.enforce = enforce

class نتيجة_رمز_اعدادات_نقل(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_رمز_نقل(object):
    def __init__(self, migrationSessionId=None):
        self.migrationSessionId = migrationSessionId

class نتيجة_رمز_نقل(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_تحقق_QR_E2EE(object):
    def __init__(self, verifier=None, pinCode=None, errorCode=None, publicKey=None, encryptedKeyChain=None, hashKeyChain=None):
        self.verifier = verifier
        self.pinCode = pinCode
        self.errorCode = errorCode
        self.publicKey = publicKey
        self.encryptedKeyChain = encryptedKeyChain
        self.hashKeyChain = hashKeyChain

class نتيجة_تحقق_QR_E2EE(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

الهياكل.extend([معاملات_تطبيع_رقم, نتيجة_تطبيع_رقم, معاملات_رد_E2EE, نتيجة_رد_E2EE, معاملات_تأكيد_E2EE, نتيجة_تأكيد_E2EE, معاملات_خروج, نتيجة_خروج, معاملات_دخول, نتيجة_دخول, معاملات_رمز_اعدادات_نقل, نتيجة_رمز_اعدادات
