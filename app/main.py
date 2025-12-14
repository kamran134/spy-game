import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.database.database import init_db, close_db
from app.bot.handlers import admin, game, user
from app.bot.middlewares.database import DatabaseMiddleware
from app.bot.middlewares.i18n import I18nMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    
    # Initialize database
    await init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register middlewares
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(I18nMiddleware())
    
    # Register routers
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(game.router)
    
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
