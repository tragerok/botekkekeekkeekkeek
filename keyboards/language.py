from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_language_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Русский 🇷🇺"))
    kb.add(KeyboardButton("English 🇬🇧"))
    return kb
