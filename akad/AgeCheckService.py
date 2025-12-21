#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgeCheckService - خدمة التحقق من العمر
متوافق مع LINE Messaging API v3
"""

from typing import Optional
from datetime import datetime
from linebot.v3.messaging import MessagingApi, ApiClient

class AgeCheckService:
    """خدمة التحقق من العمر"""
    
    # أنواع مشغلي الشبكات
    CARRIER_DOCOMO = 1
    CARRIER_AU = 2
    CARRIER_SOFTBANK = 3
    CARRIER_LINE_MOBILE = 4
    
    def __init__(self, api: MessagingApi):
        self.api = api
        self.age_records = {}
        self.tokens = {}
    
    def checkUserAge(self, carrier: int, session_id: str, 
                     verifier: str, standard_age: int) -> int:
        """
        التحقق من عمر المستخدم عبر مشغل الشبكة
        
        Returns:
            0 = لم يتم التحقق
            1 = أقل من العمر المطلوب
            2 = أكبر من أو يساوي العمر المطلوب
        """
        # محاكاة التحقق من العمر
        user_age = self._verify_with_carrier(carrier, session_id, verifier)
        
        if user_age is None:
            return 0  # فشل التحقق
        
        # حفظ النتيجة
        self.age_records[session_id] = {
            'age': user_age,
            'carrier': carrier,
            'verified': True,
            'timestamp': datetime.now()
        }
        
        return 2 if user_age >= standard_age else 1
    
    def checkUserAgeWithDocomo(self, openid_redirect_url: str, 
                              standard_age: int, verifier: str) -> dict:
        """
        التحقق من العمر عبر Docomo OpenID
        
        Returns:
            dict: نتيجة التحقق
        """
        result = {
            'authUrl': f"{openid_redirect_url}?verifier={verifier}",
            'sessionId': f"docomo_{verifier[:8]}",
            'standardAge': standard_age
        }
        
        print(f"🔗 Docomo Auth URL: {result['authUrl']}")
        return result
    
    def retrieveOpenIdAuthUrlWithDocomo(self) -> str:
        """
        الحصول على رابط المصادقة عبر Docomo OpenID
        """
        auth_url = "https://id.smt.docomo.ne.jp/cgi8/oidc/authorize"
        return f"{auth_url}?response_type=code&scope=openid+age"
    
    def retrieveRequestToken(self, carrier: int) -> dict:
        """
        الحصول على رمز الطلب للتحقق من العمر
        
        Returns:
            dict: معلومات الرمز
        """
        token = f"AGE_TOKEN_{carrier}_{datetime.now().timestamp()}"
        
        self.tokens[token] = {
            'carrier': carrier,
            'created': datetime.now(),
            'used': False
        }
        
        return {
            'requestToken': token,
            'returnUrl': f"line://age/verify?token={token}",
            'carrier': self._get_carrier_name(carrier)
        }
    
    def _verify_with_carrier(self, carrier: int, session_id: str, 
                            verifier: str) -> Optional[int]:
        """التحقق من العمر مع مشغل الشبكة (محاكاة)"""
        # في الواقع، هذا يتصل بـ API المشغل
        # هنا نرجع عمر افتراضي للاختبار
        return 20
    
    def _get_carrier_name(self, carrier: int) -> str:
        """الحصول على اسم المشغل"""
        carriers = {
            1: 'Docomo',
            2: 'AU',
            3: 'Softbank',
            4: 'LINE Mobile'
        }
        return carriers.get(carrier, 'Unknown')

# ============ مثال الاستخدام ============
if __name__ == '__main__':
    api = MessagingApi(ApiClient())
    service = AgeCheckService(api)
    
    # الحصول على رمز الطلب
    token_info = service.retrieveRequestToken(
        carrier=AgeCheckService.CARRIER_LINE_MOBILE
    )
    print(f"🎫 Token: {token_info['requestToken']}")
    
    # التحقق من العمر
    result = service.checkUserAge(
        carrier=AgeCheckService.CARRIER_LINE_MOBILE,
        session_id='test_session',
        verifier='test_verifier',
        standard_age=18
    )
    
    status = {0: 'فشل', 1: 'أقل من 18', 2: 'مؤهل ✅'}
    print(f"📊 النتيجة: {status[result]}")
