import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from routes import *

bot = Bot(config.token)


def get_storage():  # change in future to DB
    return MemoryStorage()


async def main() -> None:
    storage = get_storage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


