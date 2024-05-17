from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.keyboards.keyboard as kb


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Буу, {message.from_user.full_name}! Выберите действие', reply_markup=kb.main)
