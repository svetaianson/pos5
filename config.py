from aiogram import Bot,Dispatcher
from os import getenv
from aiogram.fsm.storage.memory import MemoryStorage
from orgHanlder import Organization
from dotenv import load_dotenv
load_dotenv()

TOKEN = getenv("BOT_TOKEN")
DD_TOKEN = getenv("DADATA_TOKEN")
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=MemoryStorage())
org = Organization(DD_TOKEN)