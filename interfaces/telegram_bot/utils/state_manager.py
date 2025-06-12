import re
import json
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass, asdict, is_dataclass, field
from enum import Enum

from config import logger


# Паттерны для коллбеков
class Data(Enum):
    # Траты
    ADD_EXPENSE = "add_expense"
    CATEGORY_SELECTION = b"^cat_(\\d+):(.+)$"
    CHANGE_ENTRY = "change_expense"
    EDIT_EXPENSE = "edit_expense"
    SAVE_EXPENSE = "save_expense"
    REPEAT_EXPENSE = "repeat_expense"
    DELETE_EXPENSE = "delete_expense"
    HISTORY = "history"
    HISTORY_SELECTION = rb"^history:(day|week|month|year)$"
    # Категории
    ADD_CATEGORY = "add_category"
    # Статистика
    STATS_EXPENSE = "stats_expense"
    STATS_SELECTION = b"stats:(day|week|month)"
    # Общие
    START = "/start"
    HOME = "home"
    CANCEL = "cancel"
    BACK = "back"


def parse_callback_data(raw_data: bytes) -> tuple[Data | None, tuple]:
    s = raw_data.decode("utf-8")
    for data_enum in Data:
        val = data_enum.value
        if isinstance(val, str):
            if s == val:
                return data_enum, ()
        elif isinstance(val, bytes):
            pattern = val.decode("utf-8")
            m = re.match(pattern, s)
            if m:
                return data_enum, m.groups()
    return None, ()


class State(Enum):
    IDLE = "IDLE"  # Пользователь не взаимодействует
    START = "START"  # Только начал, стартовое состояние

    # Добавление траты
    ADD_EXPENSE = "ADD_EXPENSE"  # Начало процесса добавления
    SELECTED_A_CATEGORY = "SELECTED_A_CATEGORY"
    BEFORE_SAVE_EXPENSE = "BEFORE_SAVE_EXPENSE"
    CHANGE_ENTRY = "CHANGE_ENTRY"
    EXPENSE_RECORDED = "EXPENSE_RECORDED"  # Успешно добавлено
    REPEAT_EXPENSE = "REPEAT_EXPENSE"
    DELETE_EXPENSE = "DELETE_EXPENSE"

    WAITING_FOR_CATEGORY = "WAITING_FOR_CATEGORY"  # Ждём выбор категории
    WAITING_FOR_AMOUNT = "WAITING_FOR_AMOUNT"  # Ждём ввод суммы

    # Редактирование последней траты
    EDIT_LAST_EXPENSE = "EDIT_LAST_EXPENSE"  # Начали редактировать
    WAITING_FOR_CATEGORY_EDIT = "WAITING_FOR_CATEGORY_EDIT"
    WAITING_FOR_AMOUNT_EDIT = "WAITING_FOR_AMOUNT_EDIT"

    # Статистика
    SHOW_STATS_KEYBOARD = "SHOW_STATS_KEYBOARD"


class AsyncDictStorage:
    def __init__(self):
        self._storage: dict[int, dict[str, str]] = {}

    async def get(self, telegram_id: int, key: str) -> Optional[str]:
        return self._storage.get(telegram_id, {}).get(key)

    async def set(self, telegram_id: int, key: str, value: str | int):
        if telegram_id not in self._storage:
            self._storage[telegram_id] = {}
        self._storage[telegram_id][key] = value

    async def dump(self, telegram_id: int) -> dict:
        return self._storage.get(telegram_id, {})


@dataclass
class ExpenseMeta:
    expense_id: int | None = None
    amount: float | None = None
    category_id: int | None = None
    category_name: str | None = None
    message_id: int | None = None


@dataclass
class FSMHistoryItem:
    state: State
    meta: Optional[ExpenseMeta] = None
    context: dict[str, Any] = field(default_factory=dict)  # user и др. данные сессии


def custom_json_decoder(obj):
    # Попробуем автоматически распарсить ISO-строки как datetime
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return obj


def custom_json_encoder(obj):
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()  # сериализация в ISO-8601
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def serialize_history(history: list[FSMHistoryItem]) -> str:
    return json.dumps([asdict(item) for item in history], default=custom_json_encoder)


