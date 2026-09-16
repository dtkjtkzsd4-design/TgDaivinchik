from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from states import SettingsStates

router = Router()


@router.message(F.text == "⚙️ Настройки поиска")
async def settings_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай анкету через /start")
        return

    mode_label = "🏙 Только мой город" if user["search_mode"] == "city" else "🌍 Все города"
    await message.answer(
        "⚙️ <b>Твои настройки поиска:</b>\n\n"
        f"Режим: {mode_label}\n"
        f"Возраст партнёра: {user['min_age']}–{user['max_age']}",
        reply_markup=kb.settings_kb(user["search_mode"]),
    )


@router.callback_query(F.data.startswith("setmode:"))
async def set_mode(callback: CallbackQuery):
    mode = callback.data.split(":")[1]
    await db.update_field(callback.from_user.id, "search_mode", mode)
    mode_label = "🏙 Мой город" if mode == "city" else "🌍 Все города"
    await callback.message.edit_text(f"✅ Режим поиска изменён на: {mode_label}")
    await callback.answer()


@router.callback_query(F.data == "setage")
async def set_age_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.age_range)
    await callback.message.answer("Введи диапазон возраста через дефис, например: 20-30")
    await callback.answer()


@router.message(SettingsStates.age_range)
async def set_age_range(message: Message, state: FSMContext):
    try:
        min_a, max_a = (int(x) for x in message.text.replace(" ", "").split("-"))
        if not (14 <= min_a <= max_a <= 100):
            raise ValueError
    except Exception:
        await message.answer("Формат неверный. Пример: 20-30 (значения от 14 до 100).")
        return

    await db.update_field(message.from_user.id, "min_age", min_a)
    await db.update_field(message.from_user.id, "max_age", max_a)
    await state.clear()
    await message.answer("✅ Возрастной диапазон обновлён!", reply_markup=kb.main_menu())
