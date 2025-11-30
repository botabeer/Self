"""
Bot Mesh v22.2 PRO 3D - UI Builder Premium Edition
Created by: Abeer Aldosari © 2025

✨ تصميم ثري دي احترافي
🎨 تدرجات لونية متناسقة
🎯 آلية ذكية للتنقل
👁️ مريح للعين
⚡ سريع وسهل الاستخدام
"""

from linebot.v3.messaging import FlexMessage, FlexContainer, QuickReply, QuickReplyItem, MessageAction, TextMessage
from constants import GAME_LIST, DEFAULT_THEME, THEMES, BOT_NAME, BOT_RIGHTS, FIXED_GAME_QR


def _colors(theme=None):
    """الحصول على ألوان الثيم"""
    return THEMES.get(theme or DEFAULT_THEME, THEMES[DEFAULT_THEME])


# ============================================================================
# مكونات التصميم الأساسية - Premium 3D Components
# ============================================================================

def _3d_gradient_card(contents, theme=None, padding="20px", margin="md"):
    """بطاقة بتأثير ثري دي وتدرج لوني"""
    c = _colors(theme)
    return {
        "type": "box",
        "layout": "vertical",
        "contents": contents,
        "backgroundColor": c["card"],
        "cornerRadius": "20px",
        "paddingAll": padding,
        "margin": margin,
        "borderWidth": "2px",
        "borderColor": c["border"],
        "offsetTop": "0px",
        "offsetStart": "0px", 
        "offsetEnd": "0px",
        "offsetBottom": "6px",
        "action": {"type": "uri", "uri": "https://line.me"}
    }


def _premium_header(text, subtitle=None, theme=None):
    """ترويسة احترافية بتدرج لوني"""
    c = _colors(theme)
    contents = [
        {
            "type": "text",
            "text": text,
            "size": "xxl",
            "weight": "bold",
            "color": c["button_text"],
            "align": "center",
            "gravity": "center"
        }
    ]
    
    if subtitle:
        contents.append({
            "type": "text",
            "text": subtitle,
            "size": "xs",
            "color": c["button_text"],
            "align": "center",
            "margin": "sm",
            "weight": "bold"
        })
    
    return {
        "type": "box",
        "layout": "vertical",
        "contents": contents,
        "background": {
            "type": "linearGradient",
            "angle": "135deg",
            "startColor": c["gradient_start"],
            "endColor": c["gradient_end"]
        },
        "cornerRadius": "20px",
        "paddingAll": "20px",
        "margin": "none",
        "offsetBottom": "6px"
    }


def _3d_button(label, text, style="primary", theme=None, height="50px"):
    """زر ثري دي احترافي مع تأثيرات"""
    c = _colors(theme)
    
    if style == "primary":
        bg_color = c["primary"]
        text_color = c["button_text"]
        border_color = c["primary"]
    elif style == "secondary":
        bg_color = c["secondary"]
        text_color = c["button_text"]
        border_color = c["secondary"]
    elif style == "success":
        bg_color = c["success"]
        text_color = c["button_text"]
        border_color = c["success"]
    else:
        bg_color = c["card"]
        text_color = c["text"]
        border_color = c["border"]
    
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": label,
                "size": "md",
                "weight": "bold",
                "color": text_color,
                "align": "center",
                "gravity": "center"
            }
        ],
        "backgroundColor": bg_color,
        "cornerRadius": "15px",
        "paddingAll": "14px",
        "action": {"type": "message", "text": text},
        "height": height,
        "borderWidth": "2px",
        "borderColor": border_color,
        "offsetBottom": "4px"
    }


def _elegant_separator(theme=None, margin="lg"):
    """فاصل أنيق"""
    c = _colors(theme)
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "flex": 1,
                "height": "2px",
                "backgroundColor": c["border"]
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "◆",
                        "size": "xs",
                        "color": c["primary"],
                        "align": "center"
                    }
                ],
                "flex": 0,
                "paddingAll": "0px",
                "margin": "none"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "flex": 1,
                "height": "2px",
                "backgroundColor": c["border"]
            }
        ],
        "margin": margin,
        "alignItems": "center"
    }


