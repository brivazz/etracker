# Преобразование DTO ↔ Entity — через мэппер, и это лучше, чем dict или **kwargs

from domain.entities.user import UserCreate, UserInDB, UserID
from application.dto.user_dto import UserCreateDTO, UserInDBDTO, UserIdDTO
from infrastructure.db.sqlalchemy.models import UserORM
from application.mappers.base_mapper import BaseMapper

# async def dto_to_entity(dto: UserCreateDTO) -> UserCreate:
#     return UserCreate(username=dto.username, balance=dto.balance)#, created_at=datetime.now(timezone.utc))
# async def entity_to_dto(user: UserInDB) -> UserInDBDTO:
#     return UserInDBDTO(**asdict(user))
# async def orm_to_entity(orm: UserORM) -> UserInDB:
#     return UserInDB(
#         id=orm.id,
#         username=orm.username,
#         balance=orm.balance,
#         created_at=orm.created_at,
#         updated_at=orm.updated_at
#     )
# async def entity_to_orm(user: UserInDB) -> UserORM:
#     return UserORM(
#         id=user.id if user.id else None,
#         username=user.username,
#         balance=user.balance
#     )
# async def create_to_orm(user_create: UserCreate) -> UserORM:
#     return UserORM(
#         username=user_create.username,
#         balance=user_create.balance,
#     )
# async def indb_to_orm(user_indb: UserInDB) -> UserORM:
#     return UserORM(
#         id=user_indb.id,
#         username=user_indb.username,
#         balance=user_indb.balance,
#         created_at=user_indb.created_at,
#         updated_at=user_indb.updated_at
#     )

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

