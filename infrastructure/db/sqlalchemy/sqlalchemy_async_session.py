from asyncio import timeout
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from config import settings, logger


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""

    pass


class Database:
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(
            settings.db_url, echo=settings.db_echo, future=True
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def create_database(self) -> None:
        """Создает все таблицы в базе данных"""
        import infrastructure.db.sqlalchemy.models

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"✅ Таблицы созданы! {list(Base.metadata.tables.keys())}")

    async def drop_database(self) -> None:
        """Удаляет все таблицы из базы данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Генератор сессий для DI"""
        async with self.async_session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def check_connection(self) -> bool:
        try:
            async with timeout(3):  # Таймаут 3 секунды
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))  # select(1)
            logger.info("✅ Подключение к БД успешно")
            return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            return False


database = Database()
