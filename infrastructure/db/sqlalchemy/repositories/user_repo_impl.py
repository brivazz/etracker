from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from domain.entities.user import UserCreate, UserInDB
from domain.entities.category import CategoryInDb
from domain.repositories.user_repo import AbstractUserRepository
from infrastructure.db.sqlalchemy.models import UserORM
from application.mappers.user_mapper import UserMapper, UserInDBMapper


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_create_mapper = UserMapper()
        self.user_indb_mapper = UserInDBMapper()

    async def add(self, user: UserCreate) -> UserInDB:
        user_orm = await self.user_create_mapper.entity_to_orm(user)
        self.session.add(user_orm)
        await self.session.flush()
        await self.session.refresh(user_orm)
        user_entity = await self.user_indb_mapper.orm_to_entity(user_orm)
        return user_entity

    async def get_by_telegram_id(self, telegram_id: int) -> UserInDB | None:
        result = await self.session.execute(
            select(UserORM).where(UserORM.telegram_id == telegram_id)
        )
        orm_user = result.scalar_one_or_none()
        return await self.user_indb_mapper.orm_to_entity(orm_user) if orm_user else None

    async def get_by_id(self, user_id: int) -> UserInDB | None:
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm_user = result.scalar_one_or_none()
        return await self.user_indb_mapper.orm_to_entity(orm_user) if orm_user else None

    async def update(self, user: UserInDB) -> UserInDB:
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            raise ValueError(f"User with id {user.id} not found")

        orm.username = user.username
        orm.balance = user.balance
        await self.session.flush()
        await self.session.refresh(orm)
        return await self.user_indb_mapper.orm_to_entity(orm)

    async def get_user_categories(self, user_id: int) -> list[CategoryInDb] | list:
        stmt = (
            select(UserORM)
            .options(joinedload(UserORM.categories))
            .where(UserORM.id == user_id)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return []
        return [
            await self.category_indb_mapper.orm_to_entity(e) for e in user.categories
        ]
