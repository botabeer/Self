from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, PushMessageRequest,
    TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, 
    JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent
)
from apscheduler.schedulers.background import BackgroundScheduler
from database import Database
from protection_advanced import AdvancedProtection
from admin_system import AdminSystem
from ui_builder import UIBuilder
import os
import logging
import atexit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

required_env_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"متغير البيئة {var} غير موجود")
        raise ValueError(f"متغير البيئة {var} مطلوب")

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

Database.init()
protection = AdvancedProtection(line_bot_api)
admin_system = AdminSystem(line_bot_api)

scheduler = BackgroundScheduler()
scheduler.add_job(func=Database.cleanup_warnings, trigger="interval", hours=24)
scheduler.add_job(func=protection.cleanup_old_data, trigger="interval", minutes=10)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def reply_message(reply_token, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
    except Exception as e:
        logger.error(f"خطأ في الرد: {e}")

def push_message(to, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.push_message(
            PushMessageRequest(to=to, messages=messages)
        )
    except Exception as e:
        logger.error(f"خطأ في الارسال: {e}")

def delete_message(message_id):
    try:
        line_bot_api.delete_message(message_id)
        return True
    except Exception as e:
        logger.error(f"فشل حذف الرسالة: {e}")
        return False

def kick_user(group_id, user_id):
    try:
        line_bot_api.kick_group_member(group_id, user_id)
        return True
    except Exception as e:
        logger.error(f"فشل الطرد: {e}")
        return False

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ في معالجة الطلب: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None)
        message_id = event.message.id
        
        if not group_id:
            reply_message(event.reply_token, TextMessage(text="هذا البوت يعمل في القروبات فقط"))
            return
        
        profile = line_bot_api.get_group_member_profile(group_id, user_id)
        display_name = profile.display_name if profile else "مستخدم"
        
        is_owner = admin_system.is_owner(user_id)
        is_admin = admin_system.is_admin(user_id) or is_owner
        
        # فحص اذا المستخدم مكتوم
        if protection.is_muted(group_id, user_id) and not is_admin:
            delete_message(message_id)
            return
        
        # اوامر المالك
        if text.startswith("اضف مالك "):
            if not is_owner:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للمالك فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                admin_system.add_owner(mentioned)
                reply_message(event.reply_token, TextMessage(text="تم اضافة المالك بنجاح"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("حذف مالك "):
            if not is_owner:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للمالك فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                admin_system.remove_owner(mentioned)
                reply_message(event.reply_token, TextMessage(text="تم حذف المالك"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        # اوامر الادمن
        if text.startswith("اضف ادمن "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                admin_system.add_admin(mentioned)
                reply_message(event.reply_token, TextMessage(text="تم اضافة الادمن بنجاح"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("حذف ادمن "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                admin_system.remove_admin(mentioned)
                reply_message(event.reply_token, TextMessage(text="تم حذف الادمن"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text == "قائمة الادمن":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            admins_list = admin_system.get_admins_list()
            reply_message(event.reply_token, TextMessage(text=admins_list))
            return
        
        # اوامر الحماية
        if text.startswith("بان ") or text.startswith("حظر "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                if admin_system.is_admin(mentioned) or admin_system.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="لا يمكن حظر ادمن او مالك"))
                    return
                
                reason = text.split(maxsplit=2)[2] if len(text.split()) > 2 else "مخالفة قوانين القروب"
                success = Database.ban_user(group_id, mentioned, user_id, reason)
                
                if success:
                    if kick_user(group_id, mentioned):
                        Database.log_action(group_id, mentioned, user_id, "ban", reason)
                        reply_message(event.reply_token, TextMessage(text=f"تم حظر {display_name}\nالسبب: {reason}"))
                    else:
                        reply_message(event.reply_token, TextMessage(text="تم اضافة المستخدم للقائمة السوداء"))
                else:
                    reply_message(event.reply_token, TextMessage(text="فشل الحظر"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("الغاء بان ") or text.startswith("الغاء حظر "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                success = Database.unban_user(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text="تم الغاء الحظر" if success else "المستخدم غير محظور"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("كتم ") or text.startswith("ميوت "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                if admin_system.is_admin(mentioned) or admin_system.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="لا يمكن كتم ادمن او مالك"))
                    return
                
                parts = text.split()
                duration = 30
                if len(parts) > 2 and parts[2].isdigit():
                    duration = int(parts[2])
                
                protection.mute_user(group_id, mentioned, duration)
                Database.log_action(group_id, mentioned, user_id, "mute", f"{duration} دقيقة")
                reply_message(event.reply_token, TextMessage(text=f"تم كتم المستخدم لمدة {duration} دقيقة"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم\nالصيغة: كتم @المستخدم المدة"))
            return
        
        if text.startswith("الغاء كتم ") or text.startswith("الغاء ميوت "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                protection.mute_user(group_id, mentioned, 0)
                reply_message(event.reply_token, TextMessage(text="تم الغاء الكتم"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("انذار ") or text.startswith("تحذير "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                if admin_system.is_admin(mentioned) or admin_system.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="لا يمكن انذار ادمن او مالك"))
                    return
                
                reason = text.split(maxsplit=2)[2] if len(text.split()) > 2 else "مخالفة"
                warnings = Database.add_warning(group_id, mentioned, user_id, reason)
                
                if warnings >= 3:
                    if kick_user(group_id, mentioned):
                        reply_message(event.reply_token, TextMessage(text=f"تم طرد المستخدم بعد {warnings} انذارات"))
                    else:
                        reply_message(event.reply_token, TextMessage(text=f"وصل المستخدم الى {warnings} انذارات"))
                else:
                    reply_message(event.reply_token, TextMessage(text=f"تم اعطاء انذار ({warnings}/3)\nالسبب: {reason}"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("حذف انذار "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                Database.clear_warnings(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text="تم حذف جميع الانذارات"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("انذارات "):
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                warnings = Database.get_user_warnings(group_id, mentioned)
                reply_message(event.reply_token, TextMessage(text=f"عدد الانذارات: {warnings}/3"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        if text.startswith("طرد ") or text.startswith("كيك "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            mentioned = admin_system.extract_user_id(text)
            if mentioned:
                if admin_system.is_admin(mentioned) or admin_system.is_owner(mentioned):
                    reply_message(event.reply_token, TextMessage(text="لا يمكن طرد ادمن او مالك"))
                    return
                
                if kick_user(group_id, mentioned):
                    Database.log_action(group_id, mentioned, user_id, "kick", "طرد")
                    reply_message(event.reply_token, TextMessage(text="تم طرد المستخدم"))
                else:
                    reply_message(event.reply_token, TextMessage(text="فشل الطرد تأكد من صلاحيات البوت"))
            else:
                reply_message(event.reply_token, TextMessage(text="قم بعمل منشن للمستخدم"))
            return
        
        # اعدادات الحماية
        if text.startswith("تفعيل "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            setting = text.replace("تفعيل ", "").strip()
            settings_map = {
                "الروابط": "links",
                "السبام": "spam",
                "الفلود": "flood",
                "الكلمات": "bad_words",
                "الترحيب": "welcome",
                "الحماية": "all"
            }
            
            if setting in settings_map:
                Database.update_group_settings(group_id, settings_map[setting], True)
                reply_message(event.reply_token, TextMessage(text=f"تم تفعيل {setting}"))
            else:
                reply_message(event.reply_token, TextMessage(text="خيار غير صحيح"))
            return
        
        if text.startswith("تعطيل "):
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            setting = text.replace("تعطيل ", "").strip()
            settings_map = {
                "الروابط": "links",
                "السبام": "spam",
                "الفلود": "flood",
                "الكلمات": "bad_words",
                "الترحيب": "welcome",
                "الحماية": "all"
            }
            
            if setting in settings_map:
                Database.update_group_settings(group_id, settings_map[setting], False)
                reply_message(event.reply_token, TextMessage(text=f"تم تعطيل {setting}"))
            else:
                reply_message(event.reply_token, TextMessage(text="خيار غير صحيح"))
            return
        
        if text == "الاعدادات":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            settings = Database.get_group_settings(group_id)
            flex = FlexMessage(
                alt_text="اعدادات الحماية",
                contents=FlexContainer.from_dict(UIBuilder.settings_card(settings))
            )
            reply_message(event.reply_token, flex)
            return
        
        # معلومات
        if text == "الاوامر":
            flex = FlexMessage(
                alt_text="قائمة الاوامر",
                contents=FlexContainer.from_dict(UIBuilder.commands_card(is_admin, is_owner))
            )
            reply_message(event.reply_token, flex)
            return
        
        if text == "احصائيات":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            stats = Database.get_group_stats(group_id)
            flex = FlexMessage(
                alt_text="احصائيات القروب",
                contents=FlexContainer.from_dict(UIBuilder.stats_card(stats))
            )
            reply_message(event.reply_token, flex)
            return
        
        if text == "المحظورين":
            if not is_admin:
                reply_message(event.reply_token, TextMessage(text="هذا الامر للادمن فقط"))
                return
            
            banned = Database.get_banned_users(group_id)
            flex = FlexMessage(
                alt_text="قائمة المحظورين",
                contents=FlexContainer.from_dict(UIBuilder.banned_users_card(banned))
            )
            reply_message(event.reply_token, flex)
            return
        
        # الفحص الشامل للرسالة اذا مو من ادمن
        if not is_admin:
            settings = Database.get_group_settings(group_id)
            if settings.get('protection_enabled', True):
                result = protection.comprehensive_check(group_id, user_id, text, display_name)
                
                if result.get('violation'):
                    delete_message(message_id)
                    
                    reason = result['reason']
                    action = result['action']
                    
                    if action == 'ban':
                        Database.ban_user(group_id, user_id, "bot", reason)
                        kick_user(group_id, user_id)
                        push_message(group_id, TextMessage(text=f"تم حظر {display_name}\nالسبب: {reason}"))
                    
                    elif action == 'kick':
                        kick_user(group_id, user_id)
                        push_message(group_id, TextMessage(text=f"تم طرد {display_name}\nالسبب: {reason}"))
                    
                    elif action == 'warn_mute':
                        warnings = Database.add_warning(group_id, user_id, "bot", reason)
                        protection.mute_user(group_id, user_id, 10)
                        push_message(group_id, TextMessage(text=f"انذار {display_name} ({warnings}/3)\nتم الكتم 10 دقائق\nالسبب: {reason}"))
                    
                    elif action == 'warn':
                        warnings = Database.add_warning(group_id, user_id, "bot", reason)
                        if warnings >= 3:
                            kick_user(group_id, user_id)
                            push_message(group_id, TextMessage(text=f"تم طرد {display_name} بعد 3 انذارات"))
                        else:
                            push_message(group_id, TextMessage(text=f"انذار {display_name} ({warnings}/3)\nالسبب: {reason}"))
                    
                    return
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    try:
        group_id = event.source.group_id
        
        for member in event.joined.members:
            user_id = member.user_id
            
            if Database.is_banned(group_id, user_id):
                kick_user(group_id, user_id)
                push_message(group_id, TextMessage(text="تم طرد مستخدم محظور حاول الدخول"))
                continue
            
            protection.register_new_member(group_id, user_id)
            
            settings = Database.get_group_settings(group_id)
            if settings.get('welcome', True):
                try:
                    profile = line_bot_api.get_group_member_profile(group_id, user_id)
                    name = profile.display_name if profile else "عضو جديد"
                    
                    flex = FlexMessage(
                        alt_text="ترحيب",
                        contents=FlexContainer.from_dict(UIBuilder.welcome_member_card(name))
                    )
                    push_message(group_id, flex)
                except:
                    pass
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الانضمام: {e}")

@handler.add(JoinEvent)
def handle_join(event):
    try:
        group_id = event.source.group_id
        Database.create_group(group_id)
        
        flex = FlexMessage(
            alt_text="شكرا للاضافة",
            contents=FlexContainer.from_dict(UIBuilder.bot_joined_card())
        )
        push_message(group_id, flex)
    
    except Exception as e:
        logger.error(f"خطأ في معالجة انضمام البوت: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'protection-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
