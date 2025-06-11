from application.mappers.base_mapper import BaseMapper
from application.dto.stats_dto import StatsRequestDTO, StatsInDbDTO
from domain.entities.stats import StatsInDb

class StatsInDbMapper(BaseMapper[StatsInDbDTO, StatsInDb, None]):
    dto_cls = StatsInDbDTO
    entity_cls = StatsInDb
    orm_cls = None  # ORM-таблицы для этого объекта нет

    async def entity_to_dto(self, entity: StatsInDb) -> StatsInDbDTO:
        return self.dto_cls(
            category_name=entity.category_name,
            total_amount=entity.total_amount
        )

    async def dto_to_entity(self, dto: StatsInDbDTO) -> StatsInDb:
        return self.entity_cls(
            category_name=dto.category_name,
            total_amount=dto.total_amount
        )

    async def entity_to_orm(self, entity: StatsInDb):
        raise NotImplementedError("Not supported")

    async def orm_to_entity(self, orm):
        raise NotImplementedError("Not supported")
