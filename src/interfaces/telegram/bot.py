import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.core.settings import settings
from src.interfaces.telegram.handlers.start import start_router
from src.interfaces.telegram.handlers.music import music_router
from src.interfaces.telegram.handlers.admin_full import admin_full_router
from src.interfaces.telegram.middlewares.security import AntiSpamMiddleware
from src.core.events import event_bus

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # میدلور امنیتی
    dp.message.middleware(AntiSpamMiddleware())
    dp.callback_query.middleware(AntiSpamMiddleware())

    # روترها
    dp.include_router(start_router)
    dp.include_router(music_router)
    dp.include_router(admin_full_router)

    # task پردازش رویدادها
    asyncio.create_task(event_bus.process_events())

    if settings.TELEGRAM_WEBHOOK_URL:
        await dp.start_webhook(bot, webhook_url=settings.TELEGRAM_WEBHOOK_URL)
    else:
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
