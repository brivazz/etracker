from datetime import datetime

from sqlalchemy import select, delete, update as sqlalchemy_update, func, Result, Sequence, Row, text, literal, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from domain.entities.expense import ExpenseCreate, ExpenseInDB, ExpenseHistory
from domain.entities.stats import StatsInDb
from domain.repositories.expense_repo import AbstractExpenseRepository
from infrastructure.db.sqlalchemy.models import ExpenseORM, CategoryORM
from application.mappers.expense_mapper import ExpenseCreateMapper, ExpenseInDBMapper

class SQLAlchemyExpenseRepository(AbstractExpenseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_create_mapper = ExpenseCreateMapper()
        self.expense_indb_mapper = ExpenseInDBMapper()

    async def add(self, expense: ExpenseCreate) -> ExpenseInDB:
        expense_orm = await self.expense_create_mapper.entity_to_orm(expense)
        self.session.add(expense_orm)
        await self.session.flush()
        await self.session.refresh(expense_orm)
        expense_entity = await self.expense_indb_mapper.orm_to_entity(expense_orm)
        return expense_entity

    async def get_user_expenses(self, user_id: int) -> list[ExpenseInDB]:
        result = await self.session.execute(select(ExpenseORM).where(ExpenseORM.user_id == user_id))
        expenses = result.scalars().all()
        return [await self.expense_indb_mapper.orm_to_entity(e) for e in expenses]

    async def get_by_id(self, expense_id: int) -> ExpenseInDB | None:
        result = await self.session.get(ExpenseORM, expense_id)
        if not result:
            return None
        return await self.expense_indb_mapper.orm_to_entity(result)

    async def get_last(self) -> ExpenseInDB | None:
        stmt = (
            select(
                ExpenseORM,
                CategoryORM.name.label("category_name")
            )
            .join(CategoryORM, ExpenseORM.category)
            .order_by(desc(ExpenseORM.id))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if not row:
            return None
        expense_orm, category_name = row
        last_expense = await self.expense_indb_mapper.orm_to_entity(expense_orm)
        last_expense.category_name = category_name
        return last_expense


    async def delete(self, expense_id: int) -> bool:
        result = await self.session.execute(
            delete(ExpenseORM).where(ExpenseORM.id == expense_id)
        )
        return result.rowcount > 0

    async def update(self, expense: ExpenseInDB) -> ExpenseInDB:
        result = await self.session.execute(
            sqlalchemy_update(ExpenseORM)
            .where(ExpenseORM.id == expense.id)
            .values(
                amount=expense.amount,
                category_id=expense.category_id,
                note=expense.note
            )
            .returning(ExpenseORM)
        )

        row = result.fetchone()
        if not row:
            raise ValueError(f"Expense with id={expense.id} not found")

        # Достаём объект ORM из Row
        orm_instance: ExpenseORM = row[0]#row._mapping[ExpenseORM]

        return await self.expense_indb_mapper.orm_to_entity(orm_instance)

    async def get_stats(self, user_id: int, from_date: datetime) -> list[StatsInDb]:
            stmt = (
                select(
                    CategoryORM.name,
                    func.sum(ExpenseORM.amount)
                )
                .join(CategoryORM, ExpenseORM.category_id == CategoryORM.id)
                .where(
                    ExpenseORM.user_id == user_id,
                    ExpenseORM.created_at >= from_date
                )
                .group_by(CategoryORM.name)
            )

            result: Result[tuple[str, float]] = await self.session.execute(stmt)
            rows = result.all()

            return [
                StatsInDb(category_name=row[0], total_amount=float(row[1] or 0))
                for row in rows
            ]

    async def get_expense_history(self, user_id: int, period: str) -> list[ExpenseHistory]:
        # def parse_date(date_str: str, period: str) -> datetime:
        #     if period == "week":
        #         # Преобразуем '2025-22' в понедельник 22-й недели 2025 года
        #         year, week = map(int, date_str.split("-"))
        #         return datetime.fromisocalendar(year, week, 1)
        #     return datetime.strptime(date_str, strftime_patterns[period])
        if self.session.bind.dialect.name == 'sqlite':
            if period == "week":
                trunc_date = func.date(ExpenseORM.created_at, 'weekday 1', '-6 days')
            else:
                strftime_patterns = {
                    "day": "%Y-%m-%d",
                    "month": "%Y-%m-01",
                    "year": "%Y-01-01"
                }
                trunc_date = func.strftime(strftime_patterns[period], ExpenseORM.created_at)
        else:
            # Для PostgreSQL и других диалектов
            trunc_date = func.date_trunc(period, ExpenseORM.created_at)

        result = await self.session.execute(
            select(
                trunc_date.label("date"),
                CategoryORM.name.label("category_name"),
                func.count().label("count"),
                func.sum(ExpenseORM.amount).label("total_amount")
            )
            .join(CategoryORM, CategoryORM.id == ExpenseORM.category_id)
            .where(ExpenseORM.user_id == user_id)
            .group_by("date", "category_name")
            .order_by(text("date DESC"))
        )

        rows = result.fetchall()
        return [
            ExpenseHistory(
                user_id=user_id,
                # date=parse_date(row.date, period),
                date=row.date,
                category_name=row.category_name,
                count=row.count,
                total_amount=row.total_amount,
                period=period,
                # display_date=strftime_patterns[period]
            )
            for row in rows
        ]
