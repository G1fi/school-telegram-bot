from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text='Получить расписание')],
        [KeyboardButton(text='Информация'), KeyboardButton(text='Настройки')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return make_row_keyboard(['Отмена'])
