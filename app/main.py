import asyncio
import logging

from app.database.db import init_db
from app.handlers import router
from app.loader import bot, dispatcher


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    await init_db()

    dispatcher.include_router(router)

    await bot.delete_webhook(
        drop_pending_updates=True,
    )

    logging.info("XJ SlimWell bot ishga tushdi.")

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

