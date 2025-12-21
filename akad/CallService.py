# -*- coding: utf-8 -*-
from linethrift.ttypes import *
from akad.ttypes import OpType
import time, json

class GroupProtection:
    def __init__(self, client):
        self.cl = client
        self.mid = self.cl.profile.mid
        # إعدادات الحماية
        self.protection = {
            'invite': True,     # حماية من الدعوات
            'kick': True,       # حماية من الطرد
            'cancel': True,     # حماية من الإلغاء
            'url': False,       # حماية من الروابط
            'mention': False,   # حماية من المنشن
            'join': True        # حماية من الانضمام
        }
        self.protected_groups = []  # القروبات المحمية
        self.admins = []            # المشرفين
        self.blacklist = []         # القائمة السوداء
        
    # === إدارة القروبات ===
    def getGroups(self):
        """جلب جميع القروبات"""
        return self.cl.getGroupIdsJoined()
    
    def getGroup(self, gid):
        """جلب معلومات قروب"""
        return self.cl.getGroup(gid)
    
    def getMembers(self, gid):
        """جلب أعضاء القروب"""
        g = self.cl.getGroup(gid)
        return [m.mid for m in g.members]
    
    def inviteToGroup(self, gid, mids):
        """دعوة للقروب"""
        if type(mids) != list:
            mids = [mids]
        for mid in mids:
            self.cl.inviteIntoGroup(gid, [mid])
            
    def kickFromGroup(self, gid, mids):
        """طرد من القروب"""
        if type(mids) != list:
            mids = [mids]
        for mid in mids:
            self.cl.kickoutFromGroup(gid, [mid])
            
    def leaveGroup(self, gid):
        """مغادرة القروب"""
        self.cl.leaveGroup(gid)
    
    # === إدارة الحماية ===
    def protectGroup(self, gid):
        """تفعيل حماية القروب"""
        if gid not in self.protected_groups:
            self.protected_groups.append(gid)
            return True
        return False
    
    def unprotectGroup(self, gid):
        """إلغاء حماية القروب"""
        if gid in self.protected_groups:
            self.protected_groups.remove(gid)
            return True
        return False
    
    def addAdmin(self, mid):
        """إضافة مشرف"""
        if mid not in self.admins:
            self.admins.append(mid)
            return True
        return False
    
    def removeAdmin(self, mid):
        """حذف مشرف"""
        if mid in self.admins:
            self.admins.remove(mid)
            return True
        return False
    
    def addBlacklist(self, mid):
        """إضافة للقائمة السوداء"""
        if mid not in self.blacklist:
            self.blacklist.append(mid)
            return True
        return False
    
    def removeBlacklist(self, mid):
        """حذف من القائمة السوداء"""
        if mid in self.blacklist:
            self.blacklist.remove(mid)
            return True
        return False
    
    # === معالج العمليات ===
    def handleOperation(self, op):
        """معالجة العمليات للحماية"""
        if op.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
            self._handleInvite(op)
        elif op.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            self._handleKick(op)
        elif op.type == OpType.NOTIFIED_CANCEL_INVITATION_GROUP:
            self._handleCancel(op)
        elif op.type == OpType.RECEIVE_MESSAGE:
            self._handleMessage(op)
            
    def _handleInvite(self, op):
        """معالجة الدعوة"""
        gid = op.param1
        if gid not in self.protected_groups:
            return
            
        inviter = op.param2
        invited = op.param3
        
        # التحقق من القائمة السوداء
        if invited in self.blacklist:
            self.kickFromGroup(gid, [invited])
            return
            
        # التحقق من الصلاحية
        if self.protection['invite'] and inviter not in self.admins and inviter != self.mid:
            self.kickFromGroup(gid, [invited])
            self.kickFromGroup(gid, [inviter])
    
    def _handleKick(self, op):
        """معالجة الطرد"""
        gid = op.param1
        if gid not in self.protected_groups:
            return
            
        kicker = op.param2
        kicked = op.param3
        
        # الحماية من الطرد
        if self.protection['kick'] and kicked in self.admins:
            if kicker not in self.admins and kicker != self.mid:
                self.kickFromGroup(gid, [kicker])
                self.inviteToGroup(gid, [kicked])
    
    def _handleCancel(self, op):
        """معالجة إلغاء الدعوة"""
        gid = op.param1
        if gid not in self.protected_groups:
            return
            
        canceler = op.param2
        
        if self.protection['cancel'] and canceler not in self.admins and canceler != self.mid:
            self.kickFromGroup(gid, [canceler])
    
    def _handleMessage(self, op):
        """معالجة الرسائل"""
        msg = op.message
        if msg.toType != 2:  # ليس في قروب
            return
            
        gid = msg.to
        if gid not in self.protected_groups:
            return
        
        sender = msg._from
        text = msg.text
        
        # حماية من الروابط
        if self.protection['url'] and sender not in self.admins and sender != self.mid:
            if 'http://' in text or 'https://' in text:
                self.kickFromGroup(gid, [sender])
                return
        
        # حماية من المنشن الجماعي
        if self.protection['mention'] and sender not in self.admins and sender != self.mid:
            if msg.contentMetadata:
                mentions = msg.contentMetadata.get('MENTION')
                if mentions:
                    mention_list = json.loads(mentions)
                    if len(mention_list['MENTIONEES']) > 5:
                        self.kickFromGroup(gid, [sender])
    
    # === الأوامر ===
    def processCommand(self, msg):
        """معالجة الأوامر"""
        if msg._from not in self.admins and msg._from != self.mid:
            return
            
        cmd = msg.text.lower()
        gid = msg.to if msg.toType == 2 else None
        
        # أوامر الحماية
        if cmd == 'protect on' and gid:
            if self.protectGroup(gid):
                self.cl.sendMessage(gid, "✅ تم تفعيل الحماية")
                
        elif cmd == 'protect off' and gid:
            if self.unprotectGroup(gid):
                self.cl.sendMessage(gid, "❌ تم إلغاء الحماية")
                
        elif cmd.startswith('protect '):
            parts = cmd.split()
            if len(parts) == 3 and gid:
                ptype = parts[1]
                status = parts[2] == 'on'
                if ptype in self.protection:
                    self.protection[ptype] = status
                    self.cl.sendMessage(gid, f"{'✅' if status else '❌'} حماية {ptype}")
                    
        # أوامر المشرفين
        elif cmd == 'admins' and gid:
            admin_list = '\n'.join([f"• {self.cl.getContact(a).displayName}" for a in self.admins])
            self.cl.sendMessage(gid, f"👥 المشرفين:\n{admin_list}")
            
        elif cmd.startswith('admin add') and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            for m in mentions.get('MENTIONEES', []):
                if self.addAdmin(m['M']):
                    self.cl.sendMessage(gid, f"✅ تمت إضافة مشرف")
                    
        elif cmd.startswith('admin remove') and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            for m in mentions.get('MENTIONEES', []):
                if self.removeAdmin(m['M']):
                    self.cl.sendMessage(gid, f"❌ تم حذف مشرف")
                    
        # أوامر القائمة السوداء
        elif cmd.startswith('ban') and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            for m in mentions.get('MENTIONEES', []):
                self.addBlacklist(m['M'])
                if gid:
                    self.kickFromGroup(gid, [m['M']])
            self.cl.sendMessage(gid or msg._from, "🚫 تم الحظر")
            
        elif cmd.startswith('unban') and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            for m in mentions.get('MENTIONEES', []):
                self.removeBlacklist(m['M'])
            self.cl.sendMessage(gid or msg._from, "✅ تم إلغاء الحظر")
            
        # أوامر إدارة القروب
        elif cmd.startswith('kick') and gid and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            mids = [m['M'] for m in mentions.get('MENTIONEES', [])]
            self.kickFromGroup(gid, mids)
            
        elif cmd.startswith('invite') and gid and msg.contentMetadata:
            mentions = json.loads(msg.contentMetadata.get('MENTION', '{}'))
            mids = [m['M'] for m in mentions.get('MENTIONEES', [])]
            self.inviteToGroup(gid, mids)
            
        elif cmd == 'leave' and gid:
            self.cl.sendMessage(gid, "👋 وداعاً")
            self.leaveGroup(gid)
            
        elif cmd == 'speed' and gid:
            start = time.time()
            self.cl.sendMessage(gid, "⚡")
            speed = time.time() - start
            self.cl.sendMessage(gid, f"⚡ السرعة: {speed:.3f}s")
            
        elif cmd == 'ginfo' and gid:
            g = self.getGroup(gid)
            info = f"📋 معلومات القروب\n"
            info += f"الاسم: {g.name}\n"
            info += f"الأعضاء: {len(g.members)}\n"
            info += f"المحمي: {'✅' if gid in self.protected_groups else '❌'}"
            self.cl.sendMessage(gid, info)

# === الاستخدام ===
# bot = GroupProtection(client)
# bot.admins.append("YOUR_MID")
# 
# while True:
#     ops = client.fetchOps(localRev, 50)
#     for op in ops:
#         bot.handleOperation(op)
#         if op.type == OpType.RECEIVE_MESSAGE:
#             bot.processCommand(op.message)
#     localRev = max(ops[-1].revision, localRev)
