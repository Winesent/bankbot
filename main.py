import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config
from database.db import init_db
from handlers.user import router as user_router
from handlers.admin import router as admin_router

async def main():
    # Инициализация БД
    init_db()

    # Создаем бота и диспетчер
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties())
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())