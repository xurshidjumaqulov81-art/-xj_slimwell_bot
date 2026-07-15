from aiogram.fsm.state import State, StatesGroup

class AdminSearch(StatesGroup):
    waiting_for_user_id = State()
