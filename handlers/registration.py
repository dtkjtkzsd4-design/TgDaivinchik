from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from states import Registration

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    if user and user["is_active"]:
        await message.answer(
            f"С возвращением, {user['name']}! 👋\nВыбирай, что делать дальше:",
            reply_markup=kb.main_menu(),
        )
        return

    await state.set_state(Registration.name)
    await message.answer(
        "💘 <b>Добро пожаловать в бот знакомств!</b>\n\n"
        "Здесь можно найти новых друзей и вторую половинку — в своём городе "
        "или по всему миру.\n\nДавай создадим твою анкету ✨\n\n"
        "Как тебя зовут?",
        reply_markup=kb.remove(),
    )


@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
    if not message.text or not (1 <= len(message.text.strip()) <= 50):
        await message.answer("Введи имя текстом (до 50 символов).")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(Registration.age)
    await message.answer("Сколько тебе лет?")


@router.message(Registration.age)
async def reg_age(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit() or not (14 <= int(message.text) <= 100):
        await message.answer("Введи возраст цифрами (от 14 до 100).")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(Registration.gender)
    await message.answer("Укажи свой пол:", reply_markup=kb.gender_kb())


@router.callback_query(Registration.gender, F.data.startswith("gender:"))
async def reg_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(Registration.looking_for)
    await callback.message.edit_text("А кого хочешь найти?")
    await callback.message.answer("Выбери вариант:", reply_markup=kb.looking_for_kb())
    await callback.answer()


@router.callback_query(Registration.looking_for, F.data.startswith("lf:"))
async def reg_looking_for(callback: CallbackQuery, state: FSMContext):
    looking_for = callback.data.split(":")[1]
    await state.update_data(looking_for=looking_for)
    await state.set_state(Registration.city)
    await callback.message.edit_text("Из какого ты города? ✍️")
    await callback.answer()


@router.message(Registration.city)
async def reg_city(message: Message, state: FSMContext):
    if not message.text or not (1 <= len(message.text.strip()) <= 50):
        await message.answer("Введи название города (до 50 символов).")
        return
    await state.update_data(city=message.text.strip())
    await state.set_state(Registration.about)
    await message.answer(
        "Расскажи немного о себе: увлечения, чем занимаешься, что ищешь 💬\n"
        "Это увидят другие пользователи в твоей анкете."
    )


@router.message(Registration.about)
async def reg_about(message: Message, state: FSMContext):
    if not message.text or not (1 <= len(message.text.strip()) <= 500):
        await message.answer("Напиши текст о себе (до 500 символов).")
        return
    await state.update_data(about=message.text.strip())
    await state.set_state(Registration.photo)
    await message.answer("Отлично! Теперь пришли своё фото для анкеты 📸")


@router.message(Registration.photo, F.photo)
async def reg_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    data["photo_id"] = photo_id

    await db.create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        looking_for=data["looking_for"],
        city=data["city"],
        about=data["about"],
        photo_id=photo_id,
    )
    await state.clear()

    await message.answer_photo(
        photo_id,
        caption="🎉 <b>Анкета создана!</b>\n\n" + kb.profile_caption(data),
    )
    await message.answer(
        "Теперь можешь искать знакомства 🔍",
        reply_markup=kb.main_menu(),
    )


@router.message(Registration.photo)
async def reg_photo_invalid(message: Message):
    await message.answer("Пожалуйста, пришли именно фотографию 📸")
