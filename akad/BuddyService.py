#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BotService - خدمة البوت الأساسية
متوافق مع LINE Messaging API v3
"""

from typing import Dict, List
from datetime import datetime
from linebot.v3.messaging import (MessagingApi, ApiClient, LeaveRequest,
                                   PushMessageRequest, TextMessage)

class BotService:
    """خدمة البوت للقروبات والغرف"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.bot_stats = {
            'groups': set(),
            'rooms': set(),
            'messages_sent': 0,
            'watermarks': {}
        }
    
    def notifyLeaveGroup(self, group_mid: str):
        """
        إشعار بمغادرة البوت للقروب
        
        Args:
            group_mid: معرف القروب
        """
        try:
            # إرسال رسالة وداع
            self.api.push_message(
                PushMessageRequest(
                    to=group_mid,
                    messages=[TextMessage(text="👋 وداعاً! شكراً لاستخدام البوت")]
                )
            )
            
            # مغادرة القروب
            self.api.leave_group(group_mid)
            
            # تحديث الإحصائيات
            self.bot_stats['groups'].discard(group_mid)
            
            print(f"✅ تم مغادرة القروب: {group_mid}")
        except Exception as e:
            print(f"❌ فشل مغادرة القروب: {e}")
    
    def notifyLeaveRoom(self, room_mid: str):
        """
        إشعار بمغادرة البوت للغرفة
        
        Args:
            room_mid: معرف الغرفة
        """
        try:
            # إرسال رسالة وداع
            self.api.push_message(
                PushMessageRequest(
                    to=room_mid,
                    messages=[TextMessage(text="👋 سأغادر الآن، شكراً!")]
                )
            )
            
            # مغادرة الغرفة
            self.api.leave_room(room_mid)
            
            # تحديث الإحصائيات
            self.bot_stats['rooms'].discard(room_mid)
            
            print(f"✅ تم مغادرة الغرفة: {room_mid}")
        except Exception as e:
            print(f"❌ فشل مغادرة الغرفة: {e}")
    
    def getBotUseInfo(self, bot_mid: str) -> dict:
        """
        الحصول على معلومات استخدام البوت
        
        Args:
            bot_mid: معرف البوت
        
        Returns:
            dict: إحصائيات البوت
        """
        return {
            'botMid': bot_mid,
            'totalGroups': len(self.bot_stats['groups']),
            'totalRooms': len(self.bot_stats['rooms']),
            'messagesSent': self.bot_stats['messages_sent'],
            'isActive': True,
            'uptime': self._calculate_uptime(),
            'lastUpdate': datetime.now().isoformat()
        }
    
    def sendChatCheckedByWatermark(self, seq: int, mid: str, 
                                   watermark: int, session_id: int):
        """
        تسجيل قراءة الرسائل عبر Watermark
        
        Args:
            seq: تسلسل الرسالة
            mid: معرف المحادثة
            watermark: رقم آخر رسالة مقروءة
            session_id: معرف الجلسة
        """
        # تحديث الـ watermark
        if mid not in self.bot_stats['watermarks']:
            self.bot_stats['watermarks'][mid] = []
        
        self.bot_stats['watermarks'][mid].append({
            'seq': seq,
            'watermark': watermark,
            'session': session_id,
            'timestamp': datetime.now().timestamp()
        })
        
        # الاحتفاظ بآخر 100 سجل فقط
        if len(self.bot_stats['watermarks'][mid]) > 100:
            self.bot_stats['watermarks'][mid] = \
                self.bot_stats['watermarks'][mid][-100:]
        
        print(f"📊 Watermark: {mid} | Seq: {seq} | Mark: {watermark}")
    
    def getLastReadMessage(self, mid: str) -> dict:
        """
        الحصول على آخر رسالة مقروءة
        
        Args:
            mid: معرف المحادثة
        
        Returns:
            dict: معلومات آخر رسالة مقروءة
        """
        if mid not in self.bot_stats['watermarks']:
            return {'error': 'لا توجد سجلات'}
        
        last_record = self.bot_stats['watermarks'][mid][-1]
        return {
            'conversationId': mid,
            'lastSeq': last_record['seq'],
            'watermark': last_record['watermark'],
            'timestamp': datetime.fromtimestamp(
                last_record['timestamp']
            ).isoformat()
        }
    
    def joinGroup(self, group_mid: str):
        """تسجيل انضمام البوت لقروب جديد"""
        self.bot_stats['groups'].add(group_mid)
        print(f"➕ انضممت للقروب: {group_mid}")
    
    def joinRoom(self, room_mid: str):
        """تسجيل انضمام البوت لغرفة جديدة"""
        self.bot_stats['rooms'].add(room_mid)
        print(f"➕ انضممت للغرفة: {room_mid}")
    
    def incrementMessageCount(self):
        """زيادة عداد الرسائل المرسلة"""
        self.bot_stats['messages_sent'] += 1
    
    def getGroupList(self) -> List[str]:
        """الحصول على قائمة القروبات"""
        return list(self.bot_stats['groups'])
    
    def getRoomList(self) -> List[str]:
        """الحصول على قائمة الغرف"""
        return list(self.bot_stats['rooms'])
    
    def _calculate_uptime(self) -> str:
        """حساب وقت تشغيل البوت"""
        # هذا مثال بسيط - في الواقع يتم حفظ وقت البدء
        return "online"

# ============ مثال الاستخدام ============
if __name__ == '__main__':
    api = MessagingApi(ApiClient())
    service = BotService(api)
    
    # محاكاة انضمام لقروبات
    service.joinGroup('G1234567890')
    service.joinGroup('G0987654321')
    
    # الحصول على معلومات البوت
    info = service.getBotUseInfo('B1234567890')
    print(f"📊 إحصائيات البوت:")
    print(f"   القروبات: {info['totalGroups']}")
    print(f"   الرسائل: {info['messagesSent']}")
    
    # تسجيل قراءة رسالة
    service.sendChatCheckedByWatermark(
        seq=100,
        mid='C1234567890',
        watermark=99,
        session_id=1
    )
    
    # الحصول على آخر رسالة مقروءة
    last_read = service.getLastReadMessage('C1234567890')
    print(f"📖 آخر رسالة مقروءة: Seq {last_read.get('lastSeq')}")
