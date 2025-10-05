from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.main_menu import get_main_menu
from utils.db import get_user, get_licenses_for_user, renew_license, get_balance, update_balance, get_all_tariffs, get_tariff_by_id
from utils.locale import L

class LicenseRenewState(StatesGroup):
    waiting_for_license = State()
    waiting_for_tariff = State()

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_renew", "ru"), L("main_menu_renew", "en")])
    async def choose_license(message: types.Message):
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        licenses = get_licenses_for_user(message.from_user.id, only_active=True)
        if not licenses:
            await message.answer("У вас нет активных лицензий." if lang == "ru" else "You have no active licenses.")
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for lic in licenses:
            txt = f"{lic['program_name']} ({L('until', lang)} {lic['valid_until'].strftime('%d.%m.%Y')})"
            kb.add(types.InlineKeyboardButton(txt, callback_data=f"renew_{lic['id']}"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="renew_cancel"))
        await message.answer("Выберите лицензию для продления:" if lang == "ru" else "Choose a license to renew:", reply_markup=kb)
        await LicenseRenewState.waiting_for_license.set()

    @dp.callback_query_handler(lambda c: c.data == "renew_cancel", state="*")
    async def renew_back_handler(cb: types.CallbackQuery, state: FSMContext):
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        await cb.message.edit_text(
            "Главное меню." if lang == "ru" else "Main menu.",
            reply_markup=get_main_menu(cb.from_user.id)
        )
        await state.finish()
        await cb.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("renew_"), state=LicenseRenewState.waiting_for_license)
    async def select_tariff(cb: types.CallbackQuery, state: FSMContext):
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        license_id = int(cb.data.split("_")[1])
        await state.update_data(license_id=license_id)
        tariffs = get_all_tariffs()
        kb = types.InlineKeyboardMarkup(row_width=1)
        for t in tariffs:
            kb.add(types.InlineKeyboardButton(
                f"{t['name']} — {t['price']}$", callback_data=f"tariff_{t['id']}"
            ))
        kb.add(types.InlineKeyboardButton("⬅️ Назад" if lang == "ru" else "⬅️ Back", callback_data="renew_choose_license"))
        await cb.message.edit_text("Выберите тариф для продления:" if lang == "ru" else "Choose a renewal plan:", reply_markup=kb)
        await LicenseRenewState.waiting_for_tariff.set()
        await cb.answer()

    @dp.callback_query_handler(lambda c: c.data == "renew_choose_license", state=LicenseRenewState.waiting_for_tariff)
    async def back_to_choose_license(cb: types.CallbackQuery, state: FSMContext):
        # Возврат к выбору лицензии
        await choose_license(cb.message)

    @dp.callback_query_handler(lambda c: c.data.startswith("tariff_"), state=LicenseRenewState.waiting_for_tariff)
    async def do_renew(cb: types.CallbackQuery, state: FSMContext):
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        tid = int(cb.data.split("_")[1])
        tariff = get_tariff_by_id(tid)
        add_days = tariff['days']
        price = tariff['price']
        balance = get_balance(cb.from_user.id)
        if balance < price:
            await cb.message.edit_text(
                f"Недостаточно средств!\nВаш баланс: {balance}$, цена: {price}$" if lang == "ru" 
                else f"Not enough funds!\nYour balance: {balance}$, price: {price}$"
            )
            await state.finish()
            await cb.answer()
            return
        data = await state.get_data()
        new_until = renew_license(data['license_id'], add_days)
        update_balance(cb.from_user.id, -price)
        new_balance = get_balance(cb.from_user.id)
        await cb.message.edit_text(
            (f"✅ Лицензия успешно продлена до {new_until.strftime('%d.%m.%Y')}.\n"
             f"💰 Новый баланс: {new_balance}$")
            if lang == "ru" else
            (f"✅ License renewed until {new_until.strftime('%d.%m.%Y')}.\n"
             f"💰 New balance: {new_balance}$")
        )
        await state.finish()
        await cb.answer()