def deserialize_history(data: str) -> list[FSMHistoryItem]:
    raw_list = json.loads(data)
    return [
        FSMHistoryItem(
            state=State(item["state"]),
            meta=item.get("meta", {}),
            context=item.get("context", {}),
        )
        for item in raw_list
    ]


class FSMManager:
    def __init__(self, storage, history_limit: int = 10):
        self.storage = storage  # Тут dict или Redis-like
        self.history_limit = history_limit

    async def get_state(self, telegram_id: int) -> Optional[State]:
        raw = await self.storage.get(telegram_id, "state")
        return State(raw) if raw else None

    async def get_history(self, telegram_id: int) -> list[FSMHistoryItem]:
        raw = await self.storage.get(telegram_id, "state_stack")
        return deserialize_history(raw) if raw else []

    async def set_state(
        self,
        telegram_id: int,
        state: State,
        *,
        meta: Optional[ExpenseMeta] = None,
        context_update: Optional[dict] = None,
    ):
        current_state = await self.get_state(telegram_id)
        if current_state:
            history = await self.get_history(telegram_id)
            current_context_raw = await self.storage.get(telegram_id, "context")
            current_meta_raw = await self.storage.get(telegram_id, "meta")

            try:
                current_context = (
                    json.loads(current_context_raw) if current_context_raw else {}
                )
                current_meta = json.loads(current_meta_raw) if current_meta_raw else {}
            except Exception:
                current_context = {}
                current_meta = {}

            history.append(
                FSMHistoryItem(
                    state=current_state,
                    context=current_context,
                    meta=current_meta,
                )
            )
            history = history[-self.history_limit :]
            await self.storage.set(
                telegram_id, "state_stack", serialize_history(history)
            )

        await self.storage.set(telegram_id, "state", state.value)

        # Обновляем context, объединяя с уже существующим
        current_context_raw = await self.storage.get(telegram_id, "context")
        try:
            current_context = (
                json.loads(current_context_raw) if current_context_raw else {}
            )
        except Exception:
            current_context = {}

        if context_update:
            current_context.update(context_update)
            await self.storage.set(
                telegram_id,
                "context",
                json.dumps(current_context, default=custom_json_encoder),
            )

        # Сохраняем короткоживущие мета-данные отдельно
        if meta:
            await self.storage.set(
                telegram_id, "meta", json.dumps(meta, default=custom_json_encoder)
            )

    async def go_back(self, telegram_id: int) -> FSMHistoryItem:
        history = await self.get_history(telegram_id)
        logger.error(history)
        if not history:
            idle_item = FSMHistoryItem(state=State.IDLE)
            await self.storage.set(telegram_id, "state", idle_item.state.value)
            return idle_item

        last = history.pop()
        await self.storage.set(telegram_id, "state_stack", serialize_history(history))
        await self.storage.set(telegram_id, "state", last.state.value)

        if last_message_id := last.meta.get("message_id") is not None:
            await self.storage.set(telegram_id, "message_id", last_message_id)

        await self.storage.set(
            telegram_id,
            "meta",
            json.dumps(last.meta, default=custom_json_encoder),
        )

        await self.storage.set(
            telegram_id,
            "context",
            json.dumps(last.context, default=custom_json_encoder),
        )

        return last

    async def get_context(self, telegram_id: int, key: str) -> Any:
        raw = await self.storage.get(telegram_id, "context")
        if not raw:
            return None
        try:
            data = json.loads(raw, object_hook=custom_json_decoder)
            return data.get(key)
        except Exception as e:
            logger.error(f"Ошибка при разборе context: {e}")
            return None

    async def get_meta(self, telegram_id: int, key: Optional[str] = None) -> Any:
        raw = await self.storage.get(telegram_id, "meta")
        if not raw:
            return None
        try:
            data = json.loads(raw, object_hook=custom_json_decoder)
            return data.get(key) if key else data
        except Exception as e:
            logger.error(f"Ошибка при разборе meta: {e}")
            return None


fsm = FSMManager(storage=AsyncDictStorage())


async def get_message_id(fsm: FSMManager, telegram_id: int) -> int:
    return await fsm.get_meta(telegram_id, "message_id")
