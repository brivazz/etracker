from abc import ABC
from typing import TypeVar, Generic, Type
from dataclasses import asdict, is_dataclass
from pydantic import BaseModel

TDto = TypeVar("TDto", bound=BaseModel)
TEntity = TypeVar("TEntity")
TOrm = TypeVar("TOrm")


class BaseMapper(Generic[TDto, TEntity, TOrm], ABC):

    dto_cls: Type[TDto]
    entity_cls: Type[TEntity]
    orm_cls: Type[TOrm]

    async def dto_to_entity(self, dto: TDto) -> TEntity:
        return self.entity_cls(**dto.model_dump())

    async def entity_to_dto(self, entity: TEntity) -> TDto:
        if is_dataclass(entity) and not isinstance(entity, type):
            return self.dto_cls(**asdict(entity))
        return self.dto_cls(**vars(entity))

    async def orm_to_entity(self, orm: TOrm) -> TEntity:
        if self.orm_cls is None:
            raise NotImplementedError("ORM not defined in this mapper")
        orm_dict = {
            k: v
            for k, v in vars(orm).items()
            if not k.startswith("_") and not callable(v)
        }
        return self.entity_cls(**orm_dict)

    async def entity_to_orm(self, entity: TEntity) -> TOrm:
        if is_dataclass(entity) and not isinstance(entity, type):
            return self.orm_cls(**asdict(entity))
        return self.orm_cls(**vars(entity))
