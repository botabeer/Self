from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport

all_structs = []

class Iface(object):
    # Group Management
    def getGroupMemberMids(self, groupId): pass
    def getGroupsForChannel(self, groupIds): pass
    def getJoinedGroupIdsForChannel(self): pass
    def isGroupMember(self, groupId): pass
    
    # Contact Management
    def findContactByUseridWithoutAbuseBlockForChannel(self, userid): pass
    def getAllContactIdsForChannel(self): pass
    def getContactsForChannel(self, ids): pass
    def getSimpleChannelContacts(self, ids): pass
    def isInContact(self, mid): pass
    
    # Messaging
    def sendMessageForChannel(self, message): pass
    
    # Operations
    def addOperationForChannel(self, opType, param1, param2, param3): pass

class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    # Group Methods
    def getGroupMemberMids(self, groupId):
        self.send_getGroupMemberMids(groupId)
        return self.recv_getGroupMemberMids()
    
    def send_getGroupMemberMids(self, groupId):
        self._oprot.writeMessageBegin('getGroupMemberMids', TMessageType.CALL, self._seqid)
        args = getGroupMemberMids_args()
        args.groupId = groupId
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_getGroupMemberMids(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = getGroupMemberMids_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getGroupMemberMids failed")

    def getGroupsForChannel(self, groupIds):
        self.send_getGroupsForChannel(groupIds)
        return self.recv_getGroupsForChannel()
    
    def send_getGroupsForChannel(self, groupIds):
        self._oprot.writeMessageBegin('getGroupsForChannel', TMessageType.CALL, self._seqid)
        args = getGroupsForChannel_args()
        args.groupIds = groupIds
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_getGroupsForChannel(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = getGroupsForChannel_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "getGroupsForChannel failed")

    def isGroupMember(self, groupId):
        self.send_isGroupMember(groupId)
        return self.recv_isGroupMember()
    
    def send_isGroupMember(self, groupId):
        self._oprot.writeMessageBegin('isGroupMember', TMessageType.CALL, self._seqid)
        args = isGroupMember_args()
        args.groupId = groupId
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_isGroupMember(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = isGroupMember_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "isGroupMember failed")

    # Contact Methods
    def isInContact(self, mid):
        self.send_isInContact(mid)
        return self.recv_isInContact()
    
    def send_isInContact(self, mid):
        self._oprot.writeMessageBegin('isInContact', TMessageType.CALL, self._seqid)
        args = isInContact_args()
        args.mid = mid
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_isInContact(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = isInContact_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "isInContact failed")

    # Message Method
    def sendMessageForChannel(self, message):
        self.send_sendMessageForChannel(message)
        return self.recv_sendMessageForChannel()
    
    def send_sendMessageForChannel(self, message):
        self._oprot.writeMessageBegin('sendMessageForChannel', TMessageType.CALL, self._seqid)
        args = sendMessageForChannel_args()
        args.message = message
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_sendMessageForChannel(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = sendMessageForChannel_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "sendMessageForChannel failed")

    # Operation Method
    def addOperationForChannel(self, opType, param1, param2, param3):
        self.send_addOperationForChannel(opType, param1, param2, param3)
        self.recv_addOperationForChannel()
    
    def send_addOperationForChannel(self, opType, param1, param2, param3):
        self._oprot.writeMessageBegin('addOperationForChannel', TMessageType.CALL, self._seqid)
        args = addOperationForChannel_args()
        args.opType = opType
        args.param1 = param1
        args.param2 = param2
        args.param3 = param3
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()
    
    def recv_addOperationForChannel(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = addOperationForChannel_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.e is not None: raise result.e
        return

# Struct definitions (compact version - only essential fields)
class getGroupMemberMids_args(object):
    def __init__(self, groupId=None):
        self.groupId = groupId
    thrift_spec = (None, (1, TType.STRING, 'groupId', 'UTF8', None))

class getGroupMemberMids_result(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e
    thrift_spec = ((0, TType.LIST, 'success', (TType.STRING, 'UTF8', False), None), (1, TType.STRUCT, 'e', [TalkException, None], None))

class isGroupMember_args(object):
    def __init__(self, groupId=None):
        self.groupId = groupId
    thrift_spec = (None, (1, TType.STRING, 'groupId', 'UTF8', None))

class isGroupMember_result(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e
    thrift_spec = ((0, TType.BOOL, 'success', None, None), (1, TType.STRUCT, 'e', [TalkException, None], None))

class sendMessageForChannel_args(object):
    def __init__(self, message=None):
        self.message = message
    thrift_spec = (None, None, (2, TType.STRUCT, 'message', [Message, None], None))

class sendMessageForChannel_result(object):
    def __init__(self, success=None, e=None):
        self.success = success
        self.e = e
    thrift_spec = ((0, TType.STRUCT, 'success', [Message, None], None), (1, TType.STRUCT, 'e', [TalkException, None], None))

fix_spec(all_structs)
