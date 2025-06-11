from datetime import datetime, timedelta

from domain.repositories.expense_repo import AbstractExpenseRepository
from domain.entities.expense import ExpenseCreate, ExpenseInDB, ExpenseHistory, ExpenseHistoryPeriod
from domain.entities.stats import StatsInDb, StatsPeriodSummary


class ExpenseService:
    def __init__(self, repo: AbstractExpenseRepository):
        self.repo = repo

    async def add_expense(self, expense: ExpenseCreate) -> ExpenseInDB:
        """Создание новой записи о расходе."""
        return await self.repo.add(expense)

    async def get_expenses_by_user(self, user_id: int) -> list[ExpenseInDB]:
        """Получение всех расходов пользователя по ID."""
        return await self.repo.get_user_expenses(user_id)

    async def delete_expense(self, expense_id: int) -> bool:
        """Удаление расхода по ID. Возвращает True, если удаление прошло успешно."""
        return await self.repo.delete(expense_id)

    async def get_by_id(self, expense_id: int) -> ExpenseInDB | None:
        """Получение конкретного расхода по ID."""
        return await self.repo.get_by_id(expense_id)

    async def get_last(self) -> ExpenseInDB | None:
        """Получение последней записи."""
        return await self.repo.get_last()

    async def update_expense(self, updated_expense: ExpenseInDB) -> ExpenseInDB:
        """Обновление данных расхода."""
        return await self.repo.update(updated_expense)

    async def get_stats(self, user_id: int, period: str) -> StatsPeriodSummary:
        now = datetime.now()
        if period == "day":
            from_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            from_date = now - timedelta(days=now.weekday())
        elif period == "month":
            from_date = now.replace(day=1)
        else:
            raise ValueError("Unknown period")

        to_date = now
        stats: list[StatsInDb] = await self.repo.get_stats(user_id, from_date)
        return StatsPeriodSummary(stats=stats, from_date=from_date, to_date=to_date)

    async def get_expense_history(self, expense: ExpenseHistoryPeriod) -> list[ExpenseHistory]:
        return await self.repo.get_expense_history(user_id=expense.user_id, period=expense.period)
