import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError
from config import settings, logger
from interfaces.telegram_bot.router import router
from pathlib import Path
from interfaces.telegram_bot.utils.inject_user_context import inject_user

client: TelegramClient | None = None

async def run_bot():
    global client
    stop_event = asyncio.Event()

    client = TelegramClient(
        "bot",
        api_id=settings.tg_api_id,
        api_hash=settings.tg_api_hash,
        connection_retries=9999,
        retry_delay=5
    )

    # Применяем middleware ДО импорта хендлеров
    router.use(inject_user())  # Применится ко всем обработчикам

    handlers_path = Path(__file__).parent / "handlers"
    router.autoimport(handlers_path)
    await router.register(client)

    await client.start(bot_token=settings.tg_bot_token)  # type: ignore
    logger.info("✅ Бот запущен!")

    # Запускаем heartbeat
    heartbeat_task = asyncio.create_task(heartbeat(stop_event))

    try:
        await client.run_until_disconnected()  # type: ignore
    except RPCError as e:
        logger.exception("❌ RPCError: %s", e)
    except (ConnectionError, OSError) as e:
        logger.exception("❌ Потеря соединения: %s", e)
    except Exception as e:
        logger.exception("❌ Необработанная ошибка: %s", e)
    finally:
        await shutdown(stop_event)
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            logger.debug("✅ Heartbeat завершён")


async def heartbeat(stop_event: asyncio.Event):
    while not stop_event.is_set():
        logger.debug("💓 Heartbeat: бот активен")
        await asyncio.sleep(60)


async def shutdown(stop_event: asyncio.Event):
    if client and client.is_connected():
        logger.info("⛔ Отключение клиента Telegram...")
        await client.disconnect()  # type: ignore
    stop_event.set()
