import asyncio
import sys

from infrastructure.db.sqlalchemy.sqlalchemy_async_session import database
from config import logger
from interfaces.telegram_bot.bot import run_bot


async def main():
    if not await database.check_connection():
        raise RuntimeError("Не удалось подключиться к БД")

    await database.create_database()
    # import sys
    # print(sys.path)
    try:
        await run_bot()
    finally:
        logger.info("🛑 Бот завершил работу")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🧹 Завершение по Ctrl+C")
        sys.exit(0)
    except Exception:
        logger.exception("💥 Необработанная ошибка")
        sys.exit(1)
