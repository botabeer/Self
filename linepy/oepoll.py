# -*- coding: utf-8 -*-
from .client import LINE
from types import *

import os, sys, threading, time

class OEPoll(object):
    """
    فئة الاستطلاع للعمليات (Operation Poll)
    تستخدم لاستقبال ومعالجة العمليات الواردة من خادم LINE
    """
    OpInterrupt = {}
    client = None
    __squareSubId = {}
    __squareSyncToken = {}

    def __init__(self, client):
        """
        تهيئة فئة الاستطلاع
        
        المعاملات:
            client: كائن عميل LINE
        """
        if type(client) is not LINE:
            raise Exception('You need to set LINE instance to initialize OEPoll')
        self.client = client
    
    def __fetchOperation(self, revision, count=1):
        """
        جلب العمليات من الخادم
        
        المعاملات:
            revision: رقم المراجعة
            count: عدد العمليات المطلوب جلبها
        
        العائد:
            قائمة العمليات
        """
        return self.client.poll.fetchOperations(revision, count)
    
    def __execute(self, op, threading):
        """
        تنفيذ معالج العملية
        
        المعاملات:
            op: كائن العملية
            threading: تفعيل المعالجة بخيوط متعددة
        """
        try:
            if threading:
                _td = threading.Thread(target=self.OpInterrupt[op.type](op))
                _td.daemon = False
                _td.start()
            else:
                self.OpInterrupt[op.type](op)
        except Exception as e:
            self.client.log(e)

    def addOpInterruptWithDict(self, OpInterruptDict):
        """
        إضافة معالجات العمليات من قاموس
        
        المعاملات:
            OpInterruptDict: قاموس يحتوي على أنواع العمليات ودوال المعالجة
        """
        self.OpInterrupt.update(OpInterruptDict)

    def addOpInterrupt(self, OperationType, DisposeFunc):
        """
        إضافة معالج لنوع عملية محدد
        
        المعاملات:
            OperationType: نوع العملية
            DisposeFunc: دالة المعالجة
        """
        self.OpInterrupt[OperationType] = DisposeFunc
    
    def setRevision(self, revision):
        """
        تعيين رقم المراجعة
        
        المعاملات:
            revision: رقم المراجعة الجديد
        """
        self.client.revision = max(revision, self.client.revision)

    def singleTrace(self, count=1):
        """
        جلب عمليات لمرة واحدة
        
        المعاملات:
            count: عدد العمليات المطلوب جلبها
        
        العائد:
            قائمة العمليات أو قائمة فارغة
        """
        try:
            operations = self.__fetchOperation(self.client.revision, count=count)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        if operations is None:
            return []
        else:
            return operations

    def trace(self, threading=False):
        """
        تتبع ومعالجة العمليات الواردة
        
        المعاملات:
            threading: تفعيل المعالجة بخيوط متعددة (افتراضي: False)
        """
        try:
            operations = self.__fetchOperation(self.client.revision)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        for op in operations:
            if op.type in self.OpInterrupt.keys():
                self.__execute(op, threading)
            self.setRevision(op.revision)

    def singleFetchSquareChat(self, squareChatMid, limit=1):
        """
        جلب أحداث محادثة المربع (Square Chat) لمرة واحدة
        
        المعاملات:
            squareChatMid: معرف محادثة المربع
            limit: الحد الأقصى لعدد الأحداث
        
        العائد:
            قائمة الأحداث
        """
        if squareChatMid not in self.__squareSubId:
            self.__squareSubId[squareChatMid] = 0
        if squareChatMid not in self.__squareSyncToken:
            self.__squareSyncToken[squareChatMid] = ''
        
        sqcEvents = self.client.fetchSquareChatEvents(squareChatMid, subscriptionId=self.__squareSubId[squareChatMid], syncToken=self.__squareSyncToken[squareChatMid], limit=limit, direction=1)
        self.__squareSubId[squareChatMid] = sqcEvents.subscription
        self.__squareSyncToken[squareChatMid] = sqcEvents.syncToken

        return sqcEvents.events
