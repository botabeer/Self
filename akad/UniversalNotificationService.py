# -*- coding: utf-8 -*-
# تم توليد هذا الملف بواسطة Thrift Compiler (0.11.0)
# ملاحظة: هذا الملف تقني بحت ولا ينصح بتعديل المنطق البرمجي فيه يدوياً.
# قمنا بتعريب التعليقات لشرح كيفية عمل جسر الإشعارات.

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
all_structs = []

class Iface(object):
    """
    واجهة الخدمة (Interface): تحديثات الإشعارات العالمية.
    """
    def notify(self, event):
        """
        الوظيفة: إرسال إشعار بحدث معين.
        المعاملات:
         - event: الحدث الذي سيتم إرساله.
        """
        pass

class Client(Iface):
    """
    العميل (Client): يستخدمه البوت لإرسال الطلبات إلى سيرفر LINE.
    """
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot is not None:
            self._oprot = oprot
        self._seqid = 0

    def notify(self, event):
        """
        إرسال إشعار وانتظار الرد.
        """
        self.send_notify(event)
        self.recv_notify()

    def send_notify(self, event):
        # بدء عملية إرسال الرسالة عبر بروتوكول Thrift
        self._oprot.writeMessageBegin('notify', TMessageType.CALL, self._seqid)
        args = notify_args()
        args.event = event
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_notify(self):
        # استقبال الرد من السيرفر والتأكد من عدم وجود أخطاء
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = notify_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.e is not None:
            raise result.e
        return

class Processor(Iface, TProcessor):
    """
    المعالج (Processor): يقوم باستلام البيانات الخام وتحويلها إلى وظائف برمجية.
    """
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {}
        self._processMap["notify"] = Processor.process_notify

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return True
        else:
            return self._processMap[name](self, seqid, iprot, oprot)

    def process_notify(self, seqid, iprot, oprot):
        # معالجة طلب إشعار وارد
        args = notify_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = notify_result()
        try:
            self._handler.notify(args.event)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except UniversalNotificationServiceException as e:
            msg_type = TMessageType.REPLY
            result.e = e
        except Exception as ex:
            msg_type = TMessageType.EXCEPTION
            logging.exception(ex)
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        
        oprot.writeMessageBegin("notify", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# --- الهياكل البيانات (Helper Structs) ---

class notify_args(object):
    """
    تغليف المعاملات الخاصة بطلب الإشعار.
    """
    thrift_spec = (
        None,  # 0
        (1, TType.STRUCT, 'event', [UniversalNotificationEvent, None], None),  # 1
    )
    def __init__(self, event=None):
        self.event = event

    def read(self, iprot):
        # قراءة البيانات المتسلسلة
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.event = UniversalNotificationEvent()
                    self.event.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        # كتابة البيانات لإرسالها
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('notify_args')
        if self.event is not None:
            oprot.writeFieldBegin('event', TType.STRUCT, 1)
            self.event.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()
