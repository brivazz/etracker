from telethon import events, errors
from application.dto.user_dto import UserInDBDTO
from config import logger
from domain.uow.abstract import AbstractUnitOfWork
from interfaces.telegram_bot.utils.state_manager import FSMManager, State, ExpenseMeta
from interfaces.telegram_bot.handlers.orchestrators.base_orchestrator import OrchestratorBase
from interfaces.telegram_bot.keyboards.common_keyboard import main_menu_keyboard, MAIN_MENU_TEXT, default_nav_buttons_keyboard
from interfaces.telegram_bot.keyboards.build_expense_keyboard import expense_keyboard
from typing import Callable, Any, Awaitable


class CommonOrchestrator(OrchestratorBase):
    def __init__(self, uow: AbstractUnitOfWork, fsm: FSMManager):
        super().__init__(uow)
        self.uow = uow
        self.fsm = fsm
        self._register_back_handlers()


    def _register_back_handlers(self):
        self.back_handlers: dict[State, Callable[[Any, UserInDBDTO], Awaitable[None]]] = {
            State.IDLE: self.back_to_main_menu,
            State.START: self.back_to_main_menu,
            State.ADD_EXPENSE: self.back_to_main_menu,
            State.SELECTED_A_CATEGORY: self.back_to_main_menu,
            State.EXPENSE_RECORDED: self.back_to_main_menu,
            State.CHANGE_ENTRY: self.back_to_category,
            State.BEFORE_SAVE_EXPENSE: self.back_to_category,

        }


    async def start_flow(self, event: events.NewMessage.Event, user: UserInDBDTO):
        """После нажатия кнопки /start."""
        if event.message: # Удаляем первое сообщение от пользователя
            await event.message.delete()
        logger.warning("❗️❗️❗️В кнопке старт")
        message = await event.respond(MAIN_MENU_TEXT.format(user.username), buttons=await main_menu_keyboard())
        await self.fsm.set_state(
            user.telegram_id,
            State.START,
            meta=ExpenseMeta(
                message_id=message.id, # Это сообщение наша клавиатура
            )
        )
        # logger.warning(f"В кнопке старт после установки нового состояния: ||, {await self.fsm.get_state(user.telegram_id)}, || history: {await self.fsm.get_history(user.telegram_id)}, || get_meta: {await self.fsm.get_meta(user.telegram_id, 'message_id')}")
        logger.warning(f"{'='*30}")


    async def handle_home(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """После нажатия кнопки Домой."""
        await self.fsm.set_state(user.telegram_id, State.IDLE)
        new_text = MAIN_MENU_TEXT.format(user.username)
        new_buttons = await main_menu_keyboard()
        await event.edit(new_text, buttons=new_buttons)
        await event.answer()  # закрыть "часики"


    async def handle_cancel(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """После нажатия кнопки Отменить."""
        await event.edit("Действие отменено.", buttons=await default_nav_buttons_keyboard())
        await event.answer()


    # Я тут но могу же вернуться в start_flow а не сюда ⬇️
    # TODO: если вернуться в start_flow, то нужно подумать, как не удалять сообщение
    async def back_to_main_menu(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        await self.fsm.set_state(user.telegram_id, State.START)
        await event.edit(MAIN_MENU_TEXT.format(user.username), buttons=await main_menu_keyboard())
        await event.answer()

    async def back_to_category(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        await self.fsm.set_state(user.telegram_id, State.ADD_EXPENSE)
        buttons, text = await expense_keyboard(user.id)
        message_id = await self.fsm.get_meta(user.telegram_id, "message_id")
        try:
            await event.client.edit_message(
                    entity=event.chat_id,
                    message=message_id,
                    text=text,
                    buttons=buttons
                )
            # await event.answer()
        except errors.MessageNotModifiedError:
            pass


    async def handle_back(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        item = await self.fsm.go_back(user.telegram_id)
        logger.warning(item)
        logger.info(f"Назад: вернулись к состоянию {item.state}")

        handler = self.back_handlers.get(item.state)
        if not handler:
            await event.answer("Не могу вернуться назад.")
            return

        await handler(event, user)
