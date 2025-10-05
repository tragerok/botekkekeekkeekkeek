from aiogram import types
from keyboards.main_menu import get_main_menu
from keyboards.language import get_language_keyboard
from utils.db import get_user, set_lang
from utils.locale import L

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_language", "ru"), L("main_menu_language", "en")])
    async def choose_language(message: types.Message):
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        await message.answer(
            "Выберите язык:" if lang == "ru" else "Choose language:",
            reply_markup=get_language_keyboard()
        )

    @dp.message_handler(lambda msg: msg.text in ["Русский 🇷🇺", "English 🇬🇧"])
    async def set_language(message: types.Message):
        lang_code = "ru" if message.text == "Русский 🇷🇺" else "en"
        set_lang(message.from_user.id, lang_code)
        await message.answer(
            "Язык изменён!" if lang_code == "ru" else "Language updated!",
            reply_markup=get_main_menu(message.from_user.id)
        )
