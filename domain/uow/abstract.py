from abc import ABC, abstractmethod
from domain.repositories.user_repo import AbstractUserRepository
from domain.repositories.message_repo import AbstractMessageRepository
from domain.repositories.expense_repo import AbstractExpenseRepository
from domain.repositories.category_repo import AbstractCategoryRepository

class AbstractUnitOfWork(ABC):
    user_repo: AbstractUserRepository
    message_repo: AbstractMessageRepository
    expense_repo: AbstractExpenseRepository
    category_repo: AbstractCategoryRepository

    @abstractmethod
    async def __aenter__(self): ...
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
    
    @abstractmethod
    async def commit(self): ...
    
    @abstractmethod
    async def rollback(self): ...
