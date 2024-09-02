from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards.keyboard as kb
from app.handlers.benches.create_bench import router as create_bench_router
from app.handlers.benches.delete_bench import router as delete_bench_router
from app.handlers.benches.nearest_bench import router as nearest_bench_router
from app.handlers.benches.update_bench import router as update_bench_router

router = Router()

router.include_router(create_bench_router)
router.include_router(nearest_bench_router)
router.include_router(update_bench_router)
router.include_router(delete_bench_router)


@router.message(F.text.casefold() == "отмена❌")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    if current_state.startswith("GeoState"):
        await message.answer(
            "Поиск отменен",
            reply_markup=kb.main,
        )

    if current_state.startswith("BenchForm"):
        await message.answer(
            "Отменено создание лавочки",
            reply_markup=kb.main,
        )

    if current_state.startswith("BenchForm"):
        await message.answer(
            "Отменено редактирование лавочки",
            reply_markup=kb.main,
        )

    await state.clear()
