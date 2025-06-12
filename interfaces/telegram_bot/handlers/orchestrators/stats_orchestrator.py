from io import BytesIO
from typing import cast
from telethon import events
from telethon.tl.functions.messages import EditMessageRequest
from telethon.tl.types import (
    InputMediaUploadedPhoto,
    ReplyInlineMarkup,
    KeyboardButtonCallback,
    KeyboardButtonRow,
)

from interfaces.telegram_bot.utils.plot import (
    generate_pie_chart,
    generate_bar_chart_bytes,
)
from application.commands.command_enum import Command
from application.dto.stats_dto import StatsRequestDTO, StatsPeriodEnum, StatsPeriodDTO
from application.dto.user_dto import UserInDBDTO
from config import logger
from domain.uow.abstract import AbstractUnitOfWork
from interfaces.telegram_bot.utils.state_manager import (
    FSMManager,
    State,
    get_message_id,
)
from interfaces.telegram_bot.keyboards.build_stats_keyboard import (
    after_click_stats_expense_keyboard,
    expense_history_keyboard_keyboard,
    after_expense_history_period_keyboard,
)
from interfaces.telegram_bot.keyboards.common_keyboard import (
    show_error_keyboard,
    default_nav_buttons_keyboard,
)
from application.dto.expense_dto import ExpenseHistoryPeriodDTO, ExpenseHistoryDTO
from interfaces.telegram_bot.handlers.orchestrators.base_orchestrator import (
    OrchestratorBase,
)
from interfaces.telegram_bot.utils.state_manager import ExpenseMeta


class StatsOrchestrator(OrchestratorBase):
    def __init__(self, uow: AbstractUnitOfWork, fsm: FSMManager):
        super().__init__(uow)
        self.uow = uow
        self.fsm = fsm

    async def show_keyboard_stats_expense(
        self, event: events.CallbackQuery.Event, user: UserInDBDTO
    ):
        """Тут после нажатия Статистика."""
        message = await after_click_stats_expense_keyboard(event)
        await self.fsm.set_state(
            user.telegram_id,
            State.SHOW_STATS_KEYBOARD,
            meta=ExpenseMeta(
                message_id=message.id,
            ),
        )

    async def handle_stats_period(
        self, event: events.CallbackQuery.Event, user: UserInDBDTO, period: str
    ):
        """Тут после нажатия на период статистики(Сегодня,Эта неделя,Этот месяц)"""
        dto = StatsRequestDTO(user_id=user.id, period=StatsPeriodEnum(period))
        stats = cast(StatsPeriodDTO, await self._handle(Command.GET_STATS_EXPENSE, dto))

        if not stats.stats:
            await show_error_keyboard(event, "Нет данных за выбранный период.")
            return

        period_label: str = dto.period.label()  # Enum.label()
        total = sum(s.total_amount for s in stats.stats)

        chart_buf: BytesIO = generate_bar_chart_bytes(
            data={s.category_name: s.total_amount for s in stats.stats},
            period_label=period_label,
            from_date=stats.from_date,
            to_date=stats.to_date,
        )
        markup = ReplyInlineMarkup(
            rows=[
                KeyboardButtonRow(
                    buttons=[
                        KeyboardButtonCallback(text="◀️ Назад", data=b"back"),
                    ]
                ),
                KeyboardButtonRow(
                    buttons=[
                        KeyboardButtonCallback(text="🏠 На главную", data=b"home"),
                    ]
                ),
            ]
        )
        message_id = await get_message_id(self.fsm, user.telegram_id)
        uploaded = await event.client.upload_file(chart_buf)

        await event.client(
            EditMessageRequest(
                peer=event.chat_id,
                id=message_id,
                media=InputMediaUploadedPhoto(file=uploaded),
                message=(
                    f"📊 Расходы за {period_label} "
                    f"({stats.from_date.strftime('%d.%m')} – {stats.to_date.strftime('%d.%m')})\n"
                    f"💸 Всего: {total:.2f}₽"
                ),
                reply_markup=markup,
            )
        )
        chart_buf.close()
        await self.fsm.set_state(
            user.telegram_id,
            State.SHOW_STATS_KEYBOARD,
            meta=ExpenseMeta(
                message_id=message_id,
            ),
        )

    async def show_keyboard_expense_history(
        self, event: events.CallbackQuery.Event, user: UserInDBDTO
    ):
        """Тут после нажания на История трат."""
        message = await expense_history_keyboard_keyboard(event)
        await self.fsm.set_state(
            user.telegram_id,
            State.SHOW_STATS_KEYBOARD,
            meta=ExpenseMeta(
                message_id=message.id,
            ),
        )

    async def handle_expense_history_period(
        self, event: events.CallbackQuery.Event, user: UserInDBDTO, period: str
    ):
        """Тут после нажатия на период истории трат(По дням,По неделям,По месяцам,По годам)."""
        dto = ExpenseHistoryPeriodDTO(user_id=user.id, period=period)
        history = cast(
            list[ExpenseHistoryDTO],
            await self._handle(Command.GET_EXPENSE_HISTORY, dto),
        )

        if not history:
            await show_error_keyboard(
                event, text="История трат пуста за выбранный период."
            )
            return

        period_title = {
            "day": "по дням",
            "week": "по неделям",
            "month": "по месяцам",
            "year": "по годам",
        }[period]

        text_lines = [f"<b>🧾 История трат {period_title}:</b>\n"]
        for record in history:
            text_lines.append(
                f"<b>{record.date.strftime('%d.%m.%Y')}:</b> "
                f"{record.category_name} — {record.count} раз(а) на {record.total_amount:.2f}₽"
            )
        await after_expense_history_period_keyboard(event, text_lines)
