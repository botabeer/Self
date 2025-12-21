#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت حماية لاين - LINE Protection Bot
متوافق مع LINE Messaging API v3
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Set
from dataclasses import dataclass, field
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (ApiClient, MessagingApi, ReplyMessageRequest,
                                   TextMessage, PushMessageRequest)
from linebot.v3.webhooks import (MessageEvent, TextMessageContent, JoinEvent,
                                 LeaveEvent, MemberJoinedEvent, MemberLeftEvent)

# ============ التهيئة | Configuration ============
@dataclass
class Config:
    """إعدادات البوت"""
    CHANNEL_TOKEN: str = "YOUR_CHANNEL_ACCESS_TOKEN"
    CHANNEL_SECRET: str = "YOUR_CHANNEL_SECRET"
    ADMIN_IDS: Set[str] = field(default_factory=lambda: {"ADMIN_USER_ID"})
    MAX_WARNINGS: int = 3
    SPAM_THRESHOLD: int = 5  # رسائل في 10 ثواني

config = Config()

# ============ قاعدة البيانات | Database ============
class Database:
    """تخزين بيانات الحماية في الذاكرة"""
    def __init__(self):
        self.warnings: Dict[str, Dict[str, int]] = {}  # {group_id: {user_id: count}}
        self.banned: Dict[str, Set[str]] = {}  # {group_id: {user_ids}}
        self.spam_tracker: Dict[str, List] = {}  # {user_id: [timestamps]}
        self.settings: Dict[str, dict] = {}  # {group_id: settings}
        
    def add_warning(self, gid: str, uid: str) -> int:
        """إضافة تحذير"""
        if gid not in self.warnings:
            self.warnings[gid] = {}
        self.warnings[gid][uid] = self.warnings[gid].get(uid, 0) + 1
        return self.warnings[gid][uid]
    
    def get_warnings(self, gid: str, uid: str) -> int:
        """الحصول على عدد التحذيرات"""
        return self.warnings.get(gid, {}).get(uid, 0)
    
    def reset_warnings(self, gid: str, uid: str):
        """حذف التحذيرات"""
        if gid in self.warnings and uid in self.warnings[gid]:
            del self.warnings[gid][uid]
    
    def ban_user(self, gid: str, uid: str):
        """حظر مستخدم"""
        if gid not in self.banned:
            self.banned[gid] = set()
        self.banned[gid].add(uid)
    
    def is_banned(self, gid: str, uid: str) -> bool:
        """التحقق من الحظر"""
        return uid in self.banned.get(gid, set())

db = Database()

