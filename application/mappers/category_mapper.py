from domain.entities.category import CategoryCreate, CategoryInDb
from application.dto.category_dto import CategoryCreateDTO, CategoryInDBDTO
from infrastructure.db.sqlalchemy.models import CategoryORM
from application.mappers.base_mapper import BaseMapper


class CategoryMapper(BaseMapper[CategoryCreateDTO, CategoryCreate, CategoryORM]):
    dto_cls = CategoryCreateDTO
    entity_cls = CategoryCreate
    orm_cls = CategoryORM


class CategoryInDBMapper(BaseMapper[CategoryInDBDTO, CategoryInDb, CategoryORM]):
    dto_cls = CategoryInDBDTO
    entity_cls = CategoryInDb
    orm_cls = CategoryORM