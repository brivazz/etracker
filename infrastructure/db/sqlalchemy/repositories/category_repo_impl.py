from sqlalchemy import select, delete, update as sqlalchemy_update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.category import CategoryCreate, CategoryInDb
from domain.repositories.category_repo import AbstractCategoryRepository
from infrastructure.db.sqlalchemy.models import UserORM
from infrastructure.db.sqlalchemy.models import CategoryORM
from application.mappers.category_mapper import CategoryMapper, CategoryInDBMapper

class SQLAlchemyCategoryRepository(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_create_mapper = CategoryMapper()
        self.category_indb_mapper = CategoryInDBMapper()


    async def add(self, category: CategoryCreate) -> CategoryInDb:
        try:
            category_orm = await self.category_create_mapper.entity_to_orm(category)
            self.session.add(category_orm)
            await self.session.flush()
            await self.session.refresh(category_orm)
            category_entity = await self.category_indb_mapper.orm_to_entity(category_orm)
            return category_entity
        except IntegrityError:
            await self.session.rollback()
            stmt = select(CategoryORM).where(CategoryORM.name == category.name)
            result = await self.session.execute(stmt)
            existing_orm = result.scalar_one_or_none()

            if not existing_orm:
                raise ValueError(f"Category with name '{category.name}' exists, but not found in DB")

            category_entity = await self.category_indb_mapper.orm_to_entity(existing_orm)
            return category_entity

    async def get_user_categories(self, user_id: int) -> list[CategoryInDb] | list:
        stmt = (
            select(UserORM)
            .options(joinedload(UserORM.categories))
            .where(UserORM.id == user_id)
        )
        result = await self.session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        if not user:
                return []
        return [await self.category_indb_mapper.orm_to_entity(e) for e in user.categories]
