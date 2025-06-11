# логика добавления, получения, редактирования расходов
from domain.uow.abstract import AbstractUnitOfWork
from application.factories.service_factory import get_expense_service
from domain.entities.expense import ExpenseCreate, ExpenseInDB, ExpenseHistory
from application.mappers.expense_mapper import ExpenseCreateMapper, ExpenseInDBMapper, ExpenseHistoryMapper, ExpenseHistoryResultMapper, ExpenseEditMapper
from application.mappers.stats_mapper import StatsInDbMapper
from application.dto.expense_dto import ExpenseCreateDTO, ExpenseInDBDTO, ExpenseHistoryDTO, ExpenseHistoryPeriodDTO, ExpenseEditDTO, ExpenseDeleteDTO
from application.dto.stats_dto import StatsRequestDTO, StatsInDbDTO, StatsPeriodDTO
from domain.entities.stats import StatsPeriodSummary, StatsInDb

class ExpenseOrchestrator:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.expense_create_mapper = ExpenseCreateMapper()
        self.expense_indb_mapper = ExpenseInDBMapper()
        self.stats_mapper = StatsInDbMapper()
        self.expense_history_mapper = ExpenseHistoryMapper()
        self.expense_history_resut_mapper = ExpenseHistoryResultMapper()
        self.expense_edit_mapper = ExpenseEditMapper()

    async def add_expense(self, expense: ExpenseCreateDTO) -> ExpenseInDBDTO:
        expense_service = await get_expense_service(self.uow.expense_repo)
        expense_entity = await self.expense_create_mapper.dto_to_entity(expense)
        expense_entity = await expense_service.add_expense(expense_entity) # type: ignore -> ExpenseInDB
        expense_dto = await self.expense_indb_mapper.entity_to_dto(expense_entity)
        return expense_dto

    async def delete_expense(self, expense: ExpenseDeleteDTO) -> bool:
        expense_service = await get_expense_service(self.uow.expense_repo)
        success = await expense_service.delete_expense(expense.id)
        if not success:
            raise ValueError("Expense not found")
        return success

    async def edit_expense(self, dto: ExpenseEditDTO) -> ExpenseInDBDTO:
        expense_service = await get_expense_service(self.uow.expense_repo)
        expense_entity = await self.expense_edit_mapper.dto_to_entity(dto)
        existing_expense = await expense_service.get_by_id(expense_entity.id)
        if not existing_expense:
            raise ValueError("Expense not found")

        existing_expense.amount = dto.amount
        existing_expense.category_id = dto.category_id
        existing_expense.note = dto.note
        updated = await self.uow.expense_repo.update(existing_expense)
        return await self.expense_indb_mapper.entity_to_dto(updated)


    async def get_stats(self, stats_dto: StatsRequestDTO) -> StatsPeriodDTO:
        expense_service = await get_expense_service(self.uow.expense_repo)

        period_summary: StatsPeriodSummary = await expense_service.get_stats(
            user_id=stats_dto.user_id,
            period=stats_dto.period
        )

        stats_dto_list: list[StatsInDbDTO] = [
            await self.stats_mapper.entity_to_dto(e)
            for e in period_summary.stats  # list[StatsInDb]
        ]

        return StatsPeriodDTO(
            stats=stats_dto_list,
            from_date=period_summary.from_date,
            to_date=period_summary.to_date
        )

    async def get_expense_history(self, history_dto: ExpenseHistoryPeriodDTO) -> list[ExpenseHistoryDTO]:
        expense_service = await get_expense_service(self.uow.expense_repo)
        expense_entity = await self.expense_history_mapper.dto_to_entity(history_dto)
        history_entities: list[ExpenseHistory] = await expense_service.get_expense_history(expense_entity)

        return [
            await self.expense_history_resut_mapper.entity_to_dto(e)
            for e in history_entities
        ]