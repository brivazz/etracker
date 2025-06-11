from abc import ABC, abstractmethod
from domain.entities.user import UserCreate, UserInDB

class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> UserInDB | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserInDB | None: ...
    
    @abstractmethod
    async def add(self, user: UserCreate) -> UserInDB: ...

    @abstractmethod
    async def update(self, user: UserInDB) -> UserInDB: ...
