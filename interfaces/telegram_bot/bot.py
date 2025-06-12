import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.updates import GetStateRequest

from config import settings, logger
from interfaces.telegram_bot.router import router
from interfaces.telegram_bot.utils.inject_user_context import inject_user

client: TelegramClient | None = None
router.use(inject_user())  # Применится ко всем обработчикам


async def run_bot():
    global client
    stop_event = asyncio.Event()

    while not stop_event.is_set():
        try:
            client = TelegramClient(
                "bot",
                api_id=settings.tg_api_id,
                api_hash=settings.tg_api_hash,
                connection_retries=9999,
                retry_delay=5,
            )

            handlers_path = Path(__file__).parent / "handlers"
            router.autoimport(handlers_path)
            await router.register(client)

            await client.start(bot_token=settings.tg_bot_token)
            logger.info("✅ Бот запущен!")

            asyncio.create_task(keep_alive(client, stop_event))

            await client.run_until_disconnected()

        except Exception as e:
            logger.exception(f"❌ Ошибка соединения или работы бота: {e}")
            await asyncio.sleep(5)
        finally:
            if client and client.is_connected():
                await client.disconnect()
            stop_event.set()


async def keep_alive(client: TelegramClient, stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            await client(GetStateRequest())
            logger.debug("✅ keep_alive: соединение активно")
        except Exception as e:
            logger.warning(f"⚠️ keep_alive: {e}")
        await asyncio.sleep(30)
