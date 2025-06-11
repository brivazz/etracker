from pydantic import BaseModel
from application.commands.command_enum import Command
from application.main_orchestrator import MainOrchestrator
from domain.uow.abstract import AbstractUnitOfWork


class OrchestratorBase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def _handle(self, command: Command, dto: BaseModel):
        async with self.uow() as uow:
            orchestrator = MainOrchestrator(uow)
            return await orchestrator.handle_command(command, dto)
