#
# خدمة إشراف الحساب - LINE Messaging API v3
# تم التعريب والتحديث للتوافق مع المعايير الحديثة
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport

الهياكل_كاملة = []

class واجهة(object):
    """واجهة خدمة إدارة الحسابات الافتراضية"""
    
    def احصل_على_مفتاح_RSA(self):
        """الحصول على مفتاح RSA للتشفير"""
        pass

    def اخطار_نتيجة_تاكيد_البريد(self, خريطة_المعاملات):
        """إخطار بنتيجة تأكيد البريد الإلكتروني"""
        pass

    def تسجيل_حساب_افتراضي(self, اللغة, معرف_مستخدم_مشفر, كلمة_سر_مشفرة):
        """تسجيل حساب افتراضي جديد"""
        pass

    def طلب_تغيير_كلمة_سر_حساب_افتراضي(self, معرف_افتراضي, معرف_مستخدم_مشفر, كلمة_سر_قديمة_مشفرة, كلمة_سر_جديدة_مشفرة):
        """طلب تغيير كلمة سر حساب افتراضي"""
        pass

    def طلب_تعيين_كلمة_سر_حساب_افتراضي(self, معرف_افتراضي, معرف_مستخدم_مشفر, كلمة_سر_جديدة_مشفرة):
        """طلب تعيين كلمة سر جديدة لحساب افتراضي"""
        pass

    def الغاء_تسجيل_حساب_افتراضي(self, معرف_افتراضي):
        """إلغاء تسجيل حساب افتراضي"""
        pass


class عميل(واجهة):
    """عميل خدمة LINE API v3"""
    
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def احصل_على_مفتاح_RSA(self):
        self._ارسل_طلب_مفتاح_RSA()
        return self._استقبل_مفتاح_RSA()

    def _ارسل_طلب_مفتاح_RSA(self):
        self._oprot.writeMessageBegin('getRSAKey', TMessageType.CALL, self._seqid)
        معاملات = معاملات_مفتاح_RSA()
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_مفتاح_RSA(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_مفتاح_RSA()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل الحصول على مفتاح RSA")

    def اخطار_نتيجة_تاكيد_البريد(self, خريطة_المعاملات):
        self._ارسل_اخطار_بريد(خريطة_المعاملات)
        self._استقبل_اخطار_بريد()

    def _ارسل_اخطار_بريد(self, خريطة_المعاملات):
        self._oprot.writeMessageBegin('notifyEmailConfirmationResult', TMessageType.CALL, self._seqid)
        معاملات = معاملات_اخطار_بريد()
        معاملات.parameterMap = خريطة_المعاملات
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_اخطار_بريد(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_اخطار_بريد()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def تسجيل_حساب_افتراضي(self, اللغة, معرف_مستخدم_مشفر, كلمة_سر_مشفرة):
        self._ارسل_تسجيل_حساب(اللغة, معرف_مستخدم_مشفر, كلمة_سر_مشفرة)
        return self._استقبل_تسجيل_حساب()

    def _ارسل_تسجيل_حساب(self, l, u, p):
        self._oprot.writeMessageBegin('registerVirtualAccount', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تسجيل_حساب()
        معاملات.locale = l
        معاملات.encryptedVirtualUserId = u
        معاملات.encryptedPassword = p
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تسجيل_حساب(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تسجيل_حساب()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.success is not None: return نتيجة.success
        if نتيجة.e is not None: raise نتيجة.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "فشل تسجيل الحساب")

    def طلب_تغيير_كلمة_سر_حساب_افتراضي(self, m, u, op, np):
        self._ارسل_تغيير_كلمة_سر(m, u, op, np)
        self._استقبل_تغيير_كلمة_سر()

    def _ارسل_تغيير_كلمة_سر(self, m, u, op, np):
        self._oprot.writeMessageBegin('requestVirtualAccountPasswordChange', TMessageType.CALL, self._seqid)
        معاملات = معاملات_تغيير_كلمة_سر()
        معاملات.virtualMid = m
        معاملات.encryptedVirtualUserId = u
        معاملات.encryptedOldPassword = op
        معاملات.encryptedNewPassword = np
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_تغيير_كلمة_سر(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_تغيير_كلمة_سر()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e

    def الغاء_تسجيل_حساب_افتراضي(self, معرف_افتراضي):
        self._ارسل_الغاء_تسجيل(معرف_افتراضي)
        self._استقبل_الغاء_تسجيل()

    def _ارسل_الغاء_تسجيل(self, معرف_افتراضي):
        self._oprot.writeMessageBegin('unregisterVirtualAccount', TMessageType.CALL, self._seqid)
        معاملات = معاملات_الغاء_تسجيل()
        معاملات.virtualMid = معرف_افتراضي
        معاملات.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def _استقبل_الغاء_تسجيل(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        نتيجة = نتيجة_الغاء_تسجيل()
        نتيجة.read(iprot)
        iprot.readMessageEnd()
        if نتيجة.e is not None: raise نتيجة.e


# فئات المعاملات والنتائج (مضغوطة)
class معاملات_مفتاح_RSA(object):
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
        oprot.writeStructBegin('getRSAKey_args')
        oprot.writeFieldStop()
        oprot.writeStructEnd()

class نتيجة_مفتاح_RSA(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_اخطار_بريد(object):
    def __init__(self, parameterMap=None):
        self.parameterMap = parameterMap

class نتيجة_اخطار_بريد(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_تسجيل_حساب(object):
    def __init__(self, locale=None, encryptedVirtualUserId=None, encryptedPassword=None):
        self.locale = locale
        self.encryptedVirtualUserId = encryptedVirtualUserId
        self.encryptedPassword = encryptedPassword

class نتيجة_تسجيل_حساب(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

class معاملات_تغيير_كلمة_سر(object):
    def __init__(self, virtualMid=None, encryptedVirtualUserId=None, encryptedOldPassword=None, encryptedNewPassword=None):
        self.virtualMid = virtualMid
        self.encryptedVirtualUserId = encryptedVirtualUserId
        self.encryptedOldPassword = encryptedOldPassword
        self.encryptedNewPassword = encryptedNewPassword

class نتيجة_تغيير_كلمة_سر(object):
    def __init__(self, e=None):
        self.e = e

class معاملات_الغاء_تسجيل(object):
    def __init__(self, virtualMid=None):
        self.virtualMid = virtualMid

class نتيجة_الغاء_تسجيل(object):
    def __init__(self, e=None):
        self.e = e

# تعريف المواصفات
الهياكل_كاملة.extend([
    معاملات_مفتاح_RSA, نتيجة_مفتاح_RSA,
    معاملات_اخطار_بريد, نتيجة_اخطار_بريد,
    معاملات_تسجيل_حساب, نتيجة_تسجيل_حساب,
    معاملات_تغيير_كلمة_سر, نتيجة_تغيير_كلمة_سر,
    معاملات_الغاء_تسجيل, نتيجة_الغاء_تسجيل
])

fix_spec(الهياكل_كاملة)
del الهياكل_كاملة
