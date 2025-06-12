from abc import ABC, abstractmethod
from domain.entities.message import MessageInDB, MessageCreate


class AbstractMessageRepository(ABC):
    @abstractmethod
    def get_messages_by_user(self, user_id: int) -> list[MessageInDB]: ...

    @abstractmethod
    def save(self, message: MessageCreate) -> None: ...
