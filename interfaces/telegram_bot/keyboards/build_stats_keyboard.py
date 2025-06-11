from telethon import Button, events
from telethon.errors import MessageNotModifiedError
from interfaces.telegram_bot.keyboards.common_keyboard import default_nav_buttons_keyboard


DEFAULT_PARSE_MODE = "html"

async def after_click_stats_expense_keyboard(event: events.CallbackQuery.Event):
    text = "Выберите период:"
    buttons = [
        [Button.inline("📅 Сегодня", data=b"stats:day")],
        [Button.inline("📆 Эта неделя", data=b"stats:week")],
        [Button.inline("🗓️ Этот месяц", data=b"stats:month")],
        [Button.inline("↩️ Назад", b"back")]
    ]
    return await event.edit(text, buttons=buttons)


# TODO: пересмотреть везде эти три кнопки, возможно добавлять их из default_nav_buttons
# и обрабатывать кнопку Назад
async def expense_history_keyboard_keyboard(event: events.CallbackQuery.Event):
    """Тут после нажатия на История трат."""
    text = "📊 Выберите период для просмотра истории расходов:"
    buttons = [
        [Button.inline("📅 По дням", b"history:day"), Button.inline("🗓️ По неделям", b"history:week")],
        [Button.inline("📆 По месяцам", b"history:month"), Button.inline("🗃️ По годам", b"history:year")],
        [Button.inline("🏠 На главную", b"home")]
    ]
    try:
        return await event.edit(text=text, buttons=buttons)
    except MessageNotModifiedError:
        pass


async def after_expense_history_period_keyboard(event: events.CallbackQuery.Event, text: list[str]):
    """Тут после нажанития на период истории трат."""
    await event.edit(
            "\n\u200b".join(text),
            buttons=await default_nav_buttons_keyboard(back="history"),
            parse_mode=DEFAULT_PARSE_MODE
        )

