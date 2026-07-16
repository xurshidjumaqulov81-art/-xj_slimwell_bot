from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    language = State()
    personal_id = State()
    name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    goal = State()
    activity = State()


# Backward-compatible alias for older code.
Registration = Onboarding


class EditProfile(StatesGroup):
    value = State()


class HabitInput(StatesGroup):
    water = State()
    steps = State()
    sleep = State()
    weight = State()


class FoodInput(StatesGroup):
    photo = State()
    description = State()


class AdminState(StatesGroup):
    broadcast = State()
    search = State()

