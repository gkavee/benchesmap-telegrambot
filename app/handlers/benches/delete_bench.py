import re

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards import keyboard as kb
from app.utils.auth import get_token
from app.utils.states import BenchDelete
from config import API_URL

router = Router()


@router.message(Command("delete"))
async def delete_bench_command(message: Message, state: FSMContext):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 1:
        await message.answer("Введите имя лавочки, которую нужно удалить:")
        await state.set_state(BenchDelete.name)
        return
    elif len(command_parts) == 2:
        name = command_parts[1]
        await delete_bench_by_name(name, message, state)
    else:
        await message.answer(
            "❌ Неправильный формат команды. Используйте: /delete {name}"
        )
        return


async def delete_bench_by_name(name: str, message: Message, state: FSMContext):
    headers = {"Content-Type": "application/json"}
    username = message.from_user.username
    token = await get_token(username)
    cookies = {"token": token}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{API_URL}/delete_bench",
                params={"bench_name": name},
                headers=headers,
                cookies=cookies,
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if (
                    "status" in data
                    and data["status"] == "error"
                    and data["message"] == "Bench not found or you are not the creator"
                ):
                    await message.answer(
                        "❌<b>Вы не можете удалить эту лавочку, так как её не существует "
                        "или вы не являетесь её создателем</b>",
                        reply_markup=kb.main,
                    )
                else:
                    await message.answer(f'<b>Лавочка "{name}" удалена</b>')
    except aiohttp.ClientResponseError:
        await message.answer(
            "<b>Произошла ошибка при удалении лавочки!</b>", reply_markup=kb.main
        )

    await state.clear()


@router.message(BenchDelete.name)
async def delete_bench(message: Message, state: FSMContext):
    name = message.text
    await delete_bench_by_name(name, message, state)


@router.callback_query(lambda c: c.data == "delete_bench")
async def delete_bench_callback(callback: CallbackQuery):
    message_text = callback.message.text
    match = re.search(r'"([^"]+)"', message_text)
    name = match.group(1)

    headers = {"Content-Type": "application/json"}
    username = callback.from_user.username
    token = await get_token(username)
    cookies = {"token": token}

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{API_URL}/delete_bench",
            params={"bench_name": name},
            headers=headers,
            cookies=cookies,
        ) as response:
            if response.status == 200:
                new_message_text = f'✅Лавочка <i>"{name}"</i> успешно удалена'
                if callback.message.text != new_message_text:
                    await callback.message.edit_text(new_message_text)
            else:
                await callback.message.answer("❗Произошла ошибка при удалении лавочки")

    await callback.answer()
