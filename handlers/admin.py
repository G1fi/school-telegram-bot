import datetime
import logging

from io import BytesIO

import asyncio
from aiogram import Bot, Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from database import sql_module
from keyboards.inline import admin_kb, make_row_keyboard
from keyboards.reply import cancel_kb, main_kb
from misc.config_reader import config
from misc.tools import parse_xlsx, get_date_tuple

router = Router()
router.message.filter(F.from_user.id.in_(config.admins_list))


class States(StatesGroup):
    get_xlsx = State()
    mailing = State()


@router.message(Command(commands=['admin']))
async def command_admin_handler(message: Message) -> None:
    logging.info(f'Login to the admin panel! '
                 f'{message.from_user.full_name} ({message.from_user.id})')

    today = datetime.datetime.today()
    old_week = get_date_tuple(today, offset=-168)[0]
    new_week = get_date_tuple(today, offset=168)[0]

    await message.answer(f'Добро пожаловать в админ-панель, '
                         f'{message.from_user.full_name}!\n'
                         f'Статистика запросов за неделю:\n'
                         f'{await sql_module.get_requests_statistic(old_week, new_week)}',
                         reply_markup=admin_kb())


@router.message(Command(commands=['doc_id']))
async def command_get_id_handler(message: Message) -> None:
    if message.document:
        await message.answer(message.document.file_id)


@router.callback_query(Text(text="create_mailing"))
async def mailing_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(States.mailing)
    await callback.message.answer('Напишите сообщение, которое нужно разослать пользователям.',
                                  reply_markup=cancel_kb())


@router.message(States.mailing)
async def confirm_mailing(message: Message, state: FSMContext) -> None:
    confirm_kb = make_row_keyboard([['Подтвердить', 'confirm_mailing']])
    users = await sql_module.get_users_with_mailing()

    await state.set_data({'message': message, 'users': users})

    await message.send_copy(message.from_user.id)
    await message.answer(f'Сообщение выше будет отправлено {len(users)} пользователям!\n'
                         f'Нажмите "Отмена" на клавиатуре для выхода.',
                         reply_markup=confirm_kb)


@router.callback_query(Text(text="confirm_mailing"))
async def start_mailing(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Рассылка начинается')

    data = await state.get_data()
    counter = 0

    try:
        for user in data['users']:
            try:
                await data['message'].send_copy(user[0])
                counter += 1
            except BaseException as e:
                logging.info(f'Failed to send message to user {user.id}: {e}')
            finally:
                await asyncio.sleep(3)

    except KeyError as e:
        logging.info(f'Failed to create mailing: {e}')

    await callback.message.answer(f'Рассылка завершена, {counter} пользователей получили сообщение!',
                                  reply_markup=main_kb())
    await state.clear()


@router.callback_query(Text(text="download_templates"))
async def download_templates_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    for template in config.templates_list:
        await callback.message.answer_document(template)


@router.callback_query(Text(text="upload_timetable"))
async def upload_timetable_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(States.get_xlsx)
    await callback.message.answer('Отправьте exel-документ с расписанием.', reply_markup=cancel_kb())


@router.callback_query(Text(text="clear_timetable"))
async def clear_timetable_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    result = await sql_module.clear_old_schedule_entries(callback.message.date.date())
    await callback.message.answer(f'Успешно очищено {result} записей!', reply_markup=main_kb())


@router.message(States.get_xlsx)
async def get_xlsx_handler(message: Message, bot: Bot) -> None:
    if message.document:
        try:
            file_content = BytesIO()
            await bot.download(
                message.document,
                destination=file_content
            )

            result = await sql_module.add_schedule(parse_xlsx(file_content))
            await message.answer(f'Расписание успешно загружено:\n'
                                 f'{result[0]} уроков добавлено\n'
                                 f'{result[1]} уроков обновлено\n',
                                 reply_markup=ReplyKeyboardRemove())

            await command_admin_handler(message)

        except ValueError as e:
            await message.answer(f'Ошибка при загрузке расписания:\n{e}\n'
                                 f'Скорее всего вы отправили неверный файл.\n')
            await message.answer('Попробуйте еще раз или обратитесь к администратору', reply_markup=cancel_kb())

        except Exception as e:
            await message.answer(f'Неизвестная ошибка при загрузке расписания:\n{e}')
            await message.answer('Попробуйте еще раз или обратитесь к администратору', reply_markup=cancel_kb())

    else:
        await message.answer('Вы не отправили документ!', reply_markup=cancel_kb())
