# -*- coding: utf-8 -*-
from linebot import LineBotApi, WebhookHandler
from config import Config
from models import Models

class Bot(Models):
    def __init__(self, token, secret):
        self.api = LineBotApi(token)
        self.handler = WebhookHandler(secret)
        self.cfg = Config(token, secret)

        self.admins = []
        self.banned = []
        self.protected = []

        self.data_file = 'bot_data.json'
        self.load_data()

    # ========= البيانات =========
    def save_data(self):
        data = {
            'admins': self.admins,
            'banned': self.banned,
            'protected': self.protected
        }
        self.save(self.data_file, data)
        self.log("💾 حفظ البيانات")

    def load_data(self):
        data = self.load(self.data_file)
        self.admins = data.get('admins', [])
        self.banned = data.get('banned', [])
        self.protected = data.get('protected', [])
        self.log("📂 تحميل البيانات")

    # ========= التحقق =========
    def is_admin(self, uid):
        return uid in self.admins

    def is_banned(self, uid):
        return uid in self.banned

    def is_protected(self, gid):
        return gid in self.protected

    # ========= الأدمن =========
    def addadmin(self, uid):
        if uid not in self.admins:
            self.admins.append(uid)
            self.save_data()
            return "✅ أضيف أدمن"
        return "⚠️ موجود"

    def deladmin(self, uid):
        if uid in self.admins:
            self.admins.remove(uid)
            self.save_data()
            return "✅ حذف أدمن"
        return "⚠️ غير موجود"

    # ========= الحظر =========
    def ban(self, uid):
        if uid not in self.banned:
            self.banned.append(uid)
            self.save_data()
            return "🚫 حظر"
        return "⚠️ محظور مسبقًا"

    def unban(self, uid):
        if uid in self.banned:
            self.banned.remove(uid)
            self.save_data()
            return "✅ فك الحظر"
        return "⚠️ غير محظور"

    # ========= الحماية =========
    def protect(self, gid):
        if gid not in self.protected:
            self.protected.append(gid)
            self.save_data()
            return "🛡️ الحماية مفعلة"
        return "⚠️ الحماية مفعلة مسبقًا"

    def unprotect(self, gid):
        if gid in self.protected:
            self.protected.remove(gid)
            self.save_data()
            return "❌ تم إيقاف الحماية"
        return "⚠️ الحماية غير مفعلة"

    # ========= الأعضاء =========
    def kick(self, gid, uid):
        try:
            self.api.leave_group(gid)
            self.log(f"👢 طرد {uid}")
            return "✅ تم الطرد"
        except Exception as e:
            self.log(f"❌ خطأ: {e}")
            return "❌ فشل الطرد"

    def members(self, gid):
        try:
            members, start = [], None
            while True:
                r = self.api.get_group_member_ids(gid, start)
                members.extend(r.member_ids)
                if not r.next:
                    break
                start = r.next
            return members
        except:
            return []

    # ========= الأحداث =========
    def on_join(self, gid, uid):
        if self.is_protected(gid) and self.is_banned(uid):
            self.kick(gid, uid)
            return "🚫 طرد محظور"
        return "👋 أهلاً وسهلاً"

    def on_leave(self, gid, uid):
        self.log(f"👋 غادر {uid}")
        return "مع السلامة"

    # ========= الأوامر =========
    def cmd(self, txt, uid, gid):
        if not self.is_admin(uid):
            return "⛔ هذا الأمر للأدمن فقط"

        c = txt.lower().split()
        if not c:
            return "❓ أمر فارغ"

        cmds = {
            'protect': lambda: self.protect(gid),
            'unprotect': lambda: self.unprotect(gid),
            'ban': lambda: self.ban(c[1]) if len(c) > 1 else "❓ ban [id]",
            'unban': lambda: self.unban(c[1]) if len(c) > 1 else "❓ unban [id]",
            'addadmin': lambda: self.addadmin(c[1]) if len(c) > 1 else "❓ addadmin [id]",
            'deladmin': lambda: self.deladmin(c[1]) if len(c) > 1 else "❓ deladmin [id]",
            'kick': lambda: self.kick(gid, c[1]) if len(c) > 1 else "❓ kick [id]",
            'members': lambda: f"👥 الأعضاء: {len(self.members(gid))}",
            'admins': lambda: f"👮 الأدمنات: {len(self.admins)}",
            'banned': lambda: f"🚫 المحظورين: {len(self.banned)}",
            'status': lambda: (
                f"🛡️ الحماية: {'✅' if self.is_protected(gid) else '❌'}\n"
                f"👮 أدمنات: {len(self.admins)}\n"
                f"🚫 محظورين: {len(self.banned)}\n"
                f"👥 أعضاء: {len(self.members(gid))}"
            )
        }

        result = cmds.get(c[0], lambda: "❓ أمر غير معروف")()
        self.log(f"⚡ أمر: {c[0]} من {uid}")
        return result
        # -*- coding: utf-8 -*-
from bot import Bot

TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
SECRET = "YOUR_CHANNEL_SECRET"

bot = Bot(TOKEN, SECRET)

# مثال
# bot.addadmin("USER_ID")
# print(bot.cmd("protect", "USER_ID", "GROUP_ID"))
