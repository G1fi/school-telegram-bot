import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage


from misc.config_reader import config
from handlers import user, admin, common
from database.sql_module import create_tables


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] | %(levelname)s | %(name)s - %(message)s",
    )

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(common.router)

    @dp.startup()
    async def on_startup():
        await create_tables()

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=[BotCommand(command="start", description="запустить бота")])
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
