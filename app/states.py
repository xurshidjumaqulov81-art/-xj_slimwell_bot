from aiogram.fsm.state import State, StatesGroup


# =====================================
# REGISTRATION
# =====================================

class Registration(StatesGroup):
    language = State()
    name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    goal = State()
    activity = State()


# =====================================
# PROFILE EDIT
# =====================================

class EditProfile(StatesGroup):
    name = State()
    age = State()
    height = State()
    weight = State()


# =====================================
# HABITS
# =====================================

class HabitInput(StatesGroup):
    water = State()
    steps = State()
    sleep = State()
    weight = State()


# =====================================
# FOOD
# =====================================

class FoodInput(StatesGroup):
    photo = State()
    description = State()


# =====================================
# ADMIN
# =====================================

class AdminState(StatesGroup):
    broadcast = State()
    search = State()
