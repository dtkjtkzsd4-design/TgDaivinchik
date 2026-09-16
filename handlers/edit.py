from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from states import EditProfile

router = Router()

FIELD_PROMPTS = {
    "name": "Введи новое имя:",
    "age": "Введи новый возраст (14-100):",
    "city": "Введи новый город:",
    "about": "Напиши новый текст о себе:",
}


@router.message(F.text == "✏️ Изменить анкету")
async def edit_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай анкету через /start")
        return
    await message.answer("Что хочешь изменить?", reply_markup=kb.edit_kb())


@router.callback_query(F.data == "goto_edit")
async def goto_edit(callback: CallbackQuery):
    await callback.message.answer("Что хочешь изменить?", reply_markup=kb.edit_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("edit:"))
async def edit_field_choose(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]

    if field == "gender":
        await callback.message.edit_text("Выбери свой пол:")
        await callback.message.answer("👇", reply_markup=kb.gender_kb(prefix="setgender"))
        await callback.answer()
        return

    if field == "looking_for":
        await callback.message.edit_text("Кого хочешь найти?")
        await callback.message.answer("👇", reply_markup=kb.looking_for_kb(prefix="setlf"))
        await callback.answer()
        return

    if field == "photo":
        await state.set_state(EditProfile.value)
        await state.update_data(field="photo")
        await callback.message.answer("Пришли новое фото:")
        await callback.answer()
        return

    await state.set_state(EditProfile.value)
    await state.update_data(field=field)
    await callback.message.answer(FIELD_PROMPTS[field])
    await callback.answer()


@router.callback_query(F.data.startswith("setgender:"))
async def set_gender(callback: CallbackQuery):
    gender = callback.data.split(":")[1]
    await db.update_field(callback.from_user.id, "gender", gender)
    await callback.message.edit_text("✅ Пол обновлён")
    await callback.answer()


@router.callback_query(F.data.startswith("setlf:"))
async def set_looking_for(callback: CallbackQuery):
    looking_for = callback.data.split(":")[1]
    await db.update_field(callback.from_user.id, "looking_for", looking_for)
    await callback.message.edit_text("✅ Предпочтения по поиску обновлены")
    await callback.answer()


@router.message(EditProfile.value, F.photo)
async def set_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("field") != "photo":
        return
    await db.update_field(message.from_user.id, "photo_id", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Фото обновлено!", reply_markup=kb.main_menu())


@router.message(EditProfile.value)
async def set_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")

    if field == "photo":
        await message.answer("Пришли именно фотографию 📸")
        return

    if not message.text:
        await message.answer("Отправь текстовое значение.")
        return

    value = message.text.strip()

    if field == "age":
        if not value.isdigit() or not (14 <= int(value) <= 100):
            await message.answer("Введи возраст цифрами (от 14 до 100).")
            return
        value = int(value)
    else:
        if not (1 <= len(value) <= 500):
            await message.answer("Слишком длинный или пустой текст (максимум 500 символов).")
            return

    await db.update_field(message.from_user.id, field, value)
    await state.clear()
    await message.answer("✅ Анкета обновлена!", reply_markup=kb.main_menu())
