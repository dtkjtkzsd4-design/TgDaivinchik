from aiogram import Router, F
from aiogram.types import Message

import database as db
import keyboards as kb

router = Router()


@router.message(F.text == "👤 Моя анкета")
async def my_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("У тебя ещё нет анкеты. Введи /start, чтобы создать её.")
        return

    stats = await db.get_stats(message.from_user.id)
    caption = (
        kb.profile_caption(user)
        + f"\n\n❤️ Лайков получено: {stats['likes_received']}"
        + f"\n💞 Мэтчей: {stats['matches']}"
    )
    await message.answer_photo(
        user["photo_id"],
        caption=caption,
        reply_markup=kb.my_profile_kb(),
    )


@router.message(F.text == "❓ Помощь")
async def help_cmd(message: Message):
    await message.answer(
        "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
        "🔍 <b>Смотреть анкеты</b> — искать людей рядом или по всему миру\n"
        "❤️ — поставить лайк, если анкета понравилась\n"
        "👎 — пропустить анкету\n"
        "⚠️ — пожаловаться (анкета скроется от тебя)\n\n"
        "❤️ <b>Кто меня лайкнул</b> — список тех, кому ты уже понравился(-ась)\n"
        "✏️ <b>Изменить анкету</b> — обновить имя, фото, возраст, описание и т.д.\n"
        "⚙️ <b>Настройки поиска</b> — искать только в своём городе или по всему миру, "
        "задать возрастной диапазон\n\n"
        "При взаимном лайке бот пришлёт вам контакт друг друга 💌"
    )
