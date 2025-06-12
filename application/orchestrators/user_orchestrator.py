# логика регистрации, получения баланса
from domain.uow.abstract import AbstractUnitOfWork
from application.dto.user_dto import UserCreateDTO, UserInDBDTO
from application.factories.service_factory import get_user_service
from application.mappers.user_mapper import UserMapper, UserInDBMapper, UserIDMapper


class UserOrchestrator:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.user_create_mapper = UserMapper()
        self.user_indb_mapper = UserInDBMapper()
        self.user_id_mapper = UserIDMapper()

    async def register_or_get_user(self, user: UserCreateDTO) -> UserInDBDTO:
        user_service = await get_user_service(self.uow.user_repo)
        user_entity = await self.user_create_mapper.dto_to_entity(user)
        if user_in_db := await user_service.get_by_telegram_id(user_entity):
            user_dto = await self.user_indb_mapper.entity_to_dto(user_in_db)
        else:
            user_entity = await user_service.create_user(user_entity)
            user_dto = await self.user_indb_mapper.entity_to_dto(user_entity)
        return user_dto

    # async def get_by_telegram_id(self, user: UserCreateDTO) -> UserInDBDTO | None:
    #     user_service = await get_user_service(self.uow.user_repo)
    #     print('uow.user_repo', self.uow.user_repo)
    #     user_entity = self.user_create_mapper.dto_to_entity(user)
    #     user_entity = await user_service.get_by_telegram_id(user_entity)
    #     user_dto = self.user_indb_mapper.entity_to_dto(user_entity)
    #     return user_dto
