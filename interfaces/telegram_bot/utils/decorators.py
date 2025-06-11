import inspect
from functools import wraps
from telethon.events import NewMessage, CallbackQuery

from application.main_orchestrator import MainOrchestrator
from application.dto.user_dto import UserCreateDTO
from application.commands.command_enum import Command
from application.factories.uow_factories import get_uow
from interfaces.telegram_bot.utils.state_manager import fsm, State

def inject_user():
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(event: NewMessage.Event | CallbackQuery.Event, *args, **kwargs):
            bound = sig.bind_partial(event, *args, **kwargs)
            bound.apply_defaults()

            telegram_id = event.sender_id
            sender = await event.get_sender()
            username = sender.username or sender.first_name

            user = await fsm.get_user(telegram_id)
            if not user:
                async with get_uow() as uow:
                    orchestrator = MainOrchestrator(uow)
                    dto = UserCreateDTO(username=username, telegram_id=telegram_id, balance=0)
                    user = await orchestrator.handle_command(Command.REGISTER_OR_GET_USER, dto)
                    await fsm.set_user(telegram_id, user)
                    await fsm.set_state(telegram_id, State.IDLE)

            # Инъекция user в аргументы
            for name, param in sig.parameters.items():
                if param.annotation.__name__ == "UserInDBDTO":
                    bound.arguments[name] = user

            return await func(*bound.args, **bound.kwargs)

        return wrapper
    return decorator
