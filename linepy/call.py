# -*- coding: utf-8 -*-
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
import json

class GroupProtection:
    def __init__(self, channel_token, channel_secret):
        self.api = LineBotApi(channel_token)
        self.handler = WebhookHandler(channel_secret)
        self.admins = []  # قائمة الأدمنات
        self.banned = []  # قائمة المحظورين
        self.protected_groups = []  # القروبات المحمية
        self.auto_kick = True  # طرد تلقائي
        
    # === إدارة الأدمنات ===
    def add_admin(self, user_id):
        """إضافة أدمن"""
        if user_id not in self.admins:
            self.admins.append(user_id)
            return "✅ تم إضافة الأدمن"
        return "⚠️ موجود مسبقاً"
    
    def remove_admin(self, user_id):
        """حذف أدمن"""
        if user_id in self.admins:
            self.admins.remove(user_id)
            return "✅ تم حذف الأدمن"
        return "⚠️ غير موجود"
    
    def is_admin(self, user_id):
        """فحص صلاحية الأدمن"""
        return user_id in self.admins
    
    # === إدارة الحظر ===
    def ban_user(self, user_id):
        """حظر عضو"""
        if user_id not in self.banned:
            self.banned.append(user_id)
            return "🚫 تم حظر العضو"
        return "⚠️ محظور مسبقاً"
    
    def unban_user(self, user_id):
        """إلغاء حظر عضو"""
        if user_id in self.banned:
            self.banned.remove(user_id)
            return "✅ تم إلغاء الحظر"
        return "⚠️ غير محظور"
    
    def is_banned(self, user_id):
        """فحص حالة الحظر"""
        return user_id in self.banned
    
    # === إدارة القروبات ===
    def protect_group(self, group_id):
        """تفعيل حماية القروب"""
        if group_id not in self.protected_groups:
            self.protected_groups.append(group_id)
            return "🛡️ تم تفعيل الحماية"
        return "⚠️ الحماية مفعلة مسبقاً"
    
    def unprotect_group(self, group_id):
        """إيقاف حماية القروب"""
        if group_id in self.protected_groups:
            self.protected_groups.remove(group_id)
            return "✅ تم إيقاف الحماية"
        return "⚠️ الحماية غير مفعلة"
    
    def is_protected(self, group_id):
        """فحص حماية القروب"""
        return group_id in self.protected_groups
    
    # === إجراءات الحماية ===
    def kick_member(self, group_id, user_id):
        """طرد عضو من القروب"""
        try:
            self.api.leave_group(group_id) if user_id == self.api.get_bot_info().user_id else None
            return "✅ تم الطرد"
        except:
            return "❌ فشل الطرد"
    
    def get_group_members(self, group_id):
        """جلب أعضاء القروب"""
        try:
            members = []
            start = None
            while True:
                result = self.api.get_group_member_ids(group_id, start)
                members.extend(result.member_ids)
                start = result.next
                if not start:
                    break
            return members
        except:
            return []
    
    def get_member_profile(self, group_id, user_id):
        """جلب بروفايل العضو"""
        try:
            return self.api.get_group_member_profile(group_id, user_id)
        except:
            return None
    
    # === معالجة الأحداث ===
    def handle_join(self, event):
        """معالجة انضمام عضو"""
        group_id = event.source.group_id
        user_id = event.joined.members[0].user_id
        
        if self.is_protected(group_id) and self.is_banned(user_id):
            if self.auto_kick:
                self.kick_member(group_id, user_id)
                return "🚫 تم طرد عضو محظور"
        
        return f"👋 مرحباً بالعضو الجديد"
    
    def handle_leave(self, event):
        """معالجة مغادرة عضو"""
        return "👋 مع السلامة"
    
    # === الأوامر ===
    def process_command(self, event, text, user_id, group_id):
        """معالجة الأوامر"""
        
        # التحقق من صلاحية الأدمن
        if not self.is_admin(user_id):
            return "⛔ هذا الأمر للأدمنات فقط"
        
        cmd = text.lower().split()
        
        # أوامر الحماية
        if cmd[0] == "protect":
            return self.protect_group(group_id)
        
        elif cmd[0] == "unprotect":
            return self.unprotect_group(group_id)
        
        # أوامر الحظر
        elif cmd[0] == "ban" and len(cmd) > 1:
            return self.ban_user(cmd[1])
        
        elif cmd[0] == "unban" and len(cmd) > 1:
            return self.unban_user(cmd[1])
        
        # أوامر الأدمنات
        elif cmd[0] == "addadmin" and len(cmd) > 1:
            return self.add_admin(cmd[1])
        
        elif cmd[0] == "removeadmin" and len(cmd) > 1:
            return self.remove_admin(cmd[1])
        
        # أوامر الأعضاء
        elif cmd[0] == "kick" and len(cmd) > 1:
            return self.kick_member(group_id, cmd[1])
        
        elif cmd[0] == "members":
            members = self.get_group_members(group_id)
            return f"👥 عدد الأعضاء: {len(members)}"
        
        elif cmd[0] == "status":
            protected = "🛡️ مفعلة" if self.is_protected(group_id) else "❌ معطلة"
            return f"الحماية: {protected}\nالأدمنات: {len(self.admins)}\nالمحظورين: {len(self.banned)}"
        
        return "❓ أمر غير معروف"

# الاستخدام
# bot = GroupProtection('YOUR_CHANNEL_TOKEN', 'YOUR_CHANNEL_SECRET')
