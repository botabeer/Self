# SnsAdaptorService.py - LINE SNS Integration (Compressed)
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
    def getSnsFriends(self, snsIdType, snsAccessToken, startIdx, limit): pass
    def getSnsMyProfile(self, snsIdType, snsAccessToken): pass
    def postSnsInvitationMessage(self, snsIdType, snsAccessToken, toSnsUserId): pass

class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    def getSnsFriends(self, snsIdType, snsAccessToken, startIdx, limit):
        self.send_getSnsFriends(snsIdType, snsAccessToken, startIdx, limit)
        return self.recv_getSnsFriends()

    def send_getSnsFriends(self, snsIdType, snsAccessToken, startIdx, limit):
        self._oprot.writeMessageBegin('getSnsFriends', TMessageType.CALL, self._seqid)
        args = getSnsFriends_args(snsIdType, snsAccessToken, startIdx, limit)
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_getSnsFriends(self):
        (fname, mtype, rseqid) = self._iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.readMessageEnd()
            raise x
        result = getSnsFriends_result()
        result.read(self._iprot)
        self._iprot.readMessageEnd()
        if result.success: return result.success
        if result.e: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getSnsFriends failed")

    def getSnsMyProfile(self, snsIdType, snsAccessToken):
        self.send_getSnsMyProfile(snsIdType, snsAccessToken)
        return self.recv_getSnsMyProfile()

    def send_getSnsMyProfile(self, snsIdType, snsAccessToken):
        self._oprot.writeMessageBegin('getSnsMyProfile', TMessageType.CALL, self._seqid)
        args = getSnsMyProfile_args(snsIdType, snsAccessToken)
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_getSnsMyProfile(self):
        (fname, mtype, rseqid) = self._iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.readMessageEnd()
            raise x
        result = getSnsMyProfile_result()
        result.read(self._iprot)
        self._iprot.readMessageEnd()
        if result.success: return result.success
        if result.e: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getSnsMyProfile failed")

    def postSnsInvitationMessage(self, snsIdType, snsAccessToken, toSnsUserId):
        self.send_postSnsInvitationMessage(snsIdType, snsAccessToken, toSnsUserId)
        self.recv_postSnsInvitationMessage()

    def send_postSnsInvitationMessage(self, snsIdType, snsAccessToken, toSnsUserId):
        self._oprot.writeMessageBegin('postSnsInvitationMessage', TMessageType.CALL, self._seqid)
        args = postSnsInvitationMessage_args(snsIdType, snsAccessToken, toSnsUserId)
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_postSnsInvitationMessage(self):
        (fname, mtype, rseqid) = self._iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.readMessageEnd()
            raise x
        result = postSnsInvitationMessage_result()
        result.read(self._iprot)
        self._iprot.readMessageEnd()
        if result.e: raise result.e

class Processor(Iface, TProcessor):
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {
            "getSnsFriends": Processor.process_getSnsFriends,
            "getSnsMyProfile": Processor.process_getSnsMyProfile,
            "postSnsInvitationMessage": Processor.process_postSnsInvitationMessage
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

# Structs (Compressed)
class getSnsFriends_args:
    def __init__(self, snsIdType=None, snsAccessToken=None, startIdx=None, limit=None):
        self.snsIdType = snsIdType
        self.snsAccessToken = snsAccessToken
        self.startIdx = startIdx
        self.limit = limit

    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 2 and ftype == TType.I32: self.snsIdType = iprot.readI32()
            elif fid == 3 and ftype == TType.STRING: self.snsAccessToken = iprot.readString().decode('utf-8')
            elif fid == 4 and ftype == TType.I32: self.startIdx = iprot.readI32()
            elif fid == 5 and ftype == TType.I32: self.limit = iprot.readI32()
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('getSnsFriends_args')
        if self.snsIdType: oprot.writeFieldBegin('snsIdType', TType.I32, 2); oprot.writeI32(self.snsIdType); oprot.writeFieldEnd()
        if self.snsAccessToken: oprot.writeFieldBegin('snsAccessToken', TType.STRING, 3); oprot.writeString(self.snsAccessToken.encode('utf-8')); oprot.writeFieldEnd()
        if self.startIdx: oprot.writeFieldBegin('startIdx', TType.I32, 4); oprot.writeI32(self.startIdx); oprot.writeFieldEnd()
        if self.limit: oprot.writeFieldBegin('limit', TType.I32, 5); oprot.writeI32(self.limit); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getSnsFriends_args)

class getSnsFriends_result:
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 0 and ftype == TType.STRUCT: self.success = SnsFriends(); self.success.read(iprot)
            elif fid == 1 and ftype == TType.STRUCT: self.e = TalkException(); self.e.read(iprot)
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('getSnsFriends_result')
        if self.success: oprot.writeFieldBegin('success', TType.STRUCT, 0); self.success.write(oprot); oprot.writeFieldEnd()
        if self.e: oprot.writeFieldBegin('e', TType.STRUCT, 1); self.e.write(oprot); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getSnsFriends_result)

class getSnsMyProfile_args:
    def __init__(self, snsIdType=None, snsAccessToken=None):
        self.snsIdType = snsIdType
        self.snsAccessToken = snsAccessToken

    def write(self, oprot):
        oprot.writeStructBegin('getSnsMyProfile_args')
        if self.snsIdType: oprot.writeFieldBegin('snsIdType', TType.I32, 2); oprot.writeI32(self.snsIdType); oprot.writeFieldEnd()
        if self.snsAccessToken: oprot.writeFieldBegin('snsAccessToken', TType.STRING, 3); oprot.writeString(self.snsAccessToken.encode('utf-8')); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getSnsMyProfile_args)

class getSnsMyProfile_result:
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e

    def read(self, iprot):
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP: break
            if fid == 0 and ftype == TType.STRUCT: self.success = SnsProfile(); self.success.read(iprot)
            elif fid == 1 and ftype == TType.STRUCT: self.e = TalkException(); self.e.read(iprot)
            else: iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        oprot.writeStructBegin('getSnsMyProfile_result')
        if self.success: oprot.writeFieldBegin('success', TType.STRUCT, 0); self.success.write(oprot); oprot.writeFieldEnd()
        if self.e: oprot.writeFieldBegin('e', TType.STRUCT, 1); self.e.write(oprot); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(getSnsMyProfile_result)

class postSnsInvitationMessage_args:
    def __init__(self, snsIdType=None, snsAccessToken=None, toSnsUserId=None):
        self.snsIdType = snsIdType
        self.snsAccessToken = snsAccessToken
        self.toSnsUserId = toSnsUserId

    def write(self, oprot):
        oprot.writeStructBegin('postSnsInvitationMessage_args')
        if self.snsIdType: oprot.writeFieldBegin('snsIdType', TType.I32, 2); oprot.writeI32(self.snsIdType); oprot.writeFieldEnd()
        if self.snsAccessToken: oprot.writeFieldBegin('snsAccessToken', TType.STRING, 3); oprot.writeString(self.snsAccessToken.encode('utf-8')); oprot.writeFieldEnd()
        if self.toSnsUserId: oprot.writeFieldBegin('toSnsUserId', TType.STRING, 4); oprot.writeString(self.toSnsUserId.encode('utf-8')); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(postSnsInvitationMessage_args)

class postSnsInvitationMessage_result:
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
        oprot.writeStructBegin('postSnsInvitationMessage_result')
        if self.e: oprot.writeFieldBegin('e', TType.STRUCT, 1); self.e.write(oprot); oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

all_structs.append(postSnsInvitationMessage_result)

fix_spec(all_structs)
del all_structs
