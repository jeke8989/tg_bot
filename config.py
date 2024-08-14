from dotenv import load_dotenv
from aiogram import Bot
import os

load_dotenv('.env')
token = os.getenv("TOKEN_API")
bot = Bot(token)
