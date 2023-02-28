import datetime
import pandas as pd

from io import BytesIO


weekdays = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье',
}


def get_date_tuple(date: datetime.datetime, offset: int = 0, utc: bool = True) -> tuple:
    date = date.astimezone(datetime.timezone(datetime.timedelta(hours=10))) if utc else date
    date += datetime.timedelta(hours=offset)
    return date.date(), weekdays[date.isoweekday()]


def parse_xlsx(file: BytesIO) -> list:
    navigation = (range(6, 20), range(12), range(5, 16), range(18, 32))
    parsed_rows = []

    df = pd.read_excel(file, 'Звонки')
    date = df.loc[0, 'Урок']
    call_schedule = {}

    for lesson_index in navigation[0]:
        lesson = f'{df.loc[lesson_index, "Смена"]}{df.loc[lesson_index, "Урок"]}'
        lesson_start = df.loc[lesson_index, 'Время начала']
        lesson_end = df.loc[lesson_index, 'Время конца']
        if isinstance(lesson_start, datetime.time):
            call_schedule[lesson] = [lesson_start, lesson_end]

    df = pd.read_excel(file, 'Расписание')
    for class_name_index in (4, 17):
        lesson_indexes = navigation[2] if class_name_index == 4 else navigation[3]

        for class_index in navigation[1]:
            class_name = df.loc[class_name_index, class_index]

            if isinstance(class_name, str):
                for lesson_index in lesson_indexes:
                    lesson = f'{df.loc[lesson_index, "Смена"]}{df.loc[lesson_index, "Урок"]}'
                    lesson_name = df.loc[lesson_index, class_index]
                    if not isinstance(lesson_name, str):
                        continue

                    lesson_start = call_schedule[lesson][0]
                    lesson_end = call_schedule[lesson][1]

                    classroom = None
                    classroom_check = lesson_name.split()

                    if classroom_check[-1][0].isdigit():
                        lesson_name = ''.join(classroom_check[:-1])
                        classroom = classroom_check[-1]

                    parsed_rows.append(
                        dict(zip(['date', 'class', 'lesson', 'lesson_start', 'lesson_end', 'lesson_name', 'classroom'],
                                 [date.date(), class_name, lesson,
                                  lesson_start.strftime('%H:%M'),
                                  lesson_end.strftime('%H:%M'),
                                  lesson_name, classroom])))

    return parsed_rows


def format_schedule(schedule: list | None) -> None | str:
    if not schedule:
        return None

    text = f'# |      Время      | Урок       \n{"-"*48}\n'
    for lesson in schedule:
        text += '{:<3}| {:<10} | {:<}, {:<}\n'.format(
            lesson["lesson"][1],
            f'{lesson["lesson_start"]}-{lesson["lesson_end"]}',
            lesson["lesson_name"],
            lesson["classroom"] if lesson["classroom"] else "-",
        )
    return text
