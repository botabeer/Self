# -*- coding: utf-8 -*-
from linebot import LineBotApi, WebhookHandler
from linebot.models import *

class GroupProtection:
    def __init__(self, token, secret):
        self.api = LineBotApi(token)
        self.handler = WebhookHandler(secret)
        self.admins = []
        self.banned = []
        self.protected = []
        
    # الأدمنات
    def add_admin(self, uid):
        if uid not in self.admins:
            self.admins.append(uid)
            return "✅ تم إضافة أدمن"
        return "⚠️ موجود"
    
    def del_admin(self, uid):
        if uid in self.admins:
            self.admins.remove(uid)
            return "✅ تم حذف أدمن"
        return "⚠️ غير موجود"
    
    def is_admin(self, uid):
        return uid in self.admins
    
    # الحظر
    def ban(self, uid):
        if uid not in self.banned:
            self.banned.append(uid)
            return "🚫 تم الحظر"
        return "⚠️ محظور"
    
    def unban(self, uid):
        if uid in self.banned:
            self.banned.remove(uid)
            return "✅ تم إلغاء الحظر"
        return "⚠️ غير محظور"
    
    def is_banned(self, uid):
        return uid in self.banned
    
    # الحماية
    def protect(self, gid):
        if gid not in self.protected:
            self.protected.append(gid)
            return "🛡️ تم تفعيل الحماية"
        return "⚠️ مفعلة"
    
    def unprotect(self, gid):
        if gid in self.protected:
            self.protected.remove(gid)
            return "✅ تم إيقاف الحماية"
        return "⚠️ معطلة"
    
    def is_protected(self, gid):
        return gid in self.protected
    
    # الأعضاء
    def kick(self, gid, uid):
        try:
            self.api.leave_group(gid) if uid == self.api.get_bot_info().user_id else None
            return "✅ تم الطرد"
        except:
            return "❌ فشل"
    
    def members(self, gid):
        try:
            m = []
            s = None
            while True:
                r = self.api.get_group_member_ids(gid, s)
                m.extend(r.member_ids)
                s = r.next
                if not s: break
            return m
        except:
            return []
    
    def profile(self, gid, uid):
        try:
            return self.api.get_group_member_profile(gid, uid)
        except:
            return None
    
    # الأحداث
    def on_join(self, gid, uid):
        if self.is_protected(gid) and self.is_banned(uid):
            self.kick(gid, uid)
            return "🚫 طرد محظور"
        return "👋 مرحباً"
    
    # الأوامر
    def cmd(self, txt, uid, gid):
        if not self.is_admin(uid):
            return "⛔ للأدمنات فقط"
        
        c = txt.lower().split()
        
        if c[0] == "protect": return self.protect(gid)
        if c[0] == "unprotect": return self.unprotect(gid)
        if c[0] == "ban" and len(c) > 1: return self.ban(c[1])
        if c[0] == "unban" and len(c) > 1: return self.unban(c[1])
        if c[0] == "addadmin" and len(c) > 1: return self.add_admin(c[1])
        if c[0] == "deladmin" and len(c) > 1: return self.del_admin(c[1])
        if c[0] == "kick" and len(c) > 1: return self.kick(gid, c[1])
        if c[0] == "members": return f"👥 الأعضاء: {len(self.members(gid))}"
        if c[0] == "status":
            p = "🛡️ مفعلة" if self.is_protected(gid) else "❌ معطلة"
            return f"الحماية: {p}\nأدمنات: {len(self.admins)}\nمحظورين: {len(self.banned)}"
        
        return "❓ أمر خاطئ"

# bot = GroupProtection('TOKEN', 'SECRET')
