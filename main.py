import asyncio
import logging
import sys

from os import getenv

from aiogram import Bot, Dispatcher, html, types, filters
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from Handlers import other_handlers, shopping_list_handlers
from Config_data.config import *
from Database.models import async_main

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.info('Roldex.pro bot started')
    await async_main()

    config: Config = load_config()

    bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp: Dispatcher = Dispatcher()

    dp.include_router(shopping_list_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
