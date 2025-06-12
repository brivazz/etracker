from domain.entities.user import UserCreate, UserInDB, UserID
from application.dto.user_dto import UserCreateDTO, UserInDBDTO, UserIdDTO
from infrastructure.db.sqlalchemy.models import UserORM
from application.mappers.base_mapper import BaseMapper


class UserMapper(BaseMapper[UserCreateDTO, UserCreate, UserORM]):
    dto_cls = UserCreateDTO
    entity_cls = UserCreate
    orm_cls = UserORM


class UserInDBMapper(BaseMapper[UserInDBDTO, UserInDB, UserORM]):
    dto_cls = UserInDBDTO
    entity_cls = UserInDB
    orm_cls = UserORM


class UserIDMapper(BaseMapper[UserIdDTO, UserID, UserORM]):
    dto_cls = UserIdDTO
    entity_cls = UserID
    orm_cls = UserORM
