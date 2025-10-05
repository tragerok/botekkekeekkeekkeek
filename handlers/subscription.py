from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.main_menu import get_main_menu
from utils.db import get_user, get_all_programs, add_license, get_all_tariffs
from utils.locale import L

class SubscriptionState(StatesGroup):
    choose_program = State()
    choose_tariff = State()
    enter_hwid = State()

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_buy", "ru"), L("main_menu_buy", "en")])
    async def start_subscription(message: types.Message):
        user_id = message.from_user.id
        user = get_user(user_id)
        lang = user.get('lang', 'ru')
        programs = get_all_programs()
        if not programs:
            await message.answer("Нет доступных программ." if lang == "ru" else "No available programs.")
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for prog in programs:
            kb.add(types.InlineKeyboardButton(f"🛡 {prog['name']}", callback_data=f"sub_prog_{prog['id']}"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="sub_back"))
        await message.answer("Выберите программу:" if lang == "ru" else "Choose program:", reply_markup=kb)
        await SubscriptionState.choose_program.set()

    @dp.callback_query_handler(lambda cb: cb.data.startswith("sub_prog_"), state=SubscriptionState.choose_program)
    async def program_select_cb(cb: types.CallbackQuery, state: FSMContext):
        program_id = int(cb.data.replace("sub_prog_", ""))
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        tariffs = get_all_tariffs(program_id)
        kb = types.InlineKeyboardMarkup(row_width=1)
        for tariff in tariffs:
            kb.add(types.InlineKeyboardButton(f"{tariff['name']} — {tariff['price']}$", callback_data=f"tariff_{tariff['id']}"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="sub_back"))
        await cb.message.edit_text("Выберите тариф:" if lang == "ru" else "Choose tariff:", reply_markup=kb)
        await state.set_state(SubscriptionState.choose_tariff.state)
        await state.update_data(program_id=program_id)
        await cb.answer()

    @dp.callback_query_handler(lambda cb: cb.data.startswith("tariff_"), state=SubscriptionState.choose_tariff)
    async def tariff_select_cb(cb: types.CallbackQuery, state: FSMContext):
        tariff_id = int(cb.data.replace("tariff_", ""))
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        await cb.message.edit_text(
            "Введите HWID (идентификатор устройства):" if lang == "ru" else "Enter your HWID:"
        )
        await state.set_state(SubscriptionState.enter_hwid.state)
        await state.update_data(tariff_id=tariff_id)
        await cb.answer()

    @dp.message_handler(state=SubscriptionState.enter_hwid)
    async def enter_hwid_step(message: types.Message, state: FSMContext):
        data = await state.get_data()
        program_id = data.get('program_id')
        tariff_id = data.get('tariff_id')
        hwid = message.text
        add_license(message.from_user.id, program_id, tariff_id, hwid)
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        await message.answer(L("buy_success", lang), reply_markup=get_main_menu(message.from_user.id))
        await state.finish()

    @dp.callback_query_handler(lambda cb: cb.data == "sub_back", state="*")
    async def sub_back_callback(cb: types.CallbackQuery, state: FSMContext):
        await cb.message.answer("Главное меню.", reply_markup=get_main_menu(cb.from_user.id))
        await state.finish()
        await cb.answer()