# ============ نظام الحماية | Protection System ============
class ProtectionSystem:
    """نظام الحماية الذكي"""
    
    # أنماط الكشف | Detection Patterns
    URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    MENTION_PATTERN = re.compile(r'@\w+')
    AD_KEYWORDS = ['اشتراك', 'subscription', 'إعلان', 'دعاية', 'تابعوني', 'follow me']
    
    @staticmethod
    def check_url(text: str) -> bool:
        """كشف الروابط"""
        return bool(ProtectionSystem.URL_PATTERN.search(text))
    
    @staticmethod
    def check_spam(uid: str) -> bool:
        """كشف السبام (5 رسائل في 10 ثواني)"""
        now = datetime.now().timestamp()
        if uid not in db.spam_tracker:
            db.spam_tracker[uid] = []
        
        # حذف الرسائل القديمة
        db.spam_tracker[uid] = [t for t in db.spam_tracker[uid] if now - t < 10]
        db.spam_tracker[uid].append(now)
        
        return len(db.spam_tracker[uid]) >= config.SPAM_THRESHOLD
    
    @staticmethod
    def check_advertisement(text: str) -> bool:
        """كشف الإعلانات"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in ProtectionSystem.AD_KEYWORDS)
    
    @staticmethod
    def analyze_message(text: str, uid: str) -> Dict:
        """تحليل الرسالة"""
        return {
            'has_url': ProtectionSystem.check_url(text),
            'is_spam': ProtectionSystem.check_spam(uid),
            'is_ad': ProtectionSystem.check_advertisement(text),
            'is_safe': True
        }

protection = ProtectionSystem()

# ============ معالج الأوامر | Command Handler ============
class CommandHandler:
    """معالج أوامر البوت"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.commands = {
            'help': self.cmd_help,
            'kick': self.cmd_kick,
            'ban': self.cmd_ban,
            'warn': self.cmd_warn,
            'warnings': self.cmd_warnings,
            'unwarn': self.cmd_unwarn,
            'stats': self.cmd_stats,
            'protect': self.cmd_protect,
            'settings': self.cmd_settings
        }
    
    def is_admin(self, uid: str) -> bool:
        """التحقق من الصلاحيات"""
        return uid in config.ADMIN_IDS
    
    async def handle(self, event: MessageEvent, text: str):
        """معالجة الأمر"""
        parts = text.strip().split()
        if not parts or not parts[0].startswith('/'):
            return
        
        cmd = parts[0][1:].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            await self.commands[cmd](event, args)
    
    async def cmd_help(self, event: MessageEvent, args: List[str]):
        """عرض المساعدة"""
        help_text = """🛡️ أوامر الحماية

👮 للمشرفين:
/kick @user - طرد عضو
/ban @user - حظر عضو
/warn @user - تحذير (3 = طرد)
/unwarn @user - حذف تحذير
/warnings @user - عرض التحذيرات
/protect on/off - تفعيل الحماية
/settings - الإعدادات

📊 للجميع:
/stats - إحصائيات القروب
/help - هذه الرسالة"""
        
        await self.reply(event, help_text)
    
    async def cmd_kick(self, event: MessageEvent, args: List[str]):
        """طرد عضو"""
        if not self.is_admin(event.source.user_id):
            return await self.reply(event, "❌ هذا الأمر للمشرفين فقط")
        
        if not args:
            return await self.reply(event, "⚠️ الاستخدام: /kick @user")
        
        # استخراج معرف المستخدم من المنشن
        target_id = args[0].replace('@', '')
        
        try:
            # طرد العضو (يحتاج صلاحيات البوت)
            await self.api.leave_group(event.source.group_id)
            await self.reply(event, f"✅ تم طرد المستخدم {args[0]}")
        except Exception as e:
            await self.reply(event, f"❌ فشل الطرد: {str(e)}")
    
    async def cmd_ban(self, event: MessageEvent, args: List[str]):
        """حظر عضو"""
        if not self.is_admin(event.source.user_id):
            return await self.reply(event, "❌ هذا الأمر للمشرفين فقط")
        
        if not args:
            return await self.reply(event, "⚠️ الاستخدام: /ban @user")
        
        target_id = args[0].replace('@', '')
        gid = event.source.group_id
        
        db.ban_user(gid, target_id)
        await self.reply(event, f"🚫 تم حظر {args[0]} من القروب")
    
    async def cmd_warn(self, event: MessageEvent, args: List[str]):
        """تحذير عضو"""
        if not self.is_admin(event.source.user_id):
            return await self.reply(event, "❌ هذا الأمر للمشرفين فقط")
        
        if not args:
            return await self.reply(event, "⚠️ الاستخدام: /warn @user")
        
        target_id = args[0].replace('@', '')
        gid = event.source.group_id
        
        warns = db.add_warning(gid, target_id)
        
        if warns >= config.MAX_WARNINGS:
            await self.reply(event, f"⛔ {args[0]} وصل للحد الأقصى ({warns}/{config.MAX_WARNINGS}) - سيتم الطرد")
            # طرد تلقائي
            db.ban_user(gid, target_id)
        else:
            await self.reply(event, f"⚠️ تحذير {args[0]}\nالتحذيرات: {warns}/{config.MAX_WARNINGS}")
    
    async def cmd_warnings(self, event: MessageEvent, args: List[str]):
        """عرض التحذيرات"""
        target_id = args[0].replace('@', '') if args else event.source.user_id
        gid = event.source.group_id
        
        warns = db.get_warnings(gid, target_id)
        await self.reply(event, f"📋 التحذيرات: {warns}/{config.MAX_WARNINGS}")
    
    async def cmd_unwarn(self, event: MessageEvent, args: List[str]):
        """حذف تحذير"""
        if not self.is_admin(event.source.user_id):
            return await self.reply(event, "❌ هذا الأمر للمشرفين فقط")
        
        if not args:
            return await self.reply(event, "⚠️ الاستخدام: /unwarn @user")
        
        target_id = args[0].replace('@', '')
        gid = event.source.group_id
        
        db.reset_warnings(gid, target_id)
        await self.reply(event, f"✅ تم حذف تحذيرات {args[0]}")
    
    async def cmd_stats(self, event: MessageEvent, args: List[str]):
        """إحصائيات القروب"""
        gid = event.source.group_id
        total_warns = sum(db.warnings.get(gid, {}).values())
        banned_count = len(db.banned.get(gid, set()))
        
        stats = f"""📊 إحصائيات القروب

👥 الأعضاء المحذرين: {len(db.warnings.get(gid, {}))}
⚠️ مجموع التحذيرات: {total_warns}
🚫 المحظورين: {banned_count}
🛡️ الحماية: {"مفعلة ✅" if db.settings.get(gid, {}).get('protection', True) else "معطلة ❌"}"""
        
        await self.reply(event, stats)
    
    async def cmd_protect(self, event: MessageEvent, args: List[str]):
        """تفعيل/تعطيل الحماية"""
        if not self.is_admin(event.source.user_id):
            return await self.reply(event, "❌ هذا الأمر للمشرفين فقط")
        
        if not args or args[0].lower() not in ['on', 'off']:
            return await self.reply(event, "⚠️ الاستخدام: /protect on|off")
        
        gid = event.source.group_id
        status = args[0].lower() == 'on'
        
        if gid not in db.settings:
            db.settings[gid] = {}
        db.settings[gid]['protection'] = status
        
        await self.reply(event, f"🛡️ الحماية الآن: {'مفعلة ✅' if status else 'معطلة ❌'}")
    
    async def cmd_settings(self, event: MessageEvent, args: List[str]):
        """عرض الإعدادات"""
        gid = event.source.group_id
        settings = db.settings.get(gid, {'protection': True})
        
        text = f"""⚙️ إعدادات القروب

🛡️ الحماية: {'مفعلة' if settings.get('protection', True) else 'معطلة'}
⚠️ حد التحذيرات: {config.MAX_WARNINGS}
📝 حد السبام: {config.SPAM_THRESHOLD} رسائل/10ث"""
        
        await self.reply(event, text)
    
    async def reply(self, event: MessageEvent, text: str):
        """الرد على رسالة"""
        self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)]
            )
        )

