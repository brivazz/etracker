from domain.uow.abstract import AbstractUnitOfWork
from domain.services.category_service import CategoryService

from domain.entities.category import CategoryCreate, CategoryInDb
from application.dto.category_dto import CategoryCreateDTO, CategoryInDBDTO
from application.factories.service_factory import get_category_service
from application.mappers.category_mapper import CategoryMapper, CategoryInDBMapper

class CategoryOrchestrator:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.category_create_mapper = CategoryMapper()
        self.category_indb_mapper = CategoryInDBMapper()

    async def add_category(self, category: CategoryCreateDTO) -> CategoryInDBDTO:
        category_service = await get_category_service(self.uow.category_repo)
        category_entity = await self.category_create_mapper.dto_to_entity(category)
        category_entity = await category_service.add_category(category_entity) # -> ExpenseInDB
        category_dto = await self.category_indb_mapper.entity_to_dto(category_entity)
        return category_dto

    async def get_user_categories(self, user_id: int) -> list[CategoryInDBDTO]:
        category_service = await get_category_service(self.uow.category_repo)
        categories_entities = await category_service.get_user_categories(user_id)
        categories_dtos = [await self.category_indb_mapper.entity_to_dto(ce) for ce in categories_entities]
        return categories_dtos
