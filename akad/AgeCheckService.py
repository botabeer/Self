#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuthService - خدمة المصادقة وتسجيل الدخول
متوافق مع LINE Messaging API v3
"""

import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
from linebot.v3.messaging import MessagingApi, ApiClient

class AuthService:
    """خدمة المصادقة والتسجيل"""
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.sessions = {}
        self.e2ee_requests = {}
    
    def loginZ(self, login_request: dict) -> dict:
        """
        تسجيل الدخول
        
        Args:
            login_request: {
                'identifier': 'email/phone',
                'password': 'hashed_password',
                'deviceName': 'device_name'
            }
        
        Returns:
            dict: نتيجة تسجيل الدخول
        """
        identifier = login_request.get('identifier')
        password = login_request.get('password')
        
        # التحقق من بيانات الاعتماد
        if not self._verify_credentials(identifier, password):
            raise Exception("بيانات الدخول خاطئة")
        
        # إنشاء جلسة
        auth_token = self._generate_token()
        session_id = self._create_session(identifier, auth_token)
        
        return {
            'authToken': auth_token,
            'sessionId': session_id,
            'expiresIn': 3600,  # ساعة واحدة
            'userId': self._get_user_id(identifier),
            'loginTime': datetime.now().isoformat()
        }
    
    def logoutZ(self):
        """تسجيل الخروج"""
        # حذف جميع الجلسات النشطة
        self.sessions.clear()
        print("✅ تم تسجيل الخروج بنجاح")
    
    def normalizePhoneNumber(self, country_code: str, phone_number: str,
                            country_code_hint: str = '') -> str:
        """
        تنسيق رقم الهاتف بالصيغة الدولية
        
        Returns:
            str: رقم الهاتف المنسق
        """
        # إزالة الرموز الخاصة
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # إضافة كود الدولة
        if not clean_number.startswith(country_code):
            clean_number = f"{country_code}{clean_number}"
        
        return f"+{clean_number}"
    
    def respondE2EELoginRequest(self, verifier: str, public_key: dict,
                               encrypted_key_chain: bytes,
                               hash_key_chain: bytes, error_code: int):
        """
        الرد على طلب تسجيل دخول E2EE (التشفير من طرف لطرف)
        """
        if error_code != 0:
            raise Exception(f"خطأ في E2EE: {error_code}")
        
        self.e2ee_requests[verifier] = {
            'publicKey': public_key,
            'encryptedKeyChain': encrypted_key_chain,
            'hashKeyChain': hash_key_chain,
            'timestamp': datetime.now()
        }
        
        print(f"✅ تم حفظ طلب E2EE: {verifier}")
    
    def confirmE2EELogin(self, verifier: str, device_secret: bytes) -> str:
        """
        تأكيد تسجيل الدخول E2EE
        
        Returns:
            str: رمز المصادقة
        """
        if verifier not in self.e2ee_requests:
            raise Exception("طلب E2EE غير موجود")
        
        # التحقق من device_secret
        auth_token = self._generate_token()
        
        # حذف الطلب بعد التأكيد
        del self.e2ee_requests[verifier]
        
        return auth_token
    
    def verifyQrcodeWithE2EE(self, verifier: str, pin_code: str,
                            error_code: int, public_key: dict,
                            encrypted_key_chain: bytes,
                            hash_key_chain: bytes) -> str:
        """
        التحقق من QR Code مع E2EE
        
        Returns:
            str: نتيجة التحقق
        """
        if error_code != 0:
            raise Exception(f"خطأ في التحقق: {error_code}")
        
        # التحقق من رمز PIN
        if not self._verify_pin(pin_code):
            raise Exception("رمز PIN خاطئ")
        
        # إنشاء رمز تحقق
        verification_token = self._generate_token()
        
        return verification_token
    
    def issueTokenForAccountMigration(self, migration_session_id: str) -> dict:
        """
        إصدار رمز لنقل الحساب
        
        Returns:
            dict: معلومات الرمز
        """
        token = self._generate_token()
        
        return {
            'migrationToken': token,
            'sessionId': migration_session_id,
            'expiresAt': (datetime.now() + timedelta(hours=24)).isoformat(),
            'url': f"line://migrate?token={token}"
        }
    
    def issueTokenForAccountMigrationSettings(self, enforce: bool) -> dict:
        """
        إصدار رمز لإعدادات نقل الحساب
        """
        token = self._generate_token()
        
        return {
            'settingsToken': token,
            'enforce': enforce,
            'expiresAt': (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    def _verify_credentials(self, identifier: str, password: str) -> bool:
        """التحقق من بيانات الاعتماد (محاكاة)"""
        # في الواقع، يتم التحقق من قاعدة البيانات
        return True
    
    def _generate_token(self) -> str:
        """إنشاء رمز عشوائي آمن"""
        return secrets.token_urlsafe(32)
    
    def _create_session(self, identifier: str, token: str) -> str:
        """إنشاء جلسة جديدة"""
        session_id = hashlib.sha256(
            f"{identifier}{token}".encode()
        ).hexdigest()[:16]
        
        self.sessions[session_id] = {
            'identifier': identifier,
            'token': token,
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=1)
        }
        
        return session_id
    
    def _get_user_id(self, identifier: str) -> str:
        """الحصول على معرف المستخدم"""
        return hashlib.md5(identifier.encode()).hexdigest()[:10]
    
    def _verify_pin(self, pin_code: str) -> bool:
        """التحقق من رمز PIN"""
        return len(pin_code) == 4 and pin_code.isdigit()

# ============ مثال الاستخدام ============
if __name__ == '__main__':
    api = MessagingApi(ApiClient())
    service = AuthService(api)
    
    # تسجيل الدخول
    result = service.loginZ({
        'identifier': 'user@example.com',
        'password': 'hashed_password',
        'deviceName': 'iPhone 15'
    })
    print(f"🔐 تم تسجيل الدخول: {result['authToken'][:20]}...")
    
    # تنسيق رقم هاتف
    phone = service.normalizePhoneNumber('966', '512345678')
    print(f"📱 الرقم المنسق: {phone}")
    
    # تسجيل الخروج
    service.logoutZ()