def _stat_card(label, value, icon="●", color_key="primary", theme=None):
    """بطاقة إحصائية ثري دي"""
    c = _colors(theme)
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": icon,
                "size": "xl",
                "color": c[color_key],
                "align": "center",
                "weight": "bold"
            },
            {
                "type": "text",
                "text": str(value),
                "size": "xxl",
                "weight": "bold",
                "color": c[color_key],
                "align": "center",
                "margin": "md"
            },
            {
                "type": "text",
                "text": label,
                "size": "xs",
                "color": c["text3"],
                "align": "center",
                "weight": "bold",
                "margin": "sm"
            }
        ],
        "backgroundColor": c["card"],
        "cornerRadius": "18px",
        "paddingAll": "18px",
        "borderWidth": "2px",
        "borderColor": c[color_key],
        "flex": 1,
        "offsetBottom": "5px"
    }


def _info_badge(text, color_key="info", theme=None):
    """شارة معلومات أنيقة"""
    c = _colors(theme)
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": text,
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "align": "center"
            }
        ],
        "backgroundColor": c[f"{color_key}_bg"],
        "cornerRadius": "12px",
        "paddingAll": "12px",
        "borderWidth": "1px",
        "borderColor": c[color_key],
        "margin": "md",
        "offsetBottom": "3px"
    }


def _game_card(game_name, theme=None):
    """بطاقة لعبة احترافية"""
    c = _colors(theme)
    
    # أيقونات الألعاب
    game_icons = {
        "ذكاء": "🧠", "رياضيات": "🔢", "لون": "🎨", "ترتيب": "🔤",
        "أسرع": "⚡", "ضد": "↔️", "تكوين": "📝", "أغنيه": "🎵",
        "لعبة": "🎮", "سلسلة": "⛓️", "خمن": "🤔", "توافق": "💕"
    }
    
    icon = game_icons.get(game_name, "🎯")
    
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": icon,
                "size": "xxl",
                "align": "center"
            },
            {
                "type": "text",
                "text": game_name,
                "size": "md",
                "weight": "bold",
                "color": c["text"],
                "align": "center",
                "margin": "sm"
            }
        ],
        "backgroundColor": c["card"],
        "cornerRadius": "16px",
        "paddingAll": "16px",
        "action": {"type": "message", "text": game_name},
        "borderWidth": "2px",
        "borderColor": c["border"],
        "flex": 1,
        "offsetBottom": "4px"
    }


# ============================================================================
# الصفحة الرئيسية المحسّنة
# ============================================================================

