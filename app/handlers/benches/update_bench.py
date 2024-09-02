from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards import keyboard as kb
from app.utils.states import EditBench, EditBenchOpen

router = Router()


@router.callback_query(lambda c: c.data == "edit_bench_open")
async def edit_bench_open(callback: CallbackQuery, state: FSMContext):
    original_text = callback.message.text
    await state.update_data(original_text=original_text)
    await callback.message.edit_text(
        "Выберите какой пункт изменить", reply_markup=kb.edit_bench
    )
    await state.set_state(EditBenchOpen.edit_bench_open)


@router.callback_query(lambda c: c.data == "edit_bench_cancel")
async def edit_bench_cancel(callback: CallbackQuery, state: FSMContext):
    original_text = (await state.get_data()).get("original_text")
    if original_text:
        await callback.message.edit_text(
            original_text, reply_markup=kb.del_or_edit_bench
        )
    else:
        await callback.message.edit_text(
            "Исходный текст не найден", reply_markup=kb.del_or_edit_bench
        )
    await state.clear()


@router.callback_query(lambda c: c.data == "edit_bench_name")
async def edit_bench_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое название", reply_markup=kb.cancel)
    await state.set_state(EditBench.name)


@router.message(EditBench.name)
async def process_name(message: Message, state: FSMContext):
    new_name = message.text
    await state.update_data(name=new_name)
    await message.answer("Название обновлено успешно", reply_markup=kb.main)
    await state.clear()


@router.callback_query(lambda c: c.data == "edit_bench_description")
async def edit_bench_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое описание", reply_markup=kb.cancel)
    await state.set_state(EditBench.description)


@router.message(EditBench.description)
async def process_description(message: Message, state: FSMContext):
    new_description = message.text
    await state.update_data(description=new_description)
    await message.answer("Описание обновлено успешно", reply_markup=kb.main)
    await state.clear()


@router.callback_query(lambda c: c.data == "edit_bench_count")
async def edit_bench_count(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое количество", reply_markup=kb.cancel)
    await state.set_state(EditBench.count)


@router.message(EditBench.count)
async def process_count(message: Message, state: FSMContext):
    new_count = message.text
    if new_count.isdigit():
        await state.update_data(count=new_count)
        await message.answer("Количество обновлено успешно", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer(
            "❌<b>Введите корректное число!</b>", reply_markup=kb.cancel
        )
