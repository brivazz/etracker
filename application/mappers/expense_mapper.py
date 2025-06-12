from domain.entities.expense import (
    ExpenseCreate,
    ExpenseInDB,
    ExpenseHistoryPeriod,
    ExpenseHistory,
    ExpenseEdit,
)
from application.dto.expense_dto import (
    ExpenseCreateDTO,
    ExpenseInDBDTO,
    ExpenseHistoryPeriodDTO,
    ExpenseHistoryDTO,
    ExpenseEditDTO,
)
from infrastructure.db.sqlalchemy.models import ExpenseORM
from application.mappers.base_mapper import BaseMapper


class ExpenseEditMapper(BaseMapper[ExpenseEditDTO, ExpenseEdit, ExpenseORM]):
    dto_cls = ExpenseEditDTO
    entity_cls = ExpenseEdit
    orm_cls = ExpenseORM


class ExpenseCreateMapper(BaseMapper[ExpenseCreateDTO, ExpenseCreate, ExpenseORM]):
    dto_cls = ExpenseCreateDTO
    entity_cls = ExpenseCreate
    orm_cls = ExpenseORM


class ExpenseInDBMapper(BaseMapper[ExpenseInDBDTO, ExpenseInDB, ExpenseORM]):
    dto_cls = ExpenseInDBDTO
    entity_cls = ExpenseInDB
    orm_cls = ExpenseORM


class ExpenseHistoryMapper(
    BaseMapper[ExpenseHistoryPeriodDTO, ExpenseHistoryPeriod, None]
):
    dto_cls = ExpenseHistoryPeriodDTO
    entity_cls = ExpenseHistoryPeriod
    orm_cls = None


class ExpenseHistoryResultMapper(BaseMapper[ExpenseHistoryDTO, ExpenseHistory, None]):
    dto_cls = ExpenseHistoryDTO
    entity_cls = ExpenseHistory
    orm_cls = None
