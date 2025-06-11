from telethon.errors import MessageNotModifiedError, MessageIdInvalidError
from telethon.tl.custom import Message
from domain.uow.abstract import AbstractUnitOfWork
from interfaces.telegram_bot.utils.state_manager import FSMManager, State
from interfaces.telegram_bot.keyboards.build_expense_keyboard import (
    before_input_amount_keyboard, before_save_amount_keyboard, edit_last_expense_keyboard,
    after_repeat_last_expense_keyboard, after_delete_last_expense_keyboard,
    after_input_amount_for_edit_expense_keyboard, expense_keyboard,
    after_save_expense_keyboard
)
from telethon import events
from typing import cast
from application.dto.user_dto import UserInDBDTO
from application.dto.expense_dto import ExpenseCreateDTO, ExpenseDeleteDTO, ExpenseEditDTO, ExpenseInDBDTO
from application.commands.command_enum import Command
from interfaces.telegram_bot.keyboards.common_keyboard import show_error_keyboard
from interfaces.telegram_bot.handlers.orchestrators.base_orchestrator import OrchestratorBase
from config import logger
from interfaces.telegram_bot.utils.state_manager import ExpenseMeta


class AddOrchestrator(OrchestratorBase):
    def __init__(self, uow: AbstractUnitOfWork, fsm: FSMManager):
        super().__init__(uow)
        self.uow = uow
        self.fsm = fsm


    async def _parse_amount(self, event: events.NewMessage.Event, input_message_id: int) -> float | None:
        try:
            return float(event.text.strip())
        except ValueError:
            await event.message.delete()
            await show_error_keyboard(event, text="❌ Введите корректную сумму (например, 123.45).", input_message_id=input_message_id)
            return None

    async def _get_category_fsm(self, telegram_id: int) -> tuple[int, str]:
        category_id = await self.fsm.get_meta(telegram_id, "category_id")
        category_name = await self.fsm.get_meta(telegram_id, "category_name")
        return category_id, category_name

    async def add_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажатия Добавить трату."""
        new_buttons, new_text = await expense_keyboard(user.id)
        # сообщение нашей клавиатуры записанное на предыдущем шаге
        message_id = await self.fsm.get_meta(user.telegram_id, 'message_id')
        # TODO: Тут нужно предусмотреть, если пользователь введут свое сообщение,
        # то нужно проверить тип сообщения, удалить его сообщение
        # и изменять как сейчас же редактируем наше сообщение!
        try:
            await event.client.edit_message(
                entity=event.chat_id,
                message=message_id,
                text=new_text,
                buttons=new_buttons
            )
        except (MessageIdInvalidError, MessageNotModifiedError):
            pass
        logger.warning("❗️❗️❗️ В кнопке Добавить трату")
        await self.fsm.set_state(
            user.telegram_id,
            State.ADD_EXPENSE,
            meta=ExpenseMeta(
                message_id=message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def handle_category_selection(self, event: events.CallbackQuery.Event, user: UserInDBDTO, category_id: int, category_name: str):
        """Тут после нажатия на категорию/при выборе категории."""
        # Когда выбрали категорию.
        new_text, new_buttons = await before_input_amount_keyboard(category_name)
        # Тоже сообщение нашей клавиатуры
        message = await event.edit(new_text, buttons=new_buttons)
        await event.answer()

        logger.warning("❗️❗️❗️В кнопке какой-то выбранной категории")
        await self.fsm.set_state(
            user.telegram_id,
            State.SELECTED_A_CATEGORY,
            meta=ExpenseMeta(
                category_id=category_id,
                category_name=category_name,
                message_id=message.id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def handle_amount_expense(self, event: events.NewMessage.Event, user: UserInDBDTO):
        """Тут после ввода цифр суммы для траты"""
        category_id, category_name = await self._get_category_fsm(user.telegram_id)
        message_id = await self.fsm.get_meta(user.telegram_id, "message_id")
        # Тоже сообщение нашей клавиатуры
        amount = await self._parse_amount(event, message_id)
        if amount is None:
            logger.info(
                f"User {user.telegram_id} added expense: {amount} in category {category_name} (id={category_id})")
            return
        # Сюда попали если были в состоянии SELECTED_A_CATEGORY и CHANGE_ENTRY
        # и удаляем сумму, написанную пользователем
        await event.message.delete()
        """Перед сохранением/записью новой траты."""
        await before_save_amount_keyboard(event, amount, category_name, message_id)

        logger.warning("❗️❗️❗️В кнопке после ввода цифр суммы для траты")
        await self.fsm.set_state(
            user.telegram_id,
            State.BEFORE_SAVE_EXPENSE,
            meta=ExpenseMeta(
                # expense_id=expense.id,
                amount=amount,
                category_id=category_id,
                category_name=category_name,
                message_id=message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def save_new_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        message_id = await self.fsm.get_meta(user.telegram_id, "message_id")
        category_id, category_name = await self._get_category_fsm(user.telegram_id)
        amount = await self.fsm.get_meta(user.telegram_id, "amount")

        dto = ExpenseCreateDTO(user_id=user.id, amount=amount, category_id=category_id, note="")
        expense = cast(ExpenseInDBDTO, await self._handle(Command.ADD_EXPENSE, dto))

        await after_save_expense_keyboard(event, amount, category_name, message_id)

        logger.warning("❗️❗️❗️В кнопке сохранить трату")
        await self.fsm.set_state(
            user.telegram_id,
            State.EXPENSE_RECORDED,
            meta=ExpenseMeta(
                expense_id=expense.id,
                amount=amount,
                category_id=category_id,
                category_name=category_name,
                message_id=message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def change_entry(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Изменить введенные пользователем Сумму и Категорию на выбор."""
        # Обработка кнопки CHANGE_ENTRY
        meta = ExpenseMeta(**await self.fsm.get_meta(user.telegram_id))
        new_buttons, new_text = await expense_keyboard(user.id)
        await event.client.edit_message(
            entity=event.chat_id,
            message=meta.message_id,
            text=new_text,
            buttons=new_buttons
        )
        await self.fsm.set_state(
            user.telegram_id,
            State.CHANGE_ENTRY,
            meta=ExpenseMeta(
                message_id=meta.message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def edit_last_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажатия на редактирование последней траты."""
        dto = ExpenseCreateDTO(user_id=user.id, amount=0.0, category_id=0, note="")
        last_expense = cast(ExpenseInDBDTO, await self._handle(Command.GET_LAST_EXPENSE, dto))
        if not last_expense:
            await show_error_keyboard(event, text="❗ Нет последней траты для редактирования.")
            return
        message = await edit_last_expense_keyboard(event)
        await self.fsm.set_state(
            user.telegram_id,
            State.EDIT_LAST_EXPENSE,
            meta=ExpenseMeta(
                expense_id=last_expense.id,
                amount=last_expense.amount,
                category_id=last_expense.category_id,
                category_name=last_expense.category_name,
                message_id=message.id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def handle_edit_expense(self, event: events.NewMessage.Event, user: UserInDBDTO):
        """Тут после ввода новой суммы траты при редактировании траты."""
        meta = ExpenseMeta(**await self.fsm.get_meta(user.telegram_id))
        new_amount = await self._parse_amount(event, meta.message_id)
        if new_amount is None:
            return
        dto = ExpenseEditDTO(id=meta.expense_id, amount=new_amount, category_id=meta.category_id, note="")
        expense = cast(ExpenseInDBDTO, await self._handle(Command.EDIT_EXPENSE, dto))

        await event.message.delete()
        await after_input_amount_for_edit_expense_keyboard(event, new_amount, meta.message_id, meta.category_name)
        await self.fsm.set_state(
            user.telegram_id,
            State.EXPENSE_RECORDED,
            meta=ExpenseMeta(
                expense_id=expense.id,
                amount=meta.amount,
                category_id=expense.category_id,
                category_name=expense.category_name,
                message_id=meta.message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def handle_repeat_last_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажатия Повторить последнюю."""
        # Получаем последнюю
        meta = ExpenseMeta(**await self.fsm.get_meta(user.telegram_id))
        dto = ExpenseCreateDTO(user_id=user.id, amount=0.0, category_id=0, note="")
        last_expense = cast(ExpenseInDBDTO, await self._handle(Command.GET_LAST_EXPENSE, dto))
        if not last_expense:
            await show_error_keyboard(event, text="❗ Нет последней траты для повторения.")
            return
        # Выполняем повтор траты
        dto = ExpenseCreateDTO(user_id=user.id, amount=last_expense.amount, category_id=last_expense.category_id, note="(повтор)")
        expense = cast(ExpenseInDBDTO, await self._handle(Command.ADD_EXPENSE, dto))

        await after_repeat_last_expense_keyboard(event, expense.amount, last_expense.category_name)
        await self.fsm.set_state(
            user.telegram_id,
            State.REPEAT_EXPENSE,
            meta=ExpenseMeta(
                expense_id=expense.id,
                amount=expense.amount,
                category_id=expense.category_id,
                category_name=expense.category_name,
                message_id=meta.message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")


    async def handle_delete_last_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажатия Удалить последнюю."""
        meta = ExpenseMeta(**await self.fsm.get_meta(user.telegram_id))
        dto = ExpenseCreateDTO(user_id=user.id, amount=0.0, category_id=0, note="")
        last_expense = cast(ExpenseInDBDTO, await self._handle(Command.GET_LAST_EXPENSE, dto))
        if not last_expense:
            await show_error_keyboard(event, text="❗ Нет последней траты для удаления.")
            return
        last_expense_category_name = last_expense.category_name
        last_expense_amount = last_expense.amount
        dto = ExpenseDeleteDTO(id=last_expense.id)
        await self._handle(Command.DELETE_EXPENSE, dto)

        await after_delete_last_expense_keyboard(event, last_expense_amount, last_expense_category_name)
        # Удаляем ключи состояния после удаления последней траты
        await self.fsm.set_state(
            user.telegram_id,
            State.DELETE_EXPENSE,
            meta=ExpenseMeta(
                message_id=meta.message_id,
            )
        )
        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")
