#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AccountSupervisorService - خدمة إدارة الحسابات الافتراضية
متوافق مع LINE Messaging API v3
"""

import base64
from typing import Dict, Optional
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from linebot.v3.messaging import MessagingApi, ApiClient

class AccountSupervisorService:
    """خدمة إشراف الحسابات الافتراضية"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.rsa_key = RSA.generate(2048)
        self.cipher = PKCS1_OAEP.new(self.rsa_key)
        self.virtual_accounts: Dict[str, dict] = {}
    
    def getRSAKey(self) -> dict:
        """الحصول على مفتاح RSA للتشفير"""
        public_key = self.rsa_key.publickey().export_key()
        return {
            'keyString': base64.b64encode(public_key).decode(),
            'nvalue': str(self.rsa_key.n),
            'evalue': str(self.rsa_key.e)
        }
    
    def registerVirtualAccount(self, locale: str, encrypted_user_id: str, 
                              encrypted_password: str) -> str:
        """تسجيل حساب افتراضي جديد"""
        try:
            # فك تشفير البيانات
            user_id = self._decrypt(encrypted_user_id)
            password = self._decrypt(encrypted_password)
            
            # إنشاء معرف افتراضي
            virtual_mid = f"V{len(self.virtual_accounts):010d}"
            
            # حفظ الحساب
            self.virtual_accounts[virtual_mid] = {
                'userId': user_id,
                'password': password,
                'locale': locale,
                'created': True
            }
            
            return virtual_mid
        except Exception as e:
            raise Exception(f"فشل التسجيل: {str(e)}")
    
    def requestVirtualAccountPasswordChange(self, virtual_mid: str, 
                                           encrypted_user_id: str,
                                           encrypted_old_password: str,
                                           encrypted_new_password: str):
        """تغيير كلمة المرور للحساب الافتراضي"""
        if virtual_mid not in self.virtual_accounts:
            raise Exception("الحساب غير موجود")
        
        try:
            old_pass = self._decrypt(encrypted_old_password)
            new_pass = self._decrypt(encrypted_new_password)
            
            # التحقق من كلمة المرور القديمة
            if self.virtual_accounts[virtual_mid]['password'] != old_pass:
                raise Exception("كلمة المرور القديمة خاطئة")
            
            # تحديث كلمة المرور
            self.virtual_accounts[virtual_mid]['password'] = new_pass
        except Exception as e:
            raise Exception(f"فشل تغيير كلمة المرور: {str(e)}")
    
    def requestVirtualAccountPasswordSet(self, virtual_mid: str,
                                        encrypted_user_id: str,
                                        encrypted_new_password: str):
        """تعيين كلمة مرور جديدة (إعادة تعيين)"""
        if virtual_mid not in self.virtual_accounts:
            raise Exception("الحساب غير موجود")
        
        try:
            new_pass = self._decrypt(encrypted_new_password)
            self.virtual_accounts[virtual_mid]['password'] = new_pass
        except Exception as e:
            raise Exception(f"فشل تعيين كلمة المرور: {str(e)}")
    
    def unregisterVirtualAccount(self, virtual_mid: str):
        """إلغاء تسجيل الحساب الافتراضي"""
        if virtual_mid in self.virtual_accounts:
            del self.virtual_accounts[virtual_mid]
        else:
            raise Exception("الحساب غير موجود")
    
    def notifyEmailConfirmationResult(self, parameter_map: Dict[str, str]):
        """إشعار بنتيجة تأكيد البريد الإلكتروني"""
        email = parameter_map.get('email')
        status = parameter_map.get('status')
        
        if status == 'confirmed':
            print(f"✅ تم تأكيد البريد: {email}")
        else:
            print(f"❌ فشل تأكيد البريد: {email}")
    
    def _decrypt(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except:
            return encrypted_data  # في حالة عدم التشفير

# ============ مثال الاستخدام ============
if __name__ == '__main__':
    api = MessagingApi(ApiClient())
    service = AccountSupervisorService(api)
    
    # الحصول على مفتاح RSA
    rsa_key = service.getRSAKey()
    print("🔑 RSA Key:", rsa_key['keyString'][:50] + "...")
    
    # تسجيل حساب افتراضي
    virtual_mid = service.registerVirtualAccount(
        locale='ar_SA',
        encrypted_user_id='user123',
        encrypted_password='pass123'
    )
    print(f"✅ تم التسجيل: {virtual_mid}")
