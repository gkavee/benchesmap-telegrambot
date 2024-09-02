import aiohttp
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards import keyboard as kb
from app.utils.states import GeoState
from config import API_URL

router = Router()


@router.message(F.text == "🔍Найти лавочку")
async def find_nearest(message: Message, state: FSMContext) -> None:
    await state.set_state(GeoState.waiting_for_location)
    await message.answer("Отправьте геолокацию", reply_markup=kb.geo)


@router.message(GeoState.waiting_for_location)
async def send_location(message: Message, state: FSMContext) -> None:
    if message.location:
        lat = message.location.latitude
        long = message.location.longitude
        await message.answer(
            f"Вы отправили геолокацию с координатами: <code>{lat}</code>, <code>{long}</code>"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/nearest_bench/?latitude={lat}&longitude={long}"
            ) as response:
                data = await response.json()
                rs_lat = data["latitude"]
                rs_long = data["longitude"]
                rs_photo = data["photo_url"]
                await message.answer_photo(
                    photo=rs_photo,
                    caption=f"🪑Ближайшая лавочка находится по координатам: <code>{rs_lat}</code>, "
                    f"<code>{rs_long}</code>",
                    reply_markup=kb.main,
                )
                await message.reply_location(rs_lat, rs_long)
                await state.clear()
    else:
        await message.answer("❌<b>Отправьте геолокацию</b>", reply_markup=kb.geo)
