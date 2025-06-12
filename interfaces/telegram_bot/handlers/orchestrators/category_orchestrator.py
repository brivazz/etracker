from domain.uow.abstract import AbstractUnitOfWork
from interfaces.telegram_bot.utils.state_manager import (
    FSMManager,
    State,
    get_message_id,
)
from telethon import events
from typing import cast
from application.dto.user_dto import UserInDBDTO
from application.dto.category_dto import CategoryCreateDTO, CategoryInDBDTO
from application.commands.command_enum import Command
from interfaces.telegram_bot.keyboards.build_category_keyboard import (
    after_add_new_category_keyboard,
    add_category_keyboard,
)
from interfaces.telegram_bot.handlers.orchestrators.base_orchestrator import (
    OrchestratorBase,
)
from config import logger
from interfaces.telegram_bot.utils.state_manager import ExpenseMeta


class CategoryOrchestrator(OrchestratorBase):
    def __init__(self, uow: AbstractUnitOfWork, fsm: FSMManager):
        super().__init__(uow)
        self.uow = uow
        self.fsm = fsm

    async def _get_category_fsm(self, telegram_id: int) -> tuple[str, str]:
        category_id = await self.fsm.get_meta(telegram_id, "category_id")
        category_name = await self.fsm.get_meta(telegram_id, "category_name")
        return category_id, category_name

    async def show_keyboard_add_category(
        self, event: events.CallbackQuery.Event, user: UserInDBDTO
    ):
        """Тут показывам клавиатуру при добавлении новой категории."""
        message_id = await get_message_id(self.fsm, user.telegram_id)
        await add_category_keyboard(event, message_id)
        await self.fsm.set_state(
            user.telegram_id,
            State.WAITING_FOR_CATEGORY,
            meta=ExpenseMeta(
                message_id=message_id,
            ),
        )

    async def handle_add_category(
        self, event: events.NewMessage.Event, user: UserInDBDTO
    ):
        """Тут после ввода названия новой категории при создании новой категории."""
        category_name: str = event.raw_text.strip()

        dto = CategoryCreateDTO(user_id=user.id, name=category_name)
        category = cast(CategoryInDBDTO, await self._handle(Command.ADD_CATEGORY, dto))

        # Удаляем сообщение пользователя с категорией
        await event.message.delete()
        message_id = await get_message_id(self.fsm, user.telegram_id)
        await after_add_new_category_keyboard(event, category_name, message_id)
        await self.fsm.set_state(
            user.telegram_id,
            State.SELECTED_A_CATEGORY,
            meta=ExpenseMeta(
                category_id=category.id,
                category_name=category.name,
                message_id=message_id,
            ),
        )

    async def handle_non_category(
        self, event: events.NewMessage.Event, user: UserInDBDTO
    ):
        """Тут если при показе кнопок категорий на них не нажать, а написать сообщение."""
        await event.message.delete()

        current_state = await self.fsm.get_state(user.telegram_id)
        logger.info(f"в состоянии: == {current_state}")
