from telethon import events

from interfaces.telegram_bot.keyboards.common_keyboard import default_nav_buttons_keyboard

async def add_category_keyboard(event: events.CallbackQuery.Event, input_message_id: int| None = None):
    """Тут после нажатия Добавить категорию."""
    text = "Введите название новой категории:"
    if input_message_id:
        await event.client.edit_message(
                    entity=event.chat_id,
                    message=input_message_id,
                    text=text,
                    buttons=await default_nav_buttons_keyboard()
                )
        return
    await event.edit(text, buttons=await default_nav_buttons_keyboard())

async def after_add_new_category_keyboard(event: events.NewMessage.Event, category_name, input_message_id):
    """Тут после успешного добавления новой категории."""
    text = f"✅ Категория «{category_name.upper()}» добавлена. Введите сумму:"
    await event.client.edit_message(
        entity=event.chat_id,
        message=input_message_id,
        text=text,
        buttons=await default_nav_buttons_keyboard()
    )


