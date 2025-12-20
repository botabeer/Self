import re
from database import Database
import logging

logger = logging.getLogger(__name__)

class AdminSystem:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
    
    def extract_user_id(self, text):
        pattern = r'U[0-9a-f]{32}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def is_owner(self, user_id):
        return Database.is_owner(user_id)
    
    def is_admin(self, user_id):
        return Database.is_admin(user_id)
    
    def add_owner(self, user_id):
        return Database.add_owner(user_id)
    
    def remove_owner(self, user_id):
        return Database.remove_owner(user_id)
    
    def add_admin(self, user_id):
        return Database.add_admin(user_id)
    
    def remove_admin(self, user_id):
        return Database.remove_admin(user_id)
    
    def get_admins_list(self):
        owners = Database.get_owners()
        admins = Database.get_admins()
        
        text = "قائمة المسؤولين\n\n"
        
        if owners:
            text += "المالكين\n"
            for i, owner in enumerate(owners, 1):
                text += f"{i}. {owner['user_id']}\n"
            text += "\n"
        
        if admins:
            text += "الادمن\n"
            for i, admin in enumerate(admins, 1):
                text += f"{i}. {admin['user_id']}\n"
        
        if not owners and not admins:
            text += "لا يوجد مسؤولين حاليا"
        
        return text
