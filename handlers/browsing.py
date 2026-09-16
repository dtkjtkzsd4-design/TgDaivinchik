from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb

router = Router()


async def send_profile_card(message: Message, user_id: int):
    profile = await db.get_next_profile(user_id)
    if not profile:
        await message.answer(
            "😕 Анкет больше нет.\n"
            "Попробуй позже или расширь поиск в «⚙️ Настройки поиска» "
            "(например, включи «🌍 Все города»)."
        )
        return
    await message.answer_photo(
        profile["photo_id"],
        caption=kb.profile_caption(profile),
        reply_markup=kb.browse_kb(profile["user_id"]),
    )


@router.message(F.text == "🔍 Смотреть анкеты")
async def browse(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай анкету через /start")
        return
    await send_profile_card(message, message.from_user.id)


@router.callback_query(F.data.startswith("like:"))
async def like_profile(callback: CallbackQuery, bot: Bot):
    target_id = int(callback.data.split(":")[1])
    is_match = await db.add_like(callback.from_user.id, target_id, "like")

    try:
        await callback.message.delete()
    except Exception:
        pass

    if is_match:
        me = await db.get_user(callback.from_user.id)
        other = await db.get_user(target_id)
        await notify_match(bot, me, other)
        await callback.answer("Это взаимно! 🎉", show_alert=True)
    else:
        await callback.answer("Лайк отправлен ❤️")

    await send_profile_card(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("dislike:"))
async def dislike_profile(callback: CallbackQuery):
    target_id = int(callback.data.split(":")[1])
    await db.add_like(callback.from_user.id, target_id, "dislike")
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Пропущено")
    await send_profile_card(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("complain:"))
async def complain_profile(callback: CallbackQuery):
    target_id = int(callback.data.split(":")[1])
    await db.add_block(callback.from_user.id, target_id)
    await db.add_like(callback.from_user.id, target_id, "dislike")
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Жалоба отправлена, анкета скрыта")
    await send_profile_card(callback.message, callback.from_user.id)


async def notify_match(bot: Bot, user_a: dict, user_b: dict):
    for me, other in ((user_a, user_b), (user_b, user_a)):
        if other.get("username"):
            contact = f"👉 @{other['username']}"
        else:
            contact = f'👉 <a href="tg://user?id={other["user_id"]}">Написать</a>'
        try:
            await bot.send_photo(
                me["user_id"],
                other["photo_id"],
                caption=(
                    "🎉 <b>Взаимная симпатия!</b>\n\n"
                    f"Тебе понравился(-ась) <b>{other['name']}</b>, и ты понравился(-ась) в ответ!\n\n"
                    f"{contact}"
                ),
            )
        except Exception:
            pass
