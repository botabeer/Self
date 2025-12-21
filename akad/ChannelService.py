from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec
import sys, logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport

all_structs = []

class Iface(object):
    # إدارة التوكن والأمان | Token & Security Management
    def issueChannelToken(self, channelId): pass
    def approveChannelAndIssueChannelToken(self, channelId): pass
    def revokeChannel(self, channelId): pass
    
    # الإشعارات | Notifications
    def fetchNotificationItems(self, localRev): pass
    def getNotificationBadgeCount(self, localRev): pass
    def getChannelNotificationSetting(self, channelId, locale): pass
    def updateChannelNotificationSetting(self, setting): pass
    
    # معلومات القنوات | Channel Info
    def getChannelInfo(self, channelId, locale): pass
    def getApprovedChannels(self, lastSynced, locale): pass
    def syncChannelData(self, lastSynced, locale): pass

class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot: self._oprot = oprot
        self._seqid = 0

    # Token Methods
    def issueChannelToken(self, channelId):
        self.send_issueChannelToken(channelId)
        return self.recv_issueChannelToken()
    
    def send_issueChannelToken(self, channelId):
        self._oprot.writeMessageBegin('issueChannelToken', TMessageType.CALL, self._seqid)
        args = issueChannelToken_args(); args.channelId = channelId
        args.write(self._oprot); self._oprot.writeMessageEnd(); self._oprot.trans.flush()
    
    def recv_issueChannelToken(self):
        iprot = self._iprot; (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION: x = TApplicationException(); x.read(iprot); iprot.readMessageEnd(); raise x
        result = issueChannelToken_result(); result.read(iprot); iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "issueChannelToken failed")

    def revokeChannel(self, channelId):
        self.send_revokeChannel(channelId); self.recv_revokeChannel()
    
    def send_revokeChannel(self, channelId):
        self._oprot.writeMessageBegin('revokeChannel', TMessageType.CALL, self._seqid)
        args = revokeChannel_args(); args.channelId = channelId
        args.write(self._oprot); self._oprot.writeMessageEnd(); self._oprot.trans.flush()
    
    def recv_revokeChannel(self):
        iprot = self._iprot; (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION: x = TApplicationException(); x.read(iprot); iprot.readMessageEnd(); raise x
        result = revokeChannel_result(); result.read(iprot); iprot.readMessageEnd()
        if result.e is not None: raise result.e
        return

    # Notification Methods
    def fetchNotificationItems(self, localRev):
        self.send_fetchNotificationItems(localRev)
        return self.recv_fetchNotificationItems()
    
    def send_fetchNotificationItems(self, localRev):
        self._oprot.writeMessageBegin('fetchNotificationItems', TMessageType.CALL, self._seqid)
        args = fetchNotificationItems_args(); args.localRev = localRev
        args.write(self._oprot); self._oprot.writeMessageEnd(); self._oprot.trans.flush()
    
    def recv_fetchNotificationItems(self):
        iprot = self._iprot; (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION: x = TApplicationException(); x.read(iprot); iprot.readMessageEnd(); raise x
        result = fetchNotificationItems_result(); result.read(iprot); iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "fetchNotificationItems failed")

    def updateChannelNotificationSetting(self, setting):
        self.send_updateChannelNotificationSetting(setting); self.recv_updateChannelNotificationSetting()
    
    def send_updateChannelNotificationSetting(self, setting):
        self._oprot.writeMessageBegin('updateChannelNotificationSetting', TMessageType.CALL, self._seqid)
        args = updateChannelNotificationSetting_args(); args.setting = setting
        args.write(self._oprot); self._oprot.writeMessageEnd(); self._oprot.trans.flush()
    
    def recv_updateChannelNotificationSetting(self):
        iprot = self._iprot; (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION: x = TApplicationException(); x.read(iprot); iprot.readMessageEnd(); raise x
        result = updateChannelNotificationSetting_result(); result.read(iprot); iprot.readMessageEnd()
        if result.e is not None: raise result.e
        return

    # Channel Info Methods
    def syncChannelData(self, lastSynced, locale):
        self.send_syncChannelData(lastSynced, locale)
        return self.recv_syncChannelData()
    
    def send_syncChannelData(self, lastSynced, locale):
        self._oprot.writeMessageBegin('syncChannelData', TMessageType.CALL, self._seqid)
        args = syncChannelData_args(); args.lastSynced = lastSynced; args.locale = locale
        args.write(self._oprot); self._oprot.writeMessageEnd(); self._oprot.trans.flush()
    
    def recv_syncChannelData(self):
        iprot = self._iprot; (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION: x = TApplicationException(); x.read(iprot); iprot.readMessageEnd(); raise x
        result = syncChannelData_result(); result.read(iprot); iprot.readMessageEnd()
        if result.success is not None: return result.success
        if result.e is not None: raise result.e
        raise TApplicationException(TApplicationException.MISSING_RESULT, "syncChannelData failed")

# Compact Struct Definitions
class issueChannelToken_args(object):
    def __init__(self, channelId=None): self.channelId = channelId
    thrift_spec = (None, (1, TType.STRING, 'channelId', 'UTF8', None))

class issueChannelToken_result(object):
    def __init__(self, success=None, e=None): self.success = success; self.e = e
    thrift_spec = ((0, TType.STRUCT, 'success', [ChannelToken, None], None), (1, TType.STRUCT, 'e', [ChannelException, None], None))

class revokeChannel_args(object):
    def __init__(self, channelId=None): self.channelId = channelId
    thrift_spec = (None, (1, TType.STRING, 'channelId', 'UTF8', None))

class revokeChannel_result(object):
    def __init__(self, e=None): self.e = e
    thrift_spec = (None, (1, TType.STRUCT, 'e', [ChannelException, None], None))

class fetchNotificationItems_args(object):
    def __init__(self, localRev=None): self.localRev = localRev
    thrift_spec = (None, None, (2, TType.I64, 'localRev', None, None))

class fetchNotificationItems_result(object):
    def __init__(self, success=None, e=None): self.success = success; self.e = e
    thrift_spec = ((0, TType.STRUCT, 'success', [NotificationFetchResult, None], None), (1, TType.STRUCT, 'e', [ChannelException, None], None))

class syncChannelData_args(object):
    def __init__(self, lastSynced=None, locale=None): self.lastSynced = lastSynced; self.locale = locale
    thrift_spec = (None, None, (2, TType.I64, 'lastSynced', None, None), (3, TType.STRING, 'locale', 'UTF8', None))

class syncChannelData_result(object):
    def __init__(self, success=None, e=None): self.success = success; self.e = e
    thrift_spec = ((0, TType.STRUCT, 'success', [ChannelSyncDatas, None], None), (1, TType.STRUCT, 'e', [ChannelException, None], None))

fix_spec(all_structs)
