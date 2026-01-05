#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
هذا الكود يستخدم طريقة بديلة للحصول على التوكن
من خلال تسجيل الدخول بالإيميل والباسورد
"""

import json
import time
import os
import re
import requests
import hashlib
import rsa
import base64
from datetime import datetime
from collections import defaultdict

print("\n" + "="*50)
print("🤖 LINE Bot - تسجيل دخول بالإيميل")
print("="*50 + "\n")

# ============ LINE Login API ============

class LineLogin:
    def __init__(self):
        self.LINE_HOST = "https://gd2.line.naver.jp"
        self.headers = {
            "User-Agent": "Line/13.0.1",
            "X-Line-Application": "ANDROID\t13.0.1\tAndroid OS\t12"
        }
        self.authToken = None
    
    def login(self, email, password):
        """تسجيل الدخول بالإيميل والباسورد"""
        try:
            print("🔄 جاري تشفير البيانات...")
            
            # الحصول على RSA key
            rsa_key = self._get_rsa_key()
            if not rsa_key:
                raise Exception("فشل الحصول على مفتاح التشفير")
            
            # تشفير الباسورد
            encrypted_password = self._encrypt_password(password, rsa_key)
            
            print("🔄 جاري تسجيل الدخول...")
            
            # تسجيل الدخول
            response = requests.post(
                f"{self.LINE_HOST}/api/v4p/rs",
                headers=self.headers,
                json={
                    "loginRequest": {
                        "type": 0,
                        "identityProvider": 1,
                        "identifier": email,
                        "password": encrypted_password,
                        "keepLoggedIn": True,
                        "accessLocation": "127.0.0.1",
                        "systemName": "Android",
                        "certificate": ""
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("type") == 1:
                    # نجح تسجيل الدخول
                    self.authToken = result.get("authToken")
                    
                    if self.authToken:
                        print("✅ تم تسجيل الدخول بنجاح!")
                        return self.authToken
                    else:
                        raise Exception("لم يتم الحصول على التوكن")
                
                elif result.get("type") == 3:
                    # يحتاج PIN
                    raise Exception("الحساب يحتاج PIN code - استخدم طريقة التوكن")
                
                else:
                    raise Exception(f"خطأ غير معروف: {result}")
            
            else:
                raise Exception(f"خطأ في الاتصال: {response.status_code}")
        
        except Exception as e:
            raise Exception(f"فشل تسجيل الدخول: {e}")
    
    def _get_rsa_key(self):
        """الحصول على مفتاح RSA"""
        try:
            response = requests.post(
                f"{self.LINE_HOST}/api/v4p/rs",
                headers=self.headers,
                json={
                    "getRSAKeyRequest": {
                        "provider": 1
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "sessionKey": result.get("sessionKey"),
                    "nvalue": result.get("nvalue"),
                    "evalue": result.get("evalue")
                }
        except:
            pass
        return None
    
    def _encrypt_password(self, password, rsa_key):
        """تشفير الباسورد بـ RSA"""
        try:
            session_key = rsa_key["sessionKey"]
            n = int(rsa_key["nvalue"], 16)
            e = int(rsa_key["evalue"], 16)
            
            public_key = rsa.PublicKey(n, e)
            
            # التشفير
            message = (chr(len(session_key)) + session_key +
                      chr(len(password)) + password).encode('utf-8')
            
            encrypted = rsa.encrypt(message, public_key)
            return base64.b64encode(encrypted).decode('utf-8')
        
        except Exception as e:
            raise Exception(f"فشل التشفير: {e}")

# ============ المحاولة الأولى: تسجيل الدخول ============

print("⚠️ ملاحظة: حسابك يجب أن يكون مربوط بإيميل وباسورد!")
print("⚠️ إذا كان حسابك برقم جوال فقط، استخدم طريقة التوكن\n")

email = input("📧 الإيميل: ").strip()
password = input("🔑 الباسورد: ").strip()

if not email or not password:
    print("❌ يجب إدخال الإيميل والباسورد!")
    exit(1)

print()

try:
    login_client = LineLogin()
    token = login_client.login(email, password)
    
    # حفظ التوكن
    with open("token.txt", "w") as f:
        f.write(token)
    
    print(f"\n✅ تم حفظ التوكن في token.txt")
    print(f"📝 التوكن: {token[:50]}...")
    print("\n🎉 الآن يمكنك تشغيل البوت!")
    print("\nشغّل: python app.py")

except Exception as e:
    print(f"\n❌ فشل: {e}\n")
    print("💡 الحلول البديلة:")
    print("="*50)
    print("1. استخدم طريقة التوكن من الكمبيوتر")
    print("2. استخدم Kiwi Browser على الجوال")
    print("3. اربط حسابك بإيميل أولاً من LINE")
    print("="*50)
