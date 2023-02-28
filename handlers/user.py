from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import sql_module
from keyboards.reply import main_kb
from keyboards.inline import settings_keyboard, classes_kb, schedules_date, info_kb
from misc.tools import get_date_tuple, format_schedule

router = Router()


@router.message(Text(text='Отмена'))
async def command_cancel_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.clear()

    await message.answer('Отменено.', reply_markup=main_kb())


@router.message(Command(commands=['start']))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.clear()

    if await sql_module.get_user_info(message.from_user.id):
        await message.answer(f'Приветствую, {message.from_user.full_name} 👋\n',
                             reply_markup=main_kb())

    else:
        await message.answer(f'Приветствую, {message.from_user.full_name} 👋\n')
        await message.answer('Кажется, вы здесь впервые. Выберите класс:',
                             reply_markup=classes_kb())


@router.message(Command(commands=['id']))
async def command_id_handler(message: Message) -> None:
    await message.delete()
    await message.answer(f'🪪 ID: {message.from_user.id}\n',
                         reply_markup=main_kb())


@router.message(Text(text='Информация'))
async def info_handler(message: Message) -> None:
    await message.answer('Телеграм-бот МБОУ СОШ №72', reply_markup=info_kb())


@router.message(Text(text='Получить расписание'))
async def schedule_handler(message: Message) -> None:
    await message.reply('На какой день?', reply_markup=schedules_date())


@router.callback_query(Text(startswith='get_schedule'))
async def send_schedule(callback: CallbackQuery) -> None:
    await callback.answer()

    user_info = await sql_module.get_user_info(callback.from_user.id)
    if user_info:

        data = callback.data.split(':')[-1]

        date = get_date_tuple(callback.message.date, 0 if data == '0' else 24)
        schedule = await sql_module.get_schedule(date[0], class_=user_info['class'])
        schedule = format_schedule(schedule)

        if schedule:
            text = f'🗓 Расписание найдено!\n' \
                   f'📆 {date[0].strftime("%d.%m.%Y")}, {date[1]}, {user_info["class"]}'
            await callback.message.answer(text)
            await callback.message.answer(schedule, reply_markup=main_kb())
        else:
            await callback.message.answer(f'🗓 Расписание на {date[0].strftime("%d.%m.%Y")} не найдено!',
                                          reply_markup=main_kb())
    else:
        await callback.message.answer('Сначала укажите класс - /start')


@router.message(Text(text='Настройки'))
async def settings_handler(message: Message) -> None:
    user_info = await sql_module.get_user_info(message.from_user.id)
    text = f'👤 Имя: {message.from_user.full_name}\n' \
           f'👥 Класс: {user_info["class"]}\n' \
           f'📬 Рассылка: {"вкл" if user_info["mailing"] else "выкл"}\n'

    await message.answer(text=text, reply_markup=settings_keyboard())


@router.callback_query(Text(startswith='class_changing'))
async def start_class_changing(callback: CallbackQuery) -> None:
    data = callback.data.split(':')
    await callback.answer()

    if not data[-1]:
        await callback.message.answer('Выберите класс.', reply_markup=classes_kb())
    elif data[-2] != 'letter':
        await callback.message.answer('Выберите букву.', reply_markup=classes_kb(data[-1]))
    else:
        if await sql_module.get_user_info(callback.from_user.id):
            func = sql_module.update_user
        else:
            func = sql_module.add_user

        await func(callback.from_user.id, class_=data[-1])
        await callback.message.answer('Готово!', reply_markup=main_kb())


@router.callback_query(Text(text="change_mailing"))
async def change_mailing_handler(callback: CallbackQuery):
    await sql_module.update_user(callback.from_user.id, mailing=True)
    await callback.message.answer('Готово!', reply_markup=main_kb())
    await callback.answer()
