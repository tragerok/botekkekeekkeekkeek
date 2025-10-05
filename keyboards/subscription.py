from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.locale import L

def get_programs_keyboard(programs, lang="ru"):
    kb = InlineKeyboardMarkup(row_width=1)
    for prog in programs:
        kb.add(InlineKeyboardButton(f"🛡 {prog['name']}", callback_data=f"sub_prog_{prog['id']}"))
    kb.add(InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="sub_back"))
    return kb

def get_tariffs_keyboard(tariffs, lang="ru"):
    kb = InlineKeyboardMarkup(row_width=1)
    for t in tariffs:
        kb.add(InlineKeyboardButton(f"{t['name']} — {t['price']}$", callback_data=f"tariff_{t['id']}"))
    kb.add(InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="sub_back_to_programs"))
    return kb

def get_hwid_keyboard(lang="ru"):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="sub_back_to_tariffs"))
    return kb
