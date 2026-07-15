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


class EditProfile(StatesGroup):
    value = State()


class FoodScan(StatesGroup):
    photo = State()

    confirm = State()


class HabitInput(StatesGroup):
    water = State()

    steps = State()

    sleep = State()

    weight = State()


class AdminSearch(StatesGroup):
    personal_id = State()
