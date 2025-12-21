#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UniversalNotificationService - نظام الإشعارات الشامل
متوافق مع LINE Messaging API v3
"""

from typing import Dict, Callable, List
from datetime import datetime
from linebot.v3.messaging import (MessagingApi, ApiClient, PushMessageRequest,
                                   TextMessage, FlexMessage, FlexContainer)

class UniversalNotificationService:
    """نظام الإشعارات الموحد"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.handlers: Dict[str, Callable] = {}
        self.notification_log: List[dict] = []
        self._setup_default_handlers()
    
    def notify(self, event: dict):
        """
        إرسال إشعار للحدث
        
        Args:
            event: {
                'type': 'EVENT_TYPE',
                'target': 'user_or_group_id',
                'data': {...}
            }
        """
        event_type = event.get('type', 'UNKNOWN')
        target = event.get('target')
        
        # تسجيل الإشعار
        self._log_notification(event)
        
        # معالجة الحدث
        if event_type in self.handlers:
            try:
                message = self.handlers[event_type](event)
                if message and target:
                    self._send_notification(target, message)
            except Exception as e:
                print(f"❌ خطأ في معالجة الإشعار: {e}")
        else:
            print(f"⚠️ نوع حدث غير معروف: {event_type}")
    
    def register_handler(self, event_type: str, handler: Callable):
        """تسجيل معالج لنوع حدث معين"""
        self.handlers[event_type] = handler
        print(f"✅ تم تسجيل معالج: {event_type}")
    
    def _setup_default_handlers(self):
        """إعداد المعالجات الافتراضية"""
        
        self.handlers['MESSAGE_SENT'] = lambda e: \
            f"📨 رسالة جديدة من {e['data'].get('sender', 'مجهول')}"
        
        self.handlers['MEMBER_JOINED'] = lambda e: \
            f"👋 انضم {e['data'].get('name', 'عضو جديد')} للقروب"
        
        self.handlers['MEMBER_LEFT'] = lambda e: \
            f"👋 غادر {e['data'].get('name', 'عضو')} القروب"
        
        self.handlers['GROUP_CREATED'] = lambda e: \
            f"🎉 تم إنشاء القروب: {e['data'].get('name', 'قروب جديد')}"
        
        self.handlers['USER_WARNED'] = lambda e: \
            f"⚠️ تحذير: {e['data'].get('reason', 'مخالفة القواعد')}"
        
        self.handlers['USER_KICKED'] = lambda e: \
            f"⛔ تم طرد {e['data'].get('user', 'مستخدم')}"
        
        self.handlers['SPAM_DETECTED'] = lambda e: \
            f"🚨 تم كشف سبام: {e['data'].get('count', 0)} رسائل"
        
        self.handlers['URL_BLOCKED'] = lambda e: \
            f"🔗 تم حظر رابط مشبوه"
        
        self.handlers['SYSTEM_ALERT'] = lambda e: \
            f"🔔 تنبيه: {e['data'].get('message', 'تنبيه نظام')}"
    
    def _send_notification(self, target: str, message: str):
        """إرسال الإشعار عبر LINE"""
        try:
            self.api.push_message(
                PushMessageRequest(
                    to=target,
                    messages=[TextMessage(text=message)]
                )
            )
            print(f"✅ تم إرسال الإشعار إلى: {target}")
        except Exception as e:
            print(f"❌ فشل إرسال الإشعار: {e}")
    
    def _log_notification(self, event: dict):
        """تسجيل الإشعار في السجل"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': event.get('type'),
            'target': event.get('target'),
            'data': event.get('data')
        }
        
        self.notification_log.append(log_entry)
        
        # الاحتفاظ بآخر 1000 سجل فقط
        if len(self.notification_log) > 1000:
            self.notification_log = self.notification_log[-1000:]
    
    def get_notification_history(self, limit: int = 50) -> List[dict]:
        """
        الحصول على سجل الإشعارات
        
        Args:
            limit: عدد السجلات المطلوبة
        
        Returns:
            List[dict]: قائمة الإشعارات
        """
        return self.notification_log[-limit:]
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات الإشعارات"""
        event_counts = {}
        for entry in self.notification_log:
            event_type = entry['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'totalNotifications': len(self.notification_log),
            'eventCounts': event_counts,
            'registeredHandlers': len(self.handlers),
            'lastNotification': self.notification_log[-1] if self.notification_log else None
        }
    
    def broadcast(self, targets: List[str], message: str):
        """
        إرسال إشعار جماعي
        
        Args:
            targets: قائمة المستلمين
            message: نص الرسالة
        """
        for target in targets:
            self._send_notification(target, message)
    
    def send_custom_notification(self, target: str, title: str, 
                                 body: str, icon: str = "🔔"):
        """
        إرسال إشعار مخصص
        
        Args:
            target: المستلم
            title: عنوان الإشعار
            body: محتوى الإشعار
            icon: أيقونة الإشعار
        """
        message = f"{icon} {title}\n\n{body}"
        self._send_notification(target, message)

# ============ مثال الاستخدام ============
if __name__ == '__main__':
    api = MessagingApi(ApiClient())
    service = UniversalNotificationService(api)
    
    # إرسال إشعار عضو جديد
    service.notify({
        'type': 'MEMBER_JOINED',
        'target': 'G1234567890',
        'data': {'name': 'أحمد'}
    })
    
    # إرسال تحذير
    service.notify({
        'type': 'USER_WARNED',
        'target': 'U1234567890',
        'data': {'reason': 'إرسال روابط'}
    })
    
    # تسجيل معالج مخصص
    service.register_handler(
        'CUSTOM_EVENT',
        lambda e: f"🎯 حدث مخصص: {e['data'].get('message')}"
    )
    
    # الحصول على الإحصائيات
    stats = service.get_stats()
    print(f"📊 إجمالي الإشعارات: {stats['totalNotifications']}")
    print(f"📝 المعالجات المسجلة: {stats['registeredHandlers']}")
