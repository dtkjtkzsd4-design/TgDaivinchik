from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    looking_for = State()
    city = State()
    about = State()
    photo = State()


class EditProfile(StatesGroup):
    value = State()


class SettingsStates(StatesGroup):
    age_range = State()
