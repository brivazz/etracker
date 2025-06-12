from telethon import Button
from telethon.errors import MessageNotModifiedError
from config import logger


# CATEGORIES = {
#     "🍔 Еда": "food",
#     "🚗 Транспорт": "transport",
#     "🚕 Такси", b"cat_taxi",
#     "🎮 Развлечения": "entertainment",
#     "🧾 Другое": "other",
#     "💊 Аптека": b"cat_apteka"
# }

MAIN_MENU_TEXT = "Привет {}! Что хотите сделать?"


async def show_error_keyboard(event, text: str, input_message_id: int | None = None):

    try:
        if input_message_id:
            # Пробуем отредактировать сообщение с указанным ID
            await event.client.edit_message(
                entity=event.chat_id,
                message=input_message_id,
                text=f"❗ {text}",
                buttons=await default_nav_buttons_keyboard(),
            )
        elif hasattr(event, "edit"):
            # Если это callback, и можно редактировать сообщение бота
            await event.edit(f"❗ {text}", buttons=await default_nav_buttons_keyboard())
        elif hasattr(event, "respond"):
            # Просто отправляем сообщение в чат
            await event.respond(
                f"❗ {text}", buttons=await default_nav_buttons_keyboard()
            )
        else:
            # Последняя попытка — alert
            await event.answer(f"❗ {text}", alert=True)
    except Exception as e:
        logger.warning(f"Ошибка: {e}")


async def default_nav_buttons_keyboard(back: str = "back"):
    return [
        [Button.inline("↩️ Назад", back)],
        [Button.inline("🏠 На главную", b"home")],
    ]


async def main_menu_keyboard():
    """Меню после нажатия кнопки старт"""
    return [
        [Button.inline("➕ Добавить трату", b"add_expense")],
        [
            Button.inline("📊 Статистика", b"stats_expense"),
            Button.inline("📄 История трат", b"history"),
        ],
        [
            Button.inline("🔁 Повторить последнюю", b"repeat_expense"),
            Button.inline("✏️ Редактировать последнюю", b"edit_expense"),
        ],
        [Button.inline("🗑 Удалить последнюю", b"delete_expense")],
    ]
