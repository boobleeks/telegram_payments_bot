from aiogram import Bot, Dispatcher
from handlers import routers
import asyncio
import logging
import os
from database.db import init_db
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    for router in routers:
        dp.include_router(router)
    
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")