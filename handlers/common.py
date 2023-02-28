from aiogram import Router
from aiogram.types import Message

from keyboards.reply import main_kb

router = Router()


@router.message()
async def unknown_handler(message: Message) -> None:
    await message.answer('Я вас не понимаю, воспользуйтесь кнопками\n'
                         'Если их у вас нет, отправьте команду /start',
                         reply_markup=main_kb())
