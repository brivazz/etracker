from asyncio import timeout
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, select

from config import settings, logger

# from infrastructure.db.sqlalchemy.models import UserORM, ExpenseORM, CategoryORM, MessageORM, UserSettingsORM

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class Database:
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(
            settings.db_url,
            echo=settings.db_echo,
            future=True
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def create_database(self) -> None:
        """Создает все таблицы в базе данных"""
        import infrastructure.db.sqlalchemy.models
        # print("Таблицы, которые будут созданы:", Base.metadata.tables.keys())
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

# # ==================================
# # db/postgres.py
# from core.config import settings
# from sqlalchemy.orm import declarative_base, sessionmaker
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# # Создаём базовый класс для будущих моделей
# Base = declarative_base()
# # Создаём движок
# # Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
# dsn = f'postgresql+asyncpg://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.db}'
# engine = create_async_engine(dsn, echo=True, future=True)
# async_session = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )
# # ==================================

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_factory() as session:
#         yield session