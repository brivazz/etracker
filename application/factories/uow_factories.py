from contextlib import asynccontextmanager
from typing import AsyncGenerator
from infrastructure.db.sqlalchemy.sqlalchemy_async_session import database
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from domain.uow.abstract import AbstractUnitOfWork


@asynccontextmanager
async def get_uow() -> AsyncGenerator[AbstractUnitOfWork, None]:
    async with database.get_session() as session:
        async with SQLAlchemyUnitOfWork(session) as uow:
            yield uow
