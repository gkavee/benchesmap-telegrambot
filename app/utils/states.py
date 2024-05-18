from aiogram.fsm.state import StatesGroup, State


class GeoState(StatesGroup):
    waiting_for_location = State()


class BenchForm(StatesGroup):
    name = State()
    description = State()
    count = State()
    latitude = State()
    longitude = State()


class BenchDelete(StatesGroup):
    name = State()