def build_enhanced_home(username, points, is_registered=True, theme=DEFAULT_THEME, mode_label="فردي"):
    """صفحة رئيسية احترافية ثري دي"""
    c = _colors(theme)
    
    # تحديد المستوى
    if points < 50:
        level = "مبتدئ 🌱"
        level_color = "text2"
    elif points < 150:
        level = "متوسط ⭐"
        level_color = "info"
    elif points < 300:
        level = "متقدم 🔥"
        level_color = "warning"
    else:
        level = "محترف 👑"
        level_color = "success"
    
    status_icon = "✅" if is_registered else "⚠️"
    status_text = "نشط" if is_registered else "غير مسجل"
    join_text = "انسحب 🚪" if is_registered else "انضم 🎯"
    
    # أزرار الثيمات الذكية
    themes_list = list(THEMES.keys())
    theme_emojis = {
        "أبيض": "☀️", "أسود": "🌙", "أزرق": "💙",
        "بنفسجي": "💜", "وردي": "💗", "أخضر": "💚",
        "برتقالي": "🧡", "أحمر": "❤️", "بني": "🤎"
    }
    
    theme_buttons = []
    for i in range(0, len(themes_list), 3):
        row_themes = themes_list[i:i+3]
        theme_buttons.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "margin": "sm",
            "contents": [
                _3d_button(
                    f"{theme_emojis.get(t, '🎨')} {t}",
                    f"ثيم {t}",
                    "primary" if t == theme else "outline",
                    theme,
                    "48px"
                )
                for t in row_themes
            ]
        })
    
    body = {
        "type": "carousel",
        "contents": [
            # البطاقة الأولى: معلومات المستخدم
            {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        _premium_header(f"👋 مرحباً", username, theme),
                        
                        _3d_gradient_card([
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": status_icon,
                                                "size": "xxl",
                                                "align": "center"
                                            },
                                            {
                                                "type": "text",
                                                "text": status_text,
                                                "size": "xs",
                                                "color": c["success"] if is_registered else c["warning"],
                                                "align": "center",
                                                "weight": "bold",
                                                "margin": "sm"
                                            }
                                        ],
                                        "flex": 1
                                    },
                                    {
                                        "type": "separator",
                                        "margin": "lg",
                                        "color": c["border"]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "🏆",
                                                "size": "xxl",
                                                "align": "center"
                                            },
                                            {
                                                "type": "text",
                                                "text": str(points),
                                                "size": "xl",
                                                "color": c["primary"],
                                                "align": "center",
                                                "weight": "bold",
                                                "margin": "sm"
                                            },
                                            {
                                                "type": "text",
                                                "text": "نقطة",
                                                "size": "xs",
                                                "color": c["text3"],
                                                "align": "center",
                                                "weight": "bold"
                                            }
                                        ],
                                        "flex": 1
                                    },
                                    {
                                        "type": "separator",
                                        "margin": "lg",
                                        "color": c["border"]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "📊",
                                                "size": "xxl",
                                                "align": "center"
                                            },
                                            {
                                                "type": "text",
                                                "text": level,
                                                "size": "sm",
                                                "color": c[level_color],
                                                "align": "center",
                                                "weight": "bold",
                                                "margin": "sm",
                                                "wrap": True
                                            }
                                        ],
                                        "flex": 1
                                    }
                                ]
                            }
                        ], theme, "20px"),
                        
                        _info_badge(f"🎮 الوضع: {mode_label}", "info", theme),
                        
                        _elegant_separator(theme),
                        
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                _3d_button(join_text, join_text.replace("🎯", "").replace("🚪", "").strip(), "primary" if is_registered else "success", theme),
                                _3d_button("🎮 ألعاب", "ألعاب", "primary", theme)
                            ]
                        },
                        
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "margin": "sm",
                            "contents": [
                                _3d_button("📊 نقاطي", "نقاطي", "secondary", theme),
                                _3d_button("🏆 صدارة", "صدارة", "secondary", theme)
                            ]
                        },
                        
                        _elegant_separator(theme),
                        
                        {
                            "type": "text",
                            "text": BOT_RIGHTS,
                            "size": "xxs",
                            "color": c["text3"],
                            "align": "center",
                            "wrap": True
                        }
                    ],
                    "paddingAll": "20px",
                    "backgroundColor": c["bg"]
                }
            },
            
            # البطاقة الثانية: الثيمات
            {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        _premium_header("🎨 المظهر", "اختر الثيم المفضل", theme),
                        
                        {
                            "type": "text",
                            "text": "✨ تخصيص المظهر",
                            "size": "md",
                            "weight": "bold",
                            "color": c["text"],
                            "align": "center",
                            "margin": "lg"
                        },
                        
                        *theme_buttons,
                        
                        _elegant_separator(theme),
                        
                        _3d_gradient_card([
                            {
                                "type": "text",
                                "text": "💡 نصيحة",
                                "size": "sm",
                                "weight": "bold",
                                "color": c["primary"]
                            },
                            {
                                "type": "text",
                                "text": "اختر الثيم الذي يريح عينك ويناسب ذوقك",
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "sm"
                            }
                        ], theme, "14px"),
                        
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                _3d_button("🏠 رجوع", "بداية", "secondary", theme),
                                _3d_button("❓ مساعدة", "مساعدة", "secondary", theme)
                            ]
                        }
                    ],
                    "paddingAll": "20px",
                    "backgroundColor": c["bg"]
                }
            }
        ]
    }
    
    msg = FlexMessage(alt_text="البداية", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


# ============================================================================
# قائمة الألعاب المحسّنة
# ============================================================================

def build_games_menu(theme=DEFAULT_THEME, top_games=None):
    """قائمة ألعاب احترافية ثري دي"""
    c = _colors(theme)
    
    # ترتيب الألعاب
    default_order = ["أسرع", "ذكاء", "لعبة", "خمن", "أغنيه", "سلسلة", 
                     "ترتيب", "تكوين", "ضد", "لون", "رياضيات", "توافق"]
    
    order = (top_games + [g for g in default_order if g not in top_games]) if top_games and len(top_games) > 0 else default_order
    order = order[:12]
    
    # تقسيم الألعاب إلى مجموعات
    game_rows = []
    for i in range(0, len(order), 3):
        row_games = order[i:i+3]
        game_rows.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "margin": "sm",
            "contents": [_game_card(game, theme) for game in row_games]
        })
    
    body = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                _premium_header("🎮 الألعاب", "اختر لعبتك المفضلة", theme),
                
                _info_badge("⭐ الأكثر شعبية", "success", theme),
                
                *game_rows,
                
                _elegant_separator(theme),
                
                _3d_gradient_card([
                    {
                        "type": "text",
                        "text": "ℹ️ كيف تلعب",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "1. اضغط على اللعبة للبدء\n2. اكتب 'لمح' للمساعدة\n3. اكتب 'جاوب' لكشف الإجابة\n4. اكتب 'إيقاف' لإنهاء اللعبة",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    }
                ], theme, "14px"),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "lg",
                    "contents": [
                        _3d_button("🏠 رجوع", "بداية", "secondary", theme),
                        _3d_button("🛑 إيقاف", "إيقاف", "secondary", theme)
                    ]
                },
                
                _elegant_separator(theme),
                
                {
                    "type": "text",
                    "text": BOT_RIGHTS,
                    "size": "xxs",
                    "color": c["text3"],
                    "align": "center",
                    "wrap": True
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="الألعاب", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


# ============================================================================
# نقاطي المحسّنة
# ============================================================================

def build_my_points(username, points, stats=None, theme=DEFAULT_THEME):
    """صفحة إحصائيات احترافية"""
    c = _colors(theme)
    
    # تحديد المستوى والشارة
    if points < 50:
        level = "مبتدئ"
        badge = "🌱"
        level_color = "text2"
        progress = (points / 50) * 100
        next_level = "متوسط"
        next_points = 50
    elif points < 150:
        level = "متوسط"
        badge = "⭐"
        level_color = "info"
        progress = ((points - 50) / 100) * 100
        next_level = "متقدم"
        next_points = 150
    elif points < 300:
        level = "متقدم"
        badge = "🔥"
        level_color = "warning"
        progress = ((points - 150) / 150) * 100
        next_level = "محترف"
        next_points = 300
    else:
        level = "محترف"
        badge = "👑"
        level_color = "success"
        progress = 100
        next_level = "أسطورة"
        next_points = points + 100
    
    remaining = next_points - points if points < 300 else 0
    
    body = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                _premium_header(f"{badge} {username}", f"مستوى {level}", theme),
                
                _3d_gradient_card([
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            _stat_card("النقاط", points, "🏆", "primary", theme),
                            _stat_card("المستوى", level, badge, level_color, theme)
                        ],
                        "spacing": "md"
                    }
                ], theme, "18px"),
                
                # شريط التقدم
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"التقدم نحو {next_level}",
                                    "size": "xs",
                                    "color": c["text2"],
                                    "weight": "bold",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": f"{int(progress)}%",
                                    "size": "xs",
                                    "color": c["primary"],
                                    "weight": "bold",
                                    "align": "end",
                                    "flex": 0
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "width": f"{int(progress)}%",
                                    "backgroundColor": c["primary"],
                                    "height": "8px",
                                    "cornerRadius": "4px"
                                }
                            ],
                            "backgroundColor": c["border"],
                            "height": "8px",
                            "cornerRadius": "4px",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": f"تبقى {remaining} نقطة" if remaining > 0 else "مستوى رائع! 🎉",
                            "size": "xs",
                            "color": c["text3"],
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": c["card"],
                    "cornerRadius": "15px",
                    "paddingAll": "16px",
                    "margin": "md",
                    "borderWidth": "1px",
                    "borderColor": c["border"]
                },
                
                _elegant_separator(theme),
                
                _3d_gradient_card([
                    {
                        "type": "text",
                        "text": "💡 نصيحة",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["primary"]
                    },
                    {
                        "type": "text",
                        "text": "العب المزيد من الألعاب لزيادة نقاطك والوصول للمستوى التالي!",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    }
                ], theme, "14px"),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "lg",
                    "contents": [
                        _3d_button("🏠 رجوع", "بداية", "secondary", theme),
                        _3d_button("🏆 الصدارة", "صدارة", "primary", theme)
                    ]
                },
                
                _elegant_separator(theme),
                
                {
                    "type": "text",
                    "text": BOT_RIGHTS,
                    "size": "xxs",
                    "color": c["text3"],
                    "align": "center"
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="نقاطي", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


# ============================================================================
# لوحة الصدارة المحسّنة
# ============================================================================

def build_leaderboard(top_users, theme=DEFAULT_THEME):
    """لوحة صدارة احترافية ثري دي"""
    c = _colors(theme)
    
    # المراكز الثلاثة الأولى (بطاقات خاصة)
    top_3_cards = []
    medals = ["🥇", "🥈", "🥉"]
    medal_colors = ["primary", "accent", "secondary"]
    
    for i, (name, pts, is_registered) in enumerate(top_users[:3]):
        if i >= 3:
            break
        
        status_icon = "✅" if is_registered else "⚠️"
        
        top_3_cards.append(_3d_gradient_card([
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": medals[i],
                                "size": "xxl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": f"#{i+1}",
                                "size": "xs",
                                "color": c["text3"],
                                "align": "center",
                                "weight": "bold",
                                "margin": "xs"
                            }
                        ],
                        "flex": 0,
                        "width": "60px"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": name[:20],
                                "size": "lg" if i == 0 else "md",
                                "weight": "bold",
                                "color": c["text"],
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": f"{status_icon} {pts} نقطة",
                                "size": "sm",
                                "color": c[medal_colors[i]],
                                "weight": "bold",
                                "margin": "sm"
                            }
                        ],
                        "flex": 1
                    }
                ]
            }
        ], theme, "16px", "sm"))
    
    # باقي المراكز (قائمة عادية)
    other_ranks = []
    for i, (name, pts, is_registered) in enumerate(top_users[3:20], 4):
        status_icon = "●" if is_registered else "○"
        status_color = c["success"] if is_registered else c["text3"]
        
        other_ranks.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"#{i}",
                    "size": "sm",
                    "weight": "bold",
                    "color": c["text2"],
                    "flex": 0,
                    "align": "center",
                    "gravity": "center"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": c["border"]
                },
                {
                    "type": "text",
                    "text": name[:25],
                    "size": "sm",
                    "color": c["text"],
                    "flex": 3,
                    "margin": "md",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": str(pts),
                    "size": "sm",
                    "weight": "bold",
                    "color": c["primary"],
                    "align": "center",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": status_icon,
                    "size": "sm",
                    "color": status_color,
                    "flex": 0,
                    "align": "center"
                }
            ],
            "paddingAll": "10px",
            "backgroundColor": c["card"],
            "cornerRadius": "10px",
            "borderWidth": "1px",
            "borderColor": c["border"],
            "margin": "xs",
            "offsetBottom": "2px"
        })
    
    body = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                _premium_header("🏆 لوحة الصدارة", "أفضل 20 لاعب", theme),
                
                {
                    "type": "text",
                    "text": "👑 المتصدرون",
                    "size": "md",
                    "weight": "bold",
                    "color": c["text"],
                    "margin": "lg"
                },
                
                *top_3_cards,
                
                _elegant_separator(theme),
                
                {
                    "type": "text",
                    "text": "📋 بقية المراكز",
                    "size": "sm",
                    "weight": "bold",
                    "color": c["text2"],
                    "margin": "md"
                },
                
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": other_ranks,
                    "margin": "sm"
                },
                
                _elegant_separator(theme),
                
                _info_badge("● نشط • ○ غير نشط", "info", theme),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "lg",
                    "contents": [
                        _3d_button("🏠 رجوع", "بداية", "secondary", theme),
                        _3d_button("📊 نقاطي", "نقاطي", "primary", theme)
                    ]
                },
                
                _elegant_separator(theme),
                
                {
                    "type": "text",
                    "text": BOT_RIGHTS,
                    "size": "xxs",
                    "color": c["text3"],
                    "align": "center"
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="الصدارة", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


# ============================================================================
# نافذة المساعدة المحسّنة
# ============================================================================

def build_help_window(theme=DEFAULT_THEME):
    """نافذة مساعدة احترافية"""
    c = _colors(theme)
    
    help_sections = [
        {
            "icon": "🎮",
            "title": "كيف تلعب",
            "text": "اختر لعبتك من القائمة وابدأ فوراً. استخدم 'لمح' للمساعدة و 'جاوب' لكشف الإجابة"
        },
        {
            "icon": "👤",
            "title": "التسجيل",
            "text": "اكتب 'انضم' للتسجيل وجمع النقاط. يمكنك اللعب بدون تسجيل في لعبة التوافق فقط"
        },
        {
            "icon": "🎨",
            "title": "المظهر",
            "text": "اكتب 'ثيمات' لتغيير الألوان واختيار المظهر المناسب لك"
        },
        {
            "icon": "👥",
            "title": "وضع الفريقين",
            "text": "في المجموعات، اكتب 'فريقين' للتبديل. سيتم تقسيم اللاعبين تلقائياً"
        },
        {
            "icon": "🏆",
            "title": "النقاط",
            "text": "احصل على نقطة واحدة لكل إجابة صحيحة. تابع تقدمك في 'نقاطي'"
        }
    ]
    
    help_cards = []
    for section in help_sections:
        help_cards.append(_3d_gradient_card([
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": section["icon"],
                        "size": "xl",
                        "flex": 0
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": section["title"],
                                "size": "sm",
                                "weight": "bold",
                                "color": c["primary"]
                            },
                            {
                                "type": "text",
                                "text": section["text"],
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "xs"
                            }
                        ],
                        "flex": 1,
                        "margin": "md"
                    }
                ]
            }
        ], theme, "14px", "sm"))
    
    body = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                _premium_header("❓ المساعدة", "دليل استخدام البوت", theme),
                
                *help_cards,
                
                _elegant_separator(theme),
                
                _3d_gradient_card([
                    {
                        "type": "text",
                        "text": "⚡ الأوامر السريعة",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["primary"]
                    },
                    {
                        "type": "text",
                        "text": "• بداية • ألعاب • نقاطي\n• صدارة • ثيمات • مساعدة\n• انضم • انسحب • إيقاف",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    }
                ], theme, "14px"),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "lg",
                    "contents": [
                        _3d_button("🏠 البداية", "بداية", "primary", theme),
                        _3d_button("🎮 الألعاب", "ألعاب", "secondary", theme)
                    ]
                },
                
                _elegant_separator(theme),
                
                {
                    "type": "text",
                    "text": BOT_RIGHTS,
                    "size": "xxs",
                    "color": c["text3"],
                    "align": "center"
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="المساعدة", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


# ============================================================================
# رسائل إضافية
# ============================================================================

def build_winner_announcement(username, game_name, round_points, total_points, theme=DEFAULT_THEME):
    """إعلان فوز احترافي"""
    c = _colors(theme)
    
    body = {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🎉",
                    "size": "xxl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "مبروك!",
                    "size": "xxl",
                    "weight": "bold",
                    "align": "center",
                    "color": c["success"],
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": username,
                    "size": "lg",
                    "weight": "bold",
                    "color": c["text"],
                    "align": "center",
                    "margin": "sm"
                },
                
                _elegant_separator(theme),
                
                _stat_card("النقاط", f"+{round_points}", "🏆", "primary", theme),
                
                {
                    "type": "text",
                    "text": f"الإجمالي: {total_points} نقطة",
                    "size": "sm",
                    "color": c["text2"],
                    "align": "center",
                    "margin": "md",
                    "weight": "bold"
                },
                
                _elegant_separator(theme),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "md",
                    "contents": [
                        _3d_button("🔄 إعادة", game_name, "primary", theme),
                        _3d_button("🛑 إيقاف", "إيقاف", "secondary", theme)
                    ]
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="فوز", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


def build_team_game_end(team_points, theme=DEFAULT_THEME):
    """نهاية لعبة الفريقين"""
    c = _colors(theme)
    t1, t2 = team_points.get("team1", 0), team_points.get("team2", 0)
    
    if t1 > t2:
        winner = "🥇 الفريق الأول"
        winner_color = "success"
    elif t2 > t1:
        winner = "🥇 الفريق الثاني"
        winner_color = "success"
    else:
        winner = "🤝 تعادل"
        winner_color = "info"
    
    body = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                _premium_header("⚡ انتهت اللعبة", None, theme),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        _stat_card("الفريق 1", t1, "🔵", "primary", theme),
                        {
                            "type": "text",
                            "text": "VS",
                            "size": "xl",
                            "color": c["text2"],
                            "align": "center",
                            "weight": "bold",
                            "flex": 0,
                            "gravity": "center"
                        },
                        _stat_card("الفريق 2", t2, "🔴", "secondary", theme)
                    ],
                    "spacing": "sm",
                    "margin": "lg"
                },
                
                _elegant_separator(theme),
                
                _info_badge(winner, winner_color, theme),
                
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "xl",
                    "contents": [
                        _3d_button("🎮 ألعاب", "ألعاب", "primary", theme),
                        _3d_button("🏠 رجوع", "بداية", "secondary", theme)
                    ]
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": c["bg"]
        }
    }
    
    msg = FlexMessage(alt_text="نتيجة", contents=FlexContainer.from_dict(body))
    msg.quick_reply = build_games_quick_reply()
    return msg


