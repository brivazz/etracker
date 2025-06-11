from functools import wraps
from telethon.events import NewMessage, CallbackQuery
from typing import Callable, Coroutine, Any
from config import logger


def inject_user(use_fsm: bool = True):
    def decorator(handler: Callable[..., Coroutine[Any, Any, None]]):
        @wraps(handler)
        async def wrapper(event: NewMessage.Event | CallbackQuery.Event, *args, **kwargs):
            from interfaces.telegram_bot.utils.state_manager import fsm, State, ExpenseMeta
            from application.main_orchestrator import MainOrchestrator
            from application.dto.user_dto import UserCreateDTO, UserInDBDTO
            from application.factories.uow_factories import get_uow
            from application.commands.command_enum import Command
            sender = await event.get_sender()
            telegram_id = event.sender_id
            username = sender.username or sender.first_name

            # Пытаемся получить user из FSM
            if user_data := await fsm.get_context(telegram_id, "user"):
                user = UserInDBDTO(**user_data)

            else:
                # Если нет — получаем или создаём в БД
                async with get_uow() as uow:
                    orchestrator = MainOrchestrator(uow=uow)
                    user_dto = UserCreateDTO(
                        username=username,
                        balance=0,
                        telegram_id=telegram_id
                    )
                    user: UserInDBDTO = await orchestrator.handle_command(Command.REGISTER_OR_GET_USER, dto=user_dto)

                if use_fsm:
                    # Сохраняем в FSM
                    message = await event.get_message() if hasattr(event, "get_message") else event.message
                    # logger.info(f"🔍 Event type: {type(event)}")#, attrs: {dir(event)}")

                    print("В inject_user")
                    await fsm.set_state(
                        telegram_id,
                        State.IDLE,
                        context_update={"user": user},
                        meta=ExpenseMeta(message_id=message.id)
                    )
            return await handler(event, user, *args, **kwargs)
        return wrapper
    return decorator
