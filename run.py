import asyncio
import logging

from aiogram.enums import ParseMode

from config import TOKEN
from app.handlers import setup_routers

from aiogram import Bot, Dispatcher

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


async def main():
    routers = setup_routers()
    dp.include_router(router=routers)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('EXITED')
