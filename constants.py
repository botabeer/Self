COLORS = {
    'primary': '#6B9BD1',
    'primary_dark': '#4A7BA7',
    'background': '#F5F7FA',
    'background_light': '#FFFFFF',
    'card_bg': '#FFFFFF',
    'text': '#2C3E50',
    'white': '#FFFFFF',
    'text_secondary': '#7F8C8D',
    'text_light': '#95A5A6',
    'text_dark': '#2C3E50',
    'text2': '#7F8C8D',
    'text3': '#95A5A6',
    'success': '#52C5B6',
    'warning': '#F39C6B',
    'error': '#E17B7B',
    'info': '#6B9BD1',
    'border': '#E8ECEF',
    'progress_bg': '#E8ECEF',
    'progress_fill': '#6B9BD1',
    'glow': '#6B9BD1',
    'shadow': 'rgba(107, 155, 209, 0.15)',
    'card': '#FFFFFF',
    'bg': '#F5F7FA',
    'secondary': '#7F8C8D'
}

THEMES = {
    'default': COLORS
}

DEFAULT_THEME = 'default'

POINTS = {
    'correct_answer': 1,
    'hint_used': 0,
    'show_answer': 0
}

QUESTIONS_PER_GAME = 5

MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 20,
    'roles': {
        'mafia': 1,
        'detective': 1,
        'doctor': 1,
        'citizen': 'remaining'
    },
    'phases': ['registration', 'night', 'day', 'voting', 'ended'],
    'night_duration': 60,
    'day_duration': 120,
    'voting_duration': 60
}

INACTIVITY_DAYS = 7
