import html
from typing import Any, Dict

import aiohttp
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.keyboards import keyboard as kb
from app.utils.auth import get_token
from app.utils.states import BenchForm
from config import API_URL
from run import bot

router = Router()


@router.message(F.text == "➕Создать лавочку")
async def fill_bench(message: Message, state: FSMContext) -> None:
    await state.set_state(BenchForm.name)
    await message.answer("Введите название", reply_markup=kb.cancel)


@router.message(BenchForm.name)
async def bench_name(message: Message, state: FSMContext) -> None:
    if len(message.text) <= 50:
        esc_name = html.escape(message.text)
        await state.update_data(name=esc_name)
        await state.set_state(BenchForm.description)
        await message.answer("Опишите лавочку")
    else:
        await message.answer("❌<b>Максимальная длина названия — 50 символов!</b>")


@router.message(BenchForm.description)
async def bench_description(message: Message, state: FSMContext) -> None:
    if len(message.text) <= 200:
        esc_description = html.escape(message.text)
        await state.update_data(description=esc_description)
        await state.set_state(BenchForm.count)
        await message.answer("Количество?")
    else:
        await message.answer("❌<b>Максимальная длина описания — 200 символов!</b>")


@router.message(BenchForm.count)
async def bench_count(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data(count=message.text)
        await state.set_state(BenchForm.latitude)
        await message.answer("Отправьте вашу геолокацию", reply_markup=kb.geo)
    else:
        await message.answer("❌<b>Введите число!</b>")


@router.message(BenchForm.latitude)
async def bench_latitude(message: Message, state: FSMContext) -> None:
    if message.location:
        await state.update_data(latitude=message.location.latitude)
        await state.update_data(longitude=message.location.longitude)
        data = await state.get_data()
        bench_id = await create_post_request(message=message, data=data)
        if bench_id:
            await state.update_data(id=bench_id)
            await message.answer(
                "<b>Лавочка создана! Отправьте фото лавочки (если есть)</b>",
                reply_markup=None,
            )
            await state.set_state(BenchForm.photo_url)
        else:
            await state.clear()
            await message.answer(
                "Не удалось создать лавочку. Попробуйте еще раз.", reply_markup=kb.main
            )
    else:
        await message.answer("❌<b>Отправьте геолокацию!</b>", reply_markup=kb.geo)


@router.message(BenchForm.photo_url)
async def bench_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    username = message.from_user.username
    token = await get_token(username)

    data = await state.get_data()
    bench_id = data.get("id")

    if not bench_id:
        await message.answer(
            "❌<b>Не удалось определить лавочку для загрузки фото!</b>",
            reply_markup=kb.main,
        )
        return

    if not message.photo:
        await message.answer("❌<b>Пожалуйста, отправьте фото!</b>")
        return

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path

    input_file = FSInputFile(file_path, filename="bench_photo.jpg")

    cookies = {
        "token": token,
    }

    try:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            form = aiohttp.FormData()
            form.add_field(
                "file",
                await bot.download_file(file_path),
                filename=input_file.filename,
                content_type="image/jpeg",
            )

            async with session.post(
                f"{API_URL}/upload_bench_photo/{bench_id}",
                data=form,
            ) as response:
                response.raise_for_status()
                await message.answer(
                    "🖼️ <b>Фото успешно загружено!<b>", reply_markup=kb.main
                )
    except aiohttp.ClientResponseError as e:
        if e.status in [401, 404]:
            await message.answer(
                "❌<b>У вас нет доступа к загрузке фото!</b>", reply_markup=kb.main
            )
        else:
            await message.answer(
                "<b>Произошла ошибка при загрузке фото!</b>", reply_markup=kb.main
            )
    finally:
        await state.clear()


async def create_post_request(message: Message, data: Dict[str, Any]) -> int | None:
    payload = {
        "name": data["name"],
        "description": data["description"],
        "count": data["count"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
    }

    headers = {
        "Content-Type": "application/json",
    }

    username = message.from_user.username
    token = await get_token(username)

    cookies = {
        "token": token,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/create_bench",
                json=payload,
                headers=headers,
                cookies=cookies,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                bench_id = data["id"]
                if bench_id:
                    await show_summary(message=message, data=data)
                    await message.answer_location(
                        data["latitude"], data["longitude"], reply_markup=kb.main
                    )
                return bench_id
    except aiohttp.ClientResponseError as e:
        if e.status in [401, 404]:
            await message.answer(
                "❌<b>У вас нет доступа к добавлению лавочек!</b>", reply_markup=kb.main
            )
        else:
            await message.answer(
                "<b>Произошла ошибка при добавлении лавочки!</b>", reply_markup=kb.main
            )
    return None


async def upload_bench_photo(message: Message, bench_id: str, photo_file: str) -> None:
    username = message.from_user.username
    token = await get_token(username)

    cookies = {
        "token": token,
    }

    try:
        with open(photo_file, "rb") as file:
            form_data = aiohttp.FormData()
            form_data.add_field(
                "file", file, filename="photo.jpg", content_type="image/jpeg"
            )

            async with aiohttp.ClientSession(cookies=cookies) as session:
                async with session.post(
                    f"{API_URL}/upload_bench_photo/{bench_id}", data=form_data
                ) as response:
                    response.raise_for_status()
                    await message.answer(
                        "📸 Фото успешно загружено!", reply_markup=kb.main
                    )

    except aiohttp.ClientResponseError as e:
        if e.status in [401, 404]:
            await message.answer(
                "❌<b>У вас нет доступа к загрузке фото!</b>", reply_markup=kb.main
            )
        else:
            await message.answer(
                "<b>Произошла ошибка при загрузке фото!</b>", reply_markup=kb.main
            )


async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    name = data["name"]
    description = data["description"]
    count = data["count"]
    latitude = data["latitude"]
    longitude = data["longitude"]
    photo_url = data["photo_url"]

    text = (
        f'✅Вы создали лавочку🪑: "{name}" (<b>x{count}</b>)\n <i>{description}</i>'
        f"\n Координаты: <code>{latitude}, {longitude}</code>\n"
        f'<span class="tg-spoiler">Используйте "/delete" или "/delete <i>Имя лавочки</i>" для удаления</span>'
    )

    if photo_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as response:
                    if response.status == 200:
                        await bot.send_photo(
                            chat_id=message.chat.id,
                            photo=photo_url,
                            caption=text,
                            reply_markup=kb.del_or_edit_bench,
                        )
                    else:
                        await message.answer(
                            text=text, reply_markup=kb.del_or_edit_bench
                        )
        except Exception as e:
            print(f"Error downloading photo: {e}")
            await message.answer(text=text, reply_markup=kb.del_or_edit_bench)
    else:
        await message.answer(text=text, reply_markup=kb.del_or_edit_bench)
