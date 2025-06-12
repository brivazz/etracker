from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.expense import ExpenseCreate, ExpenseInDB, ExpenseHistory
from domain.entities.stats import StatsInDb


class AbstractExpenseRepository(ABC):
    @abstractmethod
    async def add(self, expense: ExpenseCreate) -> ExpenseInDB: ...

    @abstractmethod
    async def get_user_expenses(self, user_id: int) -> list[ExpenseInDB]: ...

    @abstractmethod
    async def delete(self, expense_id: int) -> bool: ...

    @abstractmethod
    async def get_by_id(self, expense_id: int) -> ExpenseInDB | None: ...

    @abstractmethod
    async def get_last(self) -> ExpenseInDB | None: ...

    @abstractmethod
    async def update(self, expense: ExpenseInDB) -> ExpenseInDB: ...

    @abstractmethod
    async def get_stats(self, user_id: int, from_date: datetime) -> list[StatsInDb]: ...

    @abstractmethod
    async def get_expense_history(
        self, user_id: int, period: str
    ) -> list[ExpenseHistory]: ...
