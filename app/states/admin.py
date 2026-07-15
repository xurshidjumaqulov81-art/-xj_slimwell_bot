from aiogram.fsm.state import State, StatesGroup

class AdminSearch(StatesGroup):
    personal_id = State()
