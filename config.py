import os

# Токен твоего бота от BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8636197495:AAEjFAafZLOWeGUc76QBHJiUyoA9PZRGue8")

# Telegram ID пользователей, которым разрешен доступ (ваш с мужем ID)
ALLOWED_USERS = [
    216669280,  # Замени на свой Telegram ID
    7405942744   # Замени на Telegram ID мужа
]

# Путь к базе данных
DB_PATH = "date_ideas.db"