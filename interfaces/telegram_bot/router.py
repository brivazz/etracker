import re
import importlib
import pkgutil
from enum import Enum
from pathlib import Path
from typing import Callable, Awaitable, Pattern, Union, Optional, Literal, Any

from telethon import TelegramClient, events

EventType = Literal["message", "callback"]
Middleware = Callable[[Callable], Callable]


class Router:
    def __init__(self):
        self.routes = {
            "message": [],
            "callback": []
        }
        # хочешь добавить inline_query 
        # — просто добавь "inline_query": [] 
        # и используй _register(...)
        self.middlewares: list[Middleware] = []

    def use(self, middleware: Middleware):
        """Например router.use(inject_user())  применится ко всем хендлерам"""
        self.middlewares.append(middleware)

    def message(self, pattern: Optional[str] = None):
        compiled = re.compile(pattern) if pattern else None
        return self._register("message", compiled) 


    def callback(self, data: Union[
        str, bytes, Pattern[str], Pattern[bytes], Enum, type[Enum]
    ]):
        pattern = self._convert_to_pattern(data)
        return self._register("callback", pattern)

    def _convert_to_pattern(self, data: Any) -> Optional[Pattern]:
        # Если data — конкретный enum (EnumValue)
        if isinstance(data, Enum):
            value = data.value
            return re.compile(value) if isinstance(value, str) else value
        # Если data — класс Enum
        if isinstance(data, type) and issubclass(data, Enum):
            # Собираем все значения в один regex паттерн, например: ^(add_expense|edit_last_expense|cat_\d+:.+)$
            parts = []
            for member in data:
                val = member.value
                # Если значение — байты, то превратим их в строку для regex
                if isinstance(val, bytes):
                    val = val.decode("utf-8")
                parts.append(val)
            # Формируем объединённый паттерн, экранируя если надо (зависит от значений)
            combined = "|".join(parts)
            regex_str = f"^({combined})$"
            return re.compile(regex_str)
        # Если data — str или bytes
        if isinstance(data, (str, bytes)):
            return re.compile(data)
        # Если уже Pattern
        if isinstance(data, re.Pattern):
            return data
        # Иначе None
        return None


    def _register(self, event_type: EventType, pattern: Optional[Pattern]):
        def decorator(handler: Callable[..., Awaitable[None]]):
            for mw in reversed(self.middlewares):
                handler = mw(handler)
            self.routes[event_type].append((pattern, handler))
            return handler
        return decorator

    async def register(self, client: TelegramClient):
        for pattern, handler in self.routes["message"]:
            client.add_event_handler(handler, events.NewMessage(pattern=pattern))
        for pattern, handler in self.routes["callback"]:
            client.add_event_handler(handler, events.CallbackQuery(data=pattern))

    def autoimport(self, package: Path):
        from interfaces.telegram_bot import handlers
        for _, module_name, _ in pkgutil.iter_modules(handlers.__path__):
            importlib.import_module(f"{handlers.__name__}.{module_name}")


router = Router()


# @router.callback(Data)  # Передаём весь Enum — он будет автоматически объединён
# async def any_callback_handler(event, user, data):
#     # ...
#     pass

# @router.callback(Data.ADD_EXPENSE)  # Можно передать конкретное значение
# async def add_expense_handler(event, user):
#     # ...
#     pass

# @router.callback(r"^custom_callback_\d+$")  # Можно передать строку с regex
# async def custom_handler(event, user):
#     # ...
#     pass
