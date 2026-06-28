import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db
from handlers import start, writing, quiz, progress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    # Init DB
    await db.init_db()
    logger.info("✅ Database initialized")

    # Init bot
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(writing.router)
    dp.include_router(quiz.router)
    dp.include_router(progress.router)

    logger.info("🤖 Bot starting...")
    logger.info("✅ Akbar's IELTS Bot is running!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
