from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from misc.config_reader import config


def settings_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text='Изменить класс', callback_data='class_changing:')],
        [InlineKeyboardButton(text='Вкл/выкл рассылку', callback_data='change_mailing')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def admin_kb() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text='Загрузить расписание', callback_data='upload_timetable')],
        [InlineKeyboardButton(text='Очистить расписания', callback_data='clear_timetable')],
        [InlineKeyboardButton(text='Скачать шаблоны', callback_data='download_templates')],
        [InlineKeyboardButton(text='Создать рассылку', callback_data='create_mailing')],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def info_kb() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text='Наш телеграм канал', url='t.me/shkoly72hab')],
        [InlineKeyboardButton(text='Наш сайт', url='school-72-khb.ru')],
        [InlineKeyboardButton(text='Госуслуги', url='www.gosuslugi.ru')],
        [InlineKeyboardButton(text='Пушкинская карта', url='пушка.рф')],
        [InlineKeyboardButton(text='РЭШ', url='resh.edu.ru')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def schedules_date() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text='На сегодня', callback_data='get_schedule:0')],
        [InlineKeyboardButton(text='На завтра', callback_data='get_schedule:1')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def make_row_keyboard(items: list[list]) -> InlineKeyboardMarkup:
    row = [InlineKeyboardButton(text=item[0], callback_data=item[1]) for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def classes_kb(grade: None | str = None) -> InlineKeyboardMarkup:
    items = config.classes[grade] if grade else config.classes.keys()
    callback_data = 'class_changing:letter:' if grade else 'class_changing:'
    row = [InlineKeyboardButton(text=item, callback_data=callback_data + item) for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[row])
