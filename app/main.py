import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import get_settings
from app.handlers import router


async def main() -> None:
    settings = get_settings()

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await bot.delete_webhook(
        drop_pending_updates=True,
    )

    logging.info("XJ SlimWell bot ishga tushdi.")

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
