# -*- coding: utf-8 -*-
from linebot import LineBotApi, WebhookHandler
from linebot.models import *

class Bot:
    def __init__(self, token, secret):
        self.api = LineBotApi(token)
        self.handler = WebhookHandler(secret)
        self.admins = []
        self.banned = []
        self.protected = []
        self.settings = {}
    
    # التحقق
    def check(self, uid):
        return uid in self.admins
    
    # الأدمنات
    def addadmin(self, uid):
        if uid not in self.admins:
            self.admins.append(uid)
            return "✅ أضيف"
        return "⚠️ موجود"
    
    def deladmin(self, uid):
        if uid in self.admins:
            self.admins.remove(uid)
            return "✅ حذف"
        return "⚠️ مافي"
    
    # الحظر
    def ban(self, uid):
        if uid not in self.banned:
            self.banned.append(uid)
            return "🚫 حظر"
        return "⚠️ محظور"
    
    def unban(self, uid):
        if uid in self.banned:
            self.banned.remove(uid)
            return "✅ ألغي"
        return "⚠️ مو محظور"
    
    # الحماية
    def protect(self, gid):
        if gid not in self.protected:
            self.protected.append(gid)
            return "🛡️ مفعلة"
        return "⚠️ شغالة"
    
    def unprotect(self, gid):
        if gid in self.protected:
            self.protected.remove(gid)
            return "❌ طفت"
        return "⚠️ مطفية"
    
    # الأعضاء
    def kick(self, gid, uid):
        try:
            self.api.leave_group(gid)
            return "✅ طرد"
        except:
            return "❌ خطأ"
    
    def members(self, gid):
        try:
            m, s = [], None
            while True:
                r = self.api.get_group_member_ids(gid, s)
                m.extend(r.member_ids)
                if not r.next: break
                s = r.next
            return m
        except:
            return []
    
    def profile(self, gid, uid):
        try:
            return self.api.get_group_member_profile(gid, uid)
        except:
            return None
    
    # معالجة الانضمام
    def join(self, gid, uid):
        if gid in self.protected and uid in self.banned:
            self.kick(gid, uid)
            return "🚫 طرد محظور"
        return "👋 أهلاً"
    
    # الأوامر
    def cmd(self, t, u, g):
        if not self.check(u): return "⛔ أدمن فقط"
        c = t.lower().split()
        if not c: return "❓"
        
        cmd = {
            "protect": lambda: self.protect(g),
            "unprotect": lambda: self.unprotect(g),
            "ban": lambda: self.ban(c[1]) if len(c)>1 else "❓ ban [id]",
            "unban": lambda: self.unban(c[1]) if len(c)>1 else "❓ unban [id]",
            "addadmin": lambda: self.addadmin(c[1]) if len(c)>1 else "❓ addadmin [id]",
            "deladmin": lambda: self.deladmin(c[1]) if len(c)>1 else "❓ deladmin [id]",
            "kick": lambda: self.kick(g, c[1]) if len(c)>1 else "❓ kick [id]",
            "members": lambda: f"👥 {len(self.members(g))}",
            "status": lambda: f"🛡️ {'✅' if g in self.protected else '❌'}\n👮 {len(self.admins)}\n🚫 {len(self.banned)}"
        }
        
        return cmd.get(c[0], lambda: "❓ أمر خاطئ")()

# bot = Bot('TOKEN', 'SECRET')
