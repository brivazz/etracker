from io import BytesIO
from typing import cast
from telethon import events
from interfaces.telegram_bot.utils.plot import generate_pie_chart, generate_bar_chart_bytes
from application.commands.command_enum import Command
from application.dto.stats_dto import StatsRequestDTO, StatsPeriodEnum, StatsPeriodDTO
from application.dto.user_dto import UserInDBDTO
from config import logger
from domain.uow.abstract import AbstractUnitOfWork
from interfaces.telegram_bot.utils.state_manager import FSMManager
from interfaces.telegram_bot.keyboards.build_stats_keyboard import after_click_stats_expense_keyboard, expense_history_keyboard_keyboard, after_expense_history_period_keyboard
from interfaces.telegram_bot.keyboards.common_keyboard import show_error_keyboard, default_nav_buttons_keyboard
from application.dto.expense_dto import ExpenseHistoryPeriodDTO, ExpenseHistoryDTO
from interfaces.telegram_bot.handlers.orchestrators.base_orchestrator import OrchestratorBase


class StatsOrchestrator(OrchestratorBase):
    def __init__(self, uow: AbstractUnitOfWork, fsm: FSMManager):
        super().__init__(uow)
        self.uow = uow
        self.fsm = fsm


    async def show_keyboard_stats_expense(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажатия Статистика."""
        await after_click_stats_expense_keyboard(event)


    async def handle_stats_period(self, event: events.CallbackQuery.Event, user: UserInDBDTO, period: str):
        """Тут после нажатия на период статистики(Сегодня,Эта неделя,Этот месяц)"""
        dto = StatsRequestDTO(user_id=user.id, period=StatsPeriodEnum(period))
        stats = cast(StatsPeriodDTO, await self._handle(Command.GET_STATS_EXPENSE, dto))

        if not stats.stats:
            await show_error_keyboard(event, "Нет данных за выбранный период.")
            return

        period_label: str = dto.period.label()  # Enum.label()
        total = sum(s.total_amount for s in stats.stats)

        # chart_path = generate_bar_chart(
        #     data={s.category_name: s.total_amount for s in stats.stats},
        #     period_label=period_label,
        #     from_date=stats.from_date,
        #     to_date=stats.to_date
        # )
        # logger.info(f"Chart saved to: {chart_path}")

        chart_buf: BytesIO = generate_bar_chart_bytes(
            data={s.category_name: s.total_amount for s in stats.stats},
            period_label=period_label,
            from_date=stats.from_date,
            to_date=stats.to_date
        )
        await event.client.send_file(
            event.chat_id,
            # chart_path,
            file=chart_buf,
            caption=(
                f"📊 Расходы за {period_label} "
                f"({stats.from_date.strftime('%d.%m')} – {stats.to_date.strftime('%d.%m')})\n"
                f"💸 Всего: {total:.2f}₽"
            ),
            buttons=await default_nav_buttons_keyboard()
        )
        await event.edit()
        chart_buf.close()


    async def show_keyboard_expense_history(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        """Тут после нажания на История трат."""
        return await expense_history_keyboard_keyboard(event)


    async def handle_expense_history_period(self, event: events.CallbackQuery.Event, user: UserInDBDTO, period: str):
        """Тут после нажатия на период истории трат(По дням,По неделям,По месяцам,По годам)."""
        dto = ExpenseHistoryPeriodDTO(user_id=user.id, period=period)
        history = cast(list[ExpenseHistoryDTO], await self._handle(Command.GET_EXPENSE_HISTORY, dto))

        if not history:
            await show_error_keyboard(event, text="История трат пуста за выбранный период.")
            return

        period_title = {
            "day": "по дням",
            "week": "по неделям",
            "month": "по месяцам",
            "year": "по годам"
        }[period]

        text_lines = [f"<b>🧾 История трат {period_title}:</b>\n"]
        for record in history:
            text_lines.append(
                f"<b>{record.date.strftime('%d.%m.%Y')}:</b> "
                f"{record.category_name} — {record.count} раз(а) на {record.total_amount:.2f}₽"
            )
        await after_expense_history_period_keyboard(event, text_lines)


