# ShopService.py - LINE Shop API (Simplified & Compressed)
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
from thrift.TProcessor import TProcessor
from thrift.transport import TTransport
import sys
import logging
from .ttypes import *

all_structs = []

class Iface:
    def getProduct(self, packageID, language, country): pass
    def getProductList(self, productIdList, language, country): pass
    def buyFreeProduct(self, receiverMid, productId, messageTemplate, language, country, packageId): pass
    def getTotalBalance(self, appStoreCode): pass
    def reservePayment(self, paymentReservation): pass

class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def getProduct(self, packageID, language, country):
        self.send_getProduct(packageID, language, country)
        return self.recv_getProduct()

    def send_getProduct(self, packageID, language, country):
        self._oprot.writeMessageBegin('getProduct', TMessageType.CALL, self._seqid)
        args = getProduct_args(packageID=packageID, language=language, country=country)
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_getProduct(self):
        (fname, mtype, rseqid) = self._iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.readMessageEnd()
            raise x
        result = getProduct_result()
        result.read(self._iprot)
        self._iprot.readMessageEnd()
        if result.success: return result.success
        if result.e: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getProduct failed")

    def buyFreeProduct(self, receiverMid, productId, messageTemplate, language, country, packageId):
        self.send_buyFreeProduct(receiverMid, productId, messageTemplate, language, country, packageId)
        self.recv_buyFreeProduct()

    def send_buyFreeProduct(self, receiverMid, productId, messageTemplate, language, country, packageId):
        self._oprot.writeMessageBegin('buyFreeProduct', TMessageType.CALL, self._seqid)
        args = buyFreeProduct_args(receiverMid, productId, messageTemplate, language, country, packageId)
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_buyFreeProduct(self):
        (fname, mtype, rseqid) = self._iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.readMessageEnd()
            raise x
        result = buyFreeProduct_result()
        result.read(self._iprot)
        self._iprot.readMessageEnd()
        if result.e: raise result.e

class Processor(Iface, TProcessor):
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "getProduct": Processor.process_getProduct,
            "buyFreeProduct": Processor.process_buyFreeProduct,
            "getTotalBalance": Processor.process_getTotalBalance
        }

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, f'Unknown function {name}')
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        self._processMap[name](self, seqid, iprot, oprot)
        return True

# Struct Definitions (Compressed)
class getProduct_args:
    def __init__(self, packageID=None, language=None, country=None):
        self.packageID = packageID
        self.language = language
        self.country = country
    
    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 2 and ftype == TType.I64: self.packageID = iprot.readI64()
            elif fid == 3 and ftype == TType.STRING: self.language = iprot.readString().decode('utf-8')
            elif fid == 4 and ftype == TType.STRING: self.country = iprot.readString().decode('utf-8')
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('getProduct_args')
        if self.packageID: oprot.writeFieldBegin('packageID', TType.I64, 2); oprot.writeI64(self.packageID); oprot.writeFieldEnd()
        if self.language: oprot.writeFieldBegin('language', TType.STRING, 3); oprot.writeString(self.language.encode('utf-8')); oprot.writeFieldEnd()
        if self.country: oprot.writeFieldBegin('country', TType.STRING, 4); oprot.writeString(self.country.encode('utf-8')); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getProduct_args)

class getProduct_result:
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 0 and ftype == TType.STRUCT: self.success = Product(); self.success.read(iprot)
            elif fid == 1 and ftype == TType.STRUCT: self.e = TalkException(); self.e.read(iprot)
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('getProduct_result')
        if self.success: oprot.writeFieldBegin('success', TType.STRUCT, 0); self.success.write(oprot); oprot.writeFieldEnd()
        if self.e: oprot.writeFieldBegin('e', TType.STRUCT, 1); self.e.write(oprot); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getProduct_result)

class buyFreeProduct_args:
    def __init__(self, receiverMid=None, productId=None, messageTemplate=None, language=None, country=None, packageId=None):
        self.receiverMid = receiverMid
        self.productId = productId
        self.messageTemplate = messageTemplate
        self.language = language
        self.country = country
        self.packageId = packageId

    def write(self, oprot):
        oprot.writeStructBegin('buyFreeProduct_args')
        if self.receiverMid: oprot.writeFieldBegin('receiverMid', TType.STRING, 2); oprot.writeString(self.receiverMid.encode('utf-8')); oprot.writeFieldEnd()
        if self.productId: oprot.writeFieldBegin('productId', TType.STRING, 3); oprot.writeString(self.productId.encode('utf-8')); oprot.writeFieldEnd()
        if self.messageTemplate: oprot.writeFieldBegin('messageTemplate', TType.I32, 4); oprot.writeI32(self.messageTemplate); oprot.writeFieldEnd()
        if self.language: oprot.writeFieldBegin('language', TType.STRING, 5); oprot.writeString(self.language.encode('utf-8')); oprot.writeFieldEnd()
        if self.country: oprot.writeFieldBegin('country', TType.STRING, 6); oprot.writeString(self.country.encode('utf-8')); oprot.writeFieldEnd()
        if self.packageId: oprot.writeFieldBegin('packageId', TType.I64, 7); oprot.writeI64(self.packageId); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(buyFreeProduct_args)

class buyFreeProduct_result:
    def __init__(self, e=None):
        self.e = e

    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 1 and ftype == TType.STRUCT: self.e = TalkException(); self.e.read(iprot)
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('buyFreeProduct_result')
        if self.e: oprot.writeFieldBegin('e', TType.STRUCT, 1); self.e.write(oprot); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(buyFreeProduct_result)

fix_spec(all_structs)
del all_structs