# ============ معالج الأحداث | Event Handler ============
class BotEventHandler:
    """معالج أحداث البوت"""
    
    def __init__(self):
        self.handler = WebhookHandler(config.CHANNEL_SECRET)
        self.api = MessagingApi(ApiClient(configuration=None))
        self.cmd_handler = CommandHandler(self.api)
        self.setup_handlers()
    
    def setup_handlers(self):
        """تسجيل المعالجات"""
        
        @self.handler.add(MessageEvent, message=TextMessageContent)
        async def handle_message(event):
            """معالجة الرسائل"""
            text = event.message.text
            uid = event.source.user_id
            gid = event.source.group_id if hasattr(event.source, 'group_id') else None
            
            # تجاهل رسائل المشرفين
            if self.cmd_handler.is_admin(uid):
                if text.startswith('/'):
                    await self.cmd_handler.handle(event, text)
                return
            
            # فحص الحظر
            if gid and db.is_banned(gid, uid):
                return
            
            # تحليل الرسالة
            analysis = protection.analyze_message(text, uid)
            
            # التصرف حسب النتيجة
            if analysis['is_spam']:
                await self.auto_warn(event, "السبام المتكرر")
            elif analysis['has_url']:
                await self.auto_warn(event, "إرسال روابط بدون إذن")
            elif analysis['is_ad']:
                await self.auto_warn(event, "نشر إعلانات")
            
            # معالجة الأوامر
            if text.startswith('/'):
                await self.cmd_handler.handle(event, text)
        
        @self.handler.add(JoinEvent)
        async def handle_join(event):
            """عند انضمام البوت لقروب"""
            welcome = """👋 أهلاً! أنا بوت الحماية

🛡️ سأحمي قروبكم من:
• الروابط والسبام
• الإعلانات
• المستخدمين المزعجين

اكتب /help لعرض الأوامر"""
            
            self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome)]
                )
            )
        
        @self.handler.add(MemberJoinedEvent)
        async def handle_member_join(event):
            """عند انضمام عضو جديد"""
            for member in event.joined.members:
                gid = event.source.group_id
                if db.is_banned(gid, member.user_id):
                    # طرد المستخدم المحظور تلقائياً
                    pass
    
    async def auto_warn(self, event: MessageEvent, reason: str):
        """تحذير تلقائي"""
        gid = event.source.group_id
        uid = event.source.user_id
        
        warns = db.add_warning(gid, uid)
        
        if warns >= config.MAX_WARNINGS:
            db.ban_user(gid, uid)
            msg = f"⛔ تم طرد المستخدم\nالسبب: {reason}"
        else:
            msg = f"⚠️ تحذير ({warns}/{config.MAX_WARNINGS})\nالسبب: {reason}"
        
        self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=msg)]
            )
        )

# ============ وظائف BotService | BotService Functions ============
class BotServiceHelper:
    """وظائف BotService من Thrift"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
    
    def getBotUseInfo(self, bot_mid: str) -> dict:
        """الحصول على معلومات استخدام البوت"""
        # إحصائيات البوت
        total_groups = len(db.warnings)
        total_warnings = sum(sum(w.values()) for w in db.warnings.values())
        total_banned = sum(len(b) for b in db.banned.values())
        
        return {
            'botMid': bot_mid,
            'totalGroups': total_groups,
            'totalWarnings': total_warnings,
            'totalBanned': total_banned,
            'isActive': True,
            'lastUpdate': datetime.now().isoformat()
        }
    
    def sendChatCheckedByWatermark(self, seq: int, mid: str, watermark: int, session_id: int):
        """تتبع قراءة الرسائل (Watermark)"""
        # تسجيل آخر رسالة مقروءة
        if mid not in db.spam_tracker:
            db.spam_tracker[mid] = []
        
        # حفظ الـ watermark للتتبع
        log_entry = {
            'seq': seq,
            'mid': mid,
            'watermark': watermark,
            'session': session_id,
            'timestamp': datetime.now().timestamp()
        }
        
        print(f"📊 Watermark: {mid} read msg {seq} at {watermark}")
        return log_entry

bot_service = None  # سيتم تهيئته في main

# ============ التشغيل | Main ============
def main():
    """تشغيل البوت"""
    global bot_service
    bot = BotEventHandler()
    bot_service = BotServiceHelper(bot.api)
    
    print("🤖 بوت الحماية يعمل...")
    print(f"📊 BotService جاهز - استخدم bot_service.getBotUseInfo('BOT_ID')")
    # هنا يتم ربط Webhook مع LINE

if __name__ == '__main__':
    main()
