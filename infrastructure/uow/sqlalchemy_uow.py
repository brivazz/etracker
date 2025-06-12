from sqlalchemy.ext.asyncio import AsyncSession
from domain.uow.abstract import AbstractUnitOfWork
from infrastructure.db.sqlalchemy.repositories.user_repo_impl import (
    SQLAlchemyUserRepository,
)
from infrastructure.db.sqlalchemy.repositories.message_repo_impl import (
    SQLAlchemyMessageRepository,
)
from infrastructure.db.sqlalchemy.repositories.expense_repo_impl import (
    SQLAlchemyExpenseRepository,
)
from infrastructure.db.sqlalchemy.repositories.category_repo_impl import (
    SQLAlchemyCategoryRepository,
)
from config import logger


class RepositoryFactory:
    def __init__(self, session):
        self.session = session

    async def create_user_repo(self):
        return SQLAlchemyUserRepository(self.session)

    async def create_message_repo(self):
        return SQLAlchemyMessageRepository(self.session)

    async def create_expense_repo(self):
        return SQLAlchemyExpenseRepository(self.session)

    async def create_category_repo(self):
        return SQLAlchemyCategoryRepository(self.session)


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = None
        self.message_repo = None
        self.expense_repo = None
        self.category_repo = None

    async def __aenter__(self):
        factory = RepositoryFactory(self.session)
        self.user_repo = await factory.create_user_repo()
        self.message_repo = await factory.create_message_repo()
        self.expense_repo = await factory.create_expense_repo()
        self.category_repo = await factory.create_category_repo()

        logger.debug("UoW started")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.warning(f"Rolling back due to error. exc_type: {exc_type}")
            await self.rollback()
        else:
            logger.debug("Committing UoW")
            await self.commit()

        await self.session.close()
        logger.debug("Session closed")

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
