import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from config import BOT_TOKEN
from handlers import registration, browsing, likes, edit, settings, menu

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN or "ВСТАВЬ" in BOT_TOKEN:
        raise RuntimeError(
            "Не задан токен бота. Укажи его в config.py или через переменную окружения BOT_TOKEN."
        )

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок важен: сначала обработчики с FSM-состояниями и явными callback'ами,
    # текстовые пункты меню — в конце.
    dp.include_router(registration.router)
    dp.include_router(browsing.router)
    dp.include_router(likes.router)
    dp.include_router(edit.router)
    dp.include_router(settings.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
