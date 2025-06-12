# Сценарии (use-cases)
from pydantic import BaseModel
from application.orchestrators.user_orchestrator import UserOrchestrator
from application.orchestrators.expense_orchestrator import ExpenseOrchestrator
from application.orchestrators.category_orchestrator import CategoryOrchestrator
from application.dto.user_dto import UserCreateDTO, UserIdDTO
from application.dto.expense_dto import (
    ExpenseCreateDTO,
    ExpenseDeleteDTO,
    ExpenseHistoryPeriodDTO,
    ExpenseEditDTO,
)
from application.dto.category_dto import CategoryCreateDTO
from application.dto.stats_dto import StatsRequestDTO
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from application.commands.command_enum import Command


class MainOrchestrator:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle_command(self, command: Command, dto: BaseModel):
        if command == Command.REGISTER_OR_GET_USER:
            if not isinstance(dto, UserCreateDTO):
                raise ValueError("Invalid DTO for register_user")

            orchestrator = UserOrchestrator(self.uow)
            return await orchestrator.register_or_get_user(dto)

        elif command == Command.ADD_EXPENSE:
            if not isinstance(dto, ExpenseCreateDTO):
                raise ValueError("Invalid DTO for add_expense")

            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.add_expense(dto)

        elif command == Command.DELETE_EXPENSE:
            if not isinstance(dto, ExpenseDeleteDTO):
                raise ValueError("Invalid DTO for delete_expense")

            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.delete_expense(dto)

        elif command == Command.GET_LAST_EXPENSE:
            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.get_last_expense()

        elif command == Command.GET_EXPENSE_HISTORY:
            if not isinstance(dto, ExpenseHistoryPeriodDTO):
                raise ValueError("Invalid DTO for get_expense_history")

            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.get_expense_history(dto)

        elif command == Command.EDIT_EXPENSE:
            if not isinstance(dto, ExpenseEditDTO):
                raise ValueError("Invalid DTO for edit_expense")

            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.edit_expense(dto)

        elif command == Command.GET_STATS_EXPENSE:
            if not isinstance(dto, StatsRequestDTO):
                raise ValueError("Invalid DTO for get_stats_expense")
            orchestrator = ExpenseOrchestrator(self.uow)
            return await orchestrator.get_stats(dto)

        elif command == Command.GET_USER_CATEGORIES:
            if not isinstance(dto, UserIdDTO):
                raise ValueError("Invalid DTO for get_user_categories")

            orchestrator = CategoryOrchestrator(self.uow)
            return await orchestrator.get_user_categories(dto.user_id)

        elif command == Command.ADD_CATEGORY:
            if not isinstance(dto, CategoryCreateDTO):
                raise ValueError("Invalid DTO for add_category")

            orchestrator = CategoryOrchestrator(self.uow)
            return await orchestrator.add_category(dto)

        else:
            raise ValueError(f"Unknown command: {command}")
