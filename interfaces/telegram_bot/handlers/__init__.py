from telethon import events
from domain.uow.abstract import AbstractUnitOfWork
from application.factories.uow_factories import get_uow
from interfaces.telegram_bot.utils.state_manager import fsm, FSMManager, State, Data, parse_callback_data
from interfaces.telegram_bot.handlers.orchestrators.add_orchestrator import AddOrchestrator
from interfaces.telegram_bot.handlers.orchestrators.category_orchestrator import CategoryOrchestrator
from interfaces.telegram_bot.handlers.orchestrators.stats_orchestrator import StatsOrchestrator
from interfaces.telegram_bot.handlers.orchestrators.common_orchestrator import CommonOrchestrator
from application.dto.user_dto import UserInDBDTO
from interfaces.telegram_bot.keyboards.common_keyboard import show_error_keyboard
from interfaces.telegram_bot.router import router
from config import logger


class BotService:
    def __init__(self, fsm: FSMManager, uow: AbstractUnitOfWork):
        self.fsm = fsm
        self.uow = uow
        self._init_orchestrators()
        self._register_messages()
        self._register_callbacks()

    def _init_orchestrators(self):
        self.add_orchestrator = AddOrchestrator(self.uow, self.fsm)
        self.category_orchestrator = CategoryOrchestrator(self.uow, self.fsm)
        self.stats_orchestrator = StatsOrchestrator(self.uow, self.fsm)
        self.common_orchestrator = CommonOrchestrator(self.uow, self.fsm)

    def _register_callbacks(self):
        self.callback_handlers = {
            # ТРАТЫ:
            # добавить
            Data.ADD_EXPENSE: self.add_orchestrator.add_expense, # Добавить трату
            # выбрать категорию
            Data.CATEGORY_SELECTION: self.add_orchestrator.handle_category_selection, # Тут после нажатия на категорию/при выборе категории
            # сохранить трату
            Data.SAVE_EXPENSE: self.add_orchestrator.save_new_expense,
            # Перед сохранением изменить запись
            Data.CHANGE_ENTRY: self.add_orchestrator.change_entry,
            # # Изменяем введенные данные
            # Data.CHANGE_CATEGORY: self.add_orchestrator.handle_change_entry_category,
            # изменить последнюю
            Data.EDIT_EXPENSE: self.add_orchestrator.edit_last_expense, # Тут после нажатия на редактирование последней траты
            # повторить последнюю
            Data.REPEAT_EXPENSE: self.add_orchestrator.handle_repeat_last_expense, # Тут после нажатия Повторить последнюю
            # удалить последнюю
            Data.DELETE_EXPENSE: self.add_orchestrator.handle_delete_last_expense, # Тут после нажатия Удалить последнюю
            # ============================================
            # ИСТОРИЯ ТРАТ:
            Data.HISTORY: self.stats_orchestrator.show_keyboard_expense_history, # Тут после нажания на История трат
            # выбор по дням, неделям, месяцам, годам
            Data.HISTORY_SELECTION: self.stats_orchestrator.handle_expense_history_period, # Тут после нажатия на период истории трат(По дням,По неделям,По месяцам,По годам)
            # ============================================
            # КАТЕГОРИИ: добавить категорию
            Data.ADD_CATEGORY: self.category_orchestrator.show_keyboard_add_category, # Тут показывам клавиатуру при добавлении новой категории
            # ============================================
            # СТАТИСТИКА:
            Data.STATS_EXPENSE: self.stats_orchestrator.show_keyboard_stats_expense, # Тут после нажатия Статистика
            # сегодня, эта неделя, этот месяц
            Data.STATS_SELECTION: self.stats_orchestrator.handle_stats_period, # Тут после нажатия на период статистики(Сегодня,Эта неделя,Этот месяц)
            # ============================================
            # Общие
            Data.HOME: self.common_orchestrator.handle_home, # После нажатия кнопки Домой
            Data.CANCEL: self.common_orchestrator.handle_cancel, # После нажатия кнопки Отменить
            Data.BACK: self.common_orchestrator.handle_back, # После нажатия кнопки Назад
            # Data.START: self.common_orchestrator.start_flow,
        }

    def _register_messages(self):
        """Нужны для кнопок Назад, Отмена и при вводе сообщений(сумм,рандомных сообщений)."""
        self.message_handlers = {
            State.IDLE: self.common_orchestrator.start_flow,
            State.START: self.common_orchestrator.start_flow,
            State.ADD_EXPENSE: self.add_orchestrator.add_expense,  # Тут после нажатия Добавить трату
            State.EDIT_LAST_EXPENSE: self.add_orchestrator.handle_edit_expense,
            State.WAITING_FOR_CATEGORY: self.category_orchestrator.handle_add_category,
            State.SELECTED_A_CATEGORY: self.add_orchestrator.handle_amount_expense,
            State.CHANGE_ENTRY: self.add_orchestrator.handle_amount_expense,
        }


    async def handle_messages(self, event: events.NewMessage.Event, user: UserInDBDTO):
        current_state = await self.fsm.get_state(user.telegram_id)
        handler = self.message_handlers.get(current_state)
        logger.warning(f"HANDLER {handler}  CURRENT STATE: {current_state}")
        logger.info(f"в состоянии: == {current_state} == на всякий raw_text: {event.raw_text}")
        if handler is None:
            logger.warning(f"⚠️ Нет хендлера для состояния: {current_state}")
            await self.fsm.set_state(user.telegram_id, State.IDLE)
            return 
        await handler(event, user)


    async def handle_callbacks(self, event: events.CallbackQuery.Event, user: UserInDBDTO):
        data_enum, params = parse_callback_data(event.data)
        logger.info(f"нажал кнопку: {data_enum} с params: {params}")
        if not data_enum:
            await show_error_keyboard(event, "❌ Неизвестная команда.")
            return

        handler = self.callback_handlers.get(data_enum)
        if not handler:
            await show_error_keyboard(event, "❌ Нет обработчика для этой команды.")
            return

        await handler(event, user, *params)

    def register_handlers(self):
        @router.callback(Data)
        async def callback_handler(event: events.CallbackQuery.Event, user: UserInDBDTO):
            await self.handle_callbacks(event, user)

        @router.message()
        async def message_handler(event: events.NewMessage.Event, user: UserInDBDTO):
            await self.handle_messages(event, user)


bot_service = BotService(fsm, get_uow)
bot_service.register_handlers()
