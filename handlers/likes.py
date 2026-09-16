from aiogram import Router, F
from aiogram.types import Message

import database as db
import keyboards as kb

router = Router()


@router.message(F.text == "❤️ Кто меня лайкнул")
async def who_liked(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай анкету через /start")
        return

    pending = await db.get_pending_likes(message.from_user.id)
    if not pending:
        await message.answer(
            "Пока никто не оценил твою анкету 💤\n"
            "Смотри больше анкет сам(а) — так тебя увидит больше людей!"
        )
        return

    await message.answer(f"У тебя {len(pending)} новых симпатий! Смотрим первую 👀")
    profile = pending[0]
    await message.answer_photo(
        profile["photo_id"],
        caption=kb.profile_caption(profile),
        reply_markup=kb.browse_kb(profile["user_id"]),
    )
