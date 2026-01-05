#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Token Extractor - QR Code Method
يحصل على التوكن باستخدام QR Code
"""

import requests
import json
import time
import qrcode
from io import BytesIO

print("""
╔═══════════════════════════════════════════╗
║   🔑 LINE Token via QR Code               ║
╚═══════════════════════════════════════════╝
""")

LINE_API = "https://gd2.line.naver.jp"

def get_qr_code():
    """الحصول على QR Code"""
    print("\n🔄 جاري إنشاء QR Code...")
    
    try:
        # طلب QR Code
        response = requests.post(
            f"{LINE_API}/api/v4p/rs",
            headers={
                "User-Agent": "Line/13.0.1",
                "X-Line-Application": "ANDROID\t13.0.1\tAndroid OS\t12"
            },
            json={
                "getAuthQrCodeRequest": {}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            qr_url = result.get("callbackUrl")
            
            if qr_url:
                print("\n✅ تم إنشاء QR Code!")
                print(f"\n🔗 الرابط: {qr_url}")
                
                # عرض QR Code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                print("\n📱 QR Code:")
                qr.print_ascii()
                
                print("\n📋 الخطوات:")
                print("1. افتح LINE على جوالك")
                print("2. Settings → Account")
                print("3. Login on another device")
                print("4. امسح الـ QR Code أعلاه")
                print("\n⏳ في انتظار المسح...")
                
                # انتظار المسح
                for i in range(60):
                    time.sleep(2)
                    
                    # التحقق من المسح
                    check = requests.post(
                        f"{LINE_API}/api/v4p/rs",
                        headers={
                            "User-Agent": "Line/13.0.1",
                            "X-Line-Application": "ANDROID\t13.0.1\tAndroid OS\t12"
                        },
                        json={
                            "verifyQrCodeRequest": {
                                "verifier": result.get("verifier")
                            }
                        }
                    )
                    
                    if check.status_code == 200:
                        check_result = check.json()
                        
                        if check_result.get("type") == 1:
                            # نجح!
                            token = check_result.get("authToken")
                            
                            print("\n✅ تم المسح بنجاح!")
                            print(f"\n🔑 التوكن:")
                            print(f"{token}")
                            
                            # حفظ التوكن
                            with open("token.txt", "w") as f:
                                f.write(token)
                            
                            print("\n✅ تم حفظ التوكن في token.txt")
                            return token
                
                print("\n⏱️ انتهى الوقت! جرّب مرة ثانية")
                
        else:
            print(f"❌ خطأ: {response.status_code}")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    return None

def main():
    print("\n⚠️ ملاحظة: هذه الطريقة قد لا تعمل مع كل الحسابات")
    print("💡 إذا ما اشتغلت، استخدم الطرق البديلة\n")
    
    input("اضغط Enter للبدء...")
    
    token = get_qr_code()
    
    if token:
        print("\n🎉 نجحت!")
        print(f"\nالتوكن: {token[:50]}...")
        print("\nالآن انسخ التوكن واستخدمه في Termux!")
    else:
        print("\n❌ فشلت!")
        print("\n💡 جرّب الطرق البديلة:")
        print("1. LINE Desktop → ملفات البيانات")
        print("2. Edge → line.me")
        print("3. استخدم VPN لفتح chrome.line.me")
    
    input("\nاضغط Enter للخروج...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        input("\nاضغط Enter للخروج...")