def build_games_quick_reply():
    """Quick Reply للألعاب"""
    return QuickReply(items=[QuickReplyItem(action=MessageAction(label=i["label"], text=i["text"])) for i in FIXED_GAME_QR])


def attach_quick_reply(m):
    """إضافة Quick Reply"""
    if m and hasattr(m, 'quick_reply'):
        m.quick_reply = build_games_quick_reply()
    return m


# رسائل نصية بسيطة
def build_registration_status(username, points, theme=DEFAULT_THEME):
    return TextMessage(text=f"✅ تم التسجيل بنجاح\n\n👤 الاسم: {username}\n🏆 النقاط: {points}\n\nابدأ اللعب الآن!")

def build_registration_required(theme=DEFAULT_THEME):
    return TextMessage(text="⚠️ التسجيل مطلوب\n\nاكتب: انضم")

def build_unregister_confirmation(username, points, theme=DEFAULT_THEME):
    return TextMessage(text=f"👋 تم الانسحاب\n\n📊 نقاطك النهائية: {points}")

def build_error_message(error_text, theme=DEFAULT_THEME):
    return TextMessage(text=f"❌ خطأ: {error_text}")

def build_game_stopped(game_name, theme=DEFAULT_THEME):
    return TextMessage(text=f"🛑 تم إيقاف {game_name}")

def build_theme_selector(theme=DEFAULT_THEME):
    return build_enhanced_home("مستخدم", 0, True, theme, "فردي")

def build_answer_feedback(message, theme=DEFAULT_THEME):
    return TextMessage(text=message)


__all__ = [
    'build_enhanced_home',
    'build_games_menu', 
    'build_my_points',
    'build_leaderboard',
    'build_help_window',
    'build_registration_status',
    'build_registration_required',
    'build_unregister_confirmation',
    'build_winner_announcement',
    'build_theme_selector',
    'attach_quick_reply',
    'build_error_message',
    'build_game_stopped',
    'build_team_game_end',
    'build_answer_feedback'
]
