import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TOKEN")
if not bot_token:
    print("Error: no token provided")

storage = MemoryStorage()


bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)
