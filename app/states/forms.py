from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    goal = State()


class EditProfile(StatesGroup):
    field_value = State()


class HabitInput(StatesGroup):
    custom_water = State()
    steps = State()
    sleep = State()


class WeightInput(StatesGroup):
    weight = State()


class FoodScan(StatesGroup):
    waiting_photo = State()
    waiting_save = State()


class AdminSearch(StatesGroup):
    slimwell_id = State()
