import html
from typing import Dict, Any
import aiohttp
from config import API_URL

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards.keyboard as kb
from app.utils.states import GeoState, BenchForm, BenchDelete


router = Router()


'''
Получение токена доступа
'''


async def get_token(username: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{API_URL}/auth/tg/login?telegram_username={username}') as response:
            if response.status == 200:
                data = await response.json()
                if 'token' in data:
                    return data['token']
            return 'token is none'


'''
Отмена
'''


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

    await state.clear()

'''
Создать лавочку
'''


@router.message(F.text == '➕Создать лавочку')
async def fill_bench(message: Message, state: FSMContext) -> None:
    await state.set_state(BenchForm.name)
    await message.answer('Введите название', reply_markup=kb.cancel)


@router.message(BenchForm.name)
async def bench_name(message: Message, state: FSMContext) -> None:
    if len(message.text) <= 50:
        esc_name = html.escape(message.text)
        await state.update_data(name=esc_name)
        await state.set_state(BenchForm.description)
        await message.answer('Опишите лавочку')
    else:
        await message.answer('❌<b>Максимальная длина названия — 50 символов!</b>')


@router.message(BenchForm.description)
async def bench_description(message: Message, state: FSMContext) -> None:
    if len(message.text) <= 200:
        esc_description = html.escape(message.text)
        await state.update_data(description=esc_description)
        await state.set_state(BenchForm.count)
        await message.answer('Количество?')
    else:
        await message.answer('❌<b>Максимальная длина описания — 200 символов!</b>')


@router.message(BenchForm.count)
async def bench_count(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data(count=message.text)
        await state.set_state(BenchForm.latitude)
        await message.answer('Отправьте вашу геолокацию', reply_markup=kb.geo)
    else:
        await message.answer('❌<b>Введите число!</b>')


@router.message(BenchForm.latitude)
async def bench_latitude(message: Message, state: FSMContext) -> None:
    if message.location:
        await state.update_data(latitude=message.location.latitude)
        await state.set_state(BenchForm.longitude)
        await state.update_data(longitude=message.location.longitude)
        data = await state.get_data()
        await state.clear()

        await create_post_request(message=message, data=data)

    else:
        await message.answer('❌<b>Отправьте геолокацию!</b>', reply_markup=kb.geo)


async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    name = data['name']
    description = data['description']
    count = data['count']
    latitude = data['latitude']
    longitude = data['longitude']
    text = (f"✅Вы создали лавочку🪑: \"{name}\" (<b>x{count}</b>)\n <i>{description}</i>"
            f"\n Координаты: <code>{latitude}, {longitude}</code>\n"
            f"<span class=\"tg-spoiler\">Используйте \"/delete\" или \"/delete <i>Имя лавочки</i>\" для удаления</span>")

    await message.answer(text=text, reply_markup=kb.bench_delete)


async def create_post_request(message: Message, data: Dict[str, Any]) -> None:
    payload = {
        'name': data['name'],
        'description': data['description'],
        'count': data['count'],
        'latitude': data['latitude'],
        'longitude': data['longitude']
    }

    headers = {
        'Content-Type': 'application/json',
    }

    username = message.from_user.username
    token = await get_token(username)  # Получаем токен асинхронно

    cookies = {
        "token": token,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{API_URL}/bench/create', json=payload, headers=headers, cookies=cookies) as response:
                response.raise_for_status()
                await show_summary(message=message, data=data)
                await message.answer_location(data['latitude'], data['longitude'], reply_markup=kb.main)
    except aiohttp.ClientResponseError as e:
        if e.status in [401, 404]:
            await message.answer('❌<b>У вас нет доступа к добавлению лавочек!</b>', reply_markup=kb.main)
        else:
            await message.answer('<b>Произошла ошибка при добавлении лавочки!</b>', reply_markup=kb.main)


'''
Найти лавочку
'''


@router.message(F.text == '🔍Найти лавочку')
async def find_nearest(message: Message, state: FSMContext) -> None:
    await state.set_state(GeoState.waiting_for_location)
    await message.answer('Отправьте геолокацию', reply_markup=kb.geo)


@router.message(GeoState.waiting_for_location)
async def send_location(message: Message, state: FSMContext) -> None:
    if message.location:
        await state.set_state(GeoState.waiting_for_location)
        lat = message.location.latitude
        long = message.location.longitude
        await message.answer(f'Вы отправили геолокацию с координатами: <code>{lat}</code>, <code>{long}</code>')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_URL}/nearest_bench/?latitude={lat}&longitude={long}') as response:
                data = await response.json()
                rs_lat = data['latitude']
                rs_long = data['longitude']
                await message.answer(f"🪑Ближайшая лавочка находится по координатам: <code>{rs_lat}</code>, "
                                     f"<code>{rs_long}</code>",
                                     reply_markup=kb.main)
                await message.reply_location(rs_lat, rs_long)
                await state.clear()

    else:
        await message.answer('❌<b>Отправьте геолокацию</b>', reply_markup=kb.geo)


'''
Изменить лавочку
'''


'''
Удалить лавочку
'''


@router.message(Command('delete'))
async def delete_bench_command(message: Message, state: FSMContext):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 1:
        await message.answer('Введите имя лавочки, которую нужно удалить:')
        await state.set_state(BenchDelete.name)
        return
    elif len(command_parts) == 2:
        name = command_parts[1]
        await delete_bench_by_name(name, message, state)
    else:
        await message.answer('❌ Неправильный формат команды. Используйте: /delete {name}')
        return


async def delete_bench_by_name(name: str, message: Message, state: FSMContext):
    headers = {'Content-Type': 'application/json'}
    username = message.from_user.username
    token = await get_token(username)
    cookies = {"token": token}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{API_URL}/bench/delete', params={'bench_name': name}, headers=headers,
                                      cookies=cookies) as response:
                response.raise_for_status()
                data = await response.json()

                if ("status" in data and data["status"] == "error"
                        and data["message"] == "Bench not found or you are not the creator"):
                    await message.answer('❌<b>Вы не можете удалить эту лавочку, так как не являетесь её создателем</b>',
                                         reply_markup=kb.main)
                else:
                    await message.answer(f'<b>Лавочка "{name}" удалена</b>')
    except aiohttp.ClientResponseError:
        await message.answer('<b>Произошла ошибка при удалении лавочки!</b>', reply_markup=kb.main)

    await state.clear()


@router.message(BenchDelete.name)
async def delete_bench(message: Message, state: FSMContext):
    name = message.text
    await delete_bench_by_name(name, message, state)
