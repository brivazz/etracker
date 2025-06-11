from typing import cast
from telethon import Button, events
from application.factories.uow_factories import get_uow
from application.main_orchestrator import MainOrchestrator
from application.dto.category_dto import CategoryInDBDTO
from application.dto.user_dto import UserIdDTO, UserInDBDTO
from application.commands.command_enum import Command
from telethon.tl.custom import Message
from interfaces.telegram_bot.keyboards.common_keyboard import default_nav_buttons_keyboard


SELECT_CATEGORY_TEXT = "Выберите категорию:"


async def expense_keyboard(user_id: int):
    """Тут после нажатия Добавить трату."""
    async with get_uow() as uow:
        main_orchestrator = MainOrchestrator(uow=uow)
        dto = UserIdDTO(user_id=user_id)
        categories = cast(list[CategoryInDBDTO], await main_orchestrator.handle_command(
            command=Command.GET_USER_CATEGORIES,
            dto=dto
        ))
    # Если категорий нет — предлагаем создать
    if not categories:
        return [
            [Button.inline("➕ Добавить категорию", b"add_category")],
            [Button.inline("🏠 На главную", b"home")]
        ], "У вас пока нет категорий. Добавьте хотя бы одну, чтобы фиксировать траты."
    # Иначе показываем категории
    buttons = [
        Button.inline(cat.name.upper(), f"cat_{cat.id}:{cat.name}".encode())
        for cat in categories
    ]
    grouped = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    # Добавляем кнопку "➕ Добавить категорию" отдельно
    grouped.append([Button.inline("➕ Добавить категорию", b"add_category")])
    grouped.append([Button.inline("↩️ Назад", b"back")])
    return grouped, SELECT_CATEGORY_TEXT


async def before_input_amount_keyboard(category_name: str):
    """Когда выбрали/нажали на категорию."""
    new_text = f"Вы выбрали категорию: **{category_name.upper()}**. Введите сумму траты:"
    new_buttons = await default_nav_buttons_keyboard()
    return new_text, new_buttons


async def before_save_amount_keyboard(event: events.NewMessage.Event, amount: float, category_name: str, input_message_id: int):
    """Перед сохранением/записью новой траты, когда написали сумму."""
    text = f"✔️Сумма: {amount:.2f} руб. | Категория: {category_name.upper()}"
    buttons=[
        [Button.inline("✏️ Изменить", b"change_expense"), Button.inline("❌️ Отменить", b"cancel")],
        [Button.inline("✅ Сохранить", b"save_expense")],
        [Button.inline("🏠 На главную", b"home"), Button.inline("↩️ Назад", b"back")]
    ]# + await default_nav_buttons_keyboard()
    await event.client.edit_message(entity=event.chat_id, message=input_message_id, text=text, buttons=buttons)
    return text, buttons


async def after_save_expense_keyboard(event: events.NewMessage.Event, amount: float, category_name: str, input_message_id: int):
    """После сохранения/записи новой траты, когда написали сумму."""
    text = f"✅Трата на {amount:.2f} ₽ сохранена в категорию {category_name.upper()}"
    buttons=[
        [Button.inline("🗑 Удалить", b"delete_expense")],
        [Button.inline("↩️ Назад", b"back")], [Button.inline("🏠 На главную", b"home")]]
    await event.client.edit_message(entity=event.chat_id, message=input_message_id, text=text, buttons=buttons)
    return text, buttons


async def edit_last_expense_keyboard(event: events.CallbackQuery.Event) -> Message:
    """Тут после нажатия на редактирование последней траты."""
    text = "Введите новую сумму для последней траты:"
    buttons = [
            Button.inline("🏠 На главную", b"home"),
            Button.inline("↩️ Назад", b"back"),
            Button.inline("❌ Отмена", b"cancel"),
        ]
    return await event.edit(text, buttons=buttons)


async def after_input_amount_for_edit_expense_keyboard(event: events.NewMessage.Event, new_amount: float, input_message_id):
    await event.client.edit_message(
            entity=event.chat_id,
            message=input_message_id,
            text = f"✅ Последняя трата обновлена: {new_amount:.2f} руб.",
            buttons=await default_nav_buttons_keyboard()
        )


async def after_repeat_last_expense_keyboard(event: events.CallbackQuery.Event, last_expense_amount: float, category_name: str):
    text = f"🔁 Успешно повторили трату: {last_expense_amount} руб., категория: {category_name.upper()}"
    await event.edit(text, buttons=await default_nav_buttons_keyboard())


# TODO: пересмотреть везде эти три кнопки, возможно добавлять их из default_nav_buttons
# и обрабатывать кнопку Назад
async def after_delete_last_expense_keyboard(event: events.CallbackQuery.Event, last_expense_amount, category_name):
    """Тут после удаления последнй траты."""
    text = f"Запись на сумму {last_expense_amount} из категории {category_name.upper()} успешно удалена!"
    buttons = [
            Button.inline("🏠 На главную", b"home"),
            Button.inline("↩️ Назад", b"back"),
            Button.inline("❌ Отмена", b"cancel"),
        ]
    await event.edit(text, buttons=buttons)
