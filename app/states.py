from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    language = State()
    name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    goal = State()
    activity = State()


class ProfileEdit(StatesGroup):
    name = State()
    age = State()
    height = State()
    weight = State()


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
