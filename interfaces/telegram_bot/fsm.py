from interfaces.telegram_bot.utils.state_manager import fsm as _fsm

class FSM:
    def __init__(self, fsm):
        self._fsm = fsm

    async def get_user(self, telegram_id):
        return await self._fsm.get_user(telegram_id)

    async def set_user(self, telegram_id, user):
        await self._fsm.set_user(telegram_id, user)

    async def set_data(self, telegram_id, key, value):
        await self._fsm.set_data(telegram_id, key, value)

    async def get_data(self, telegram_id, key, default=None):
        return await self._fsm.get_data(telegram_id, key, default)

    async def set_state(self, telegram_id, state):
        await self._fsm.set_state(telegram_id, state)

    async def get_state(self, telegram_id):
        return await self._fsm.get_state(telegram_id)

fsm = FSM(_fsm)
