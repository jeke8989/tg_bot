import asyncio
import logging
from aiogram import Dispatcher

from bot.handlers.user_handlers import router
from bot.database.models import async_main
import config


bot = config.bot
dp = Dispatcher()



async def main() -> None:
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
         print('Exit')