import os

# Токен можно задать через переменную окружения BOT_TOKEN,
# либо просто вписать его сюда вместо строки ниже.
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER")

# Путь к файлу базы данных SQLite
DB_PATH = os.getenv("DB_PATH", "dating_bot.db")
