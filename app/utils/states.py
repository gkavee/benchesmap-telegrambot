from aiogram.fsm.state import State, StatesGroup


class GeoState(StatesGroup):
    waiting_for_location = State()


class BenchForm(StatesGroup):
    id = State
    name = State()
    description = State()
    count = State()
    latitude = State()
    longitude = State()
    photo_url = State()


class BenchDelete(StatesGroup):
    name = State()


class EditBenchOpen(StatesGroup):
    edit_bench_open = State()
    edit_bench_cancel = State()


class EditBench(StatesGroup):
    name = State()
    description = State()
    count = State()
    latitude = State()
    longitude = State()
