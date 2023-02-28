import aiosqlite
import datetime

from misc.config_reader import config


async def create_tables() -> None:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    user_id INTEGER PRIMARY KEY,
                                    class CHAR(3),
                                    mailing BOOLEAN DEFAULT TRUE
                                )''')

            await cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
                                    date DATE,
                                    class CHAR(3), 
                                    lesson CHAR(2), 
                                    lesson_start TIME,
                                    lesson_end TIME,
                                    lesson_name CHAR(10), 
                                    classroom CHAR(3),
                                    PRIMARY KEY (date, class, lesson)
                                )''')

            await cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                                    date DATE,
                                    request_type CHAR(20),
                                    details TEXT
                                )''')

        await db.commit()


async def get_user_info(user_id: int) -> dict | None:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute('SELECT class, mailing '
                                 'FROM users '
                                 'WHERE user_id=?',
                                 (user_id,))
            result = await cursor.fetchone()

    return {'class': result[0], 'mailing': result[1]} if result else None


async def add_user(user_id: int, class_: str) -> None:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute('INSERT INTO users (user_id, class) '
                                 'VALUES (?, ?)',
                                 (user_id, class_))
        await db.commit()

    await add_request('add_user', f'user_id: {user_id}')


async def update_user(user_id: int, class_: str = None, mailing: bool = False) -> None:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            user_info = await get_user_info(user_id)

            if class_:
                user_info['class'] = class_
            if mailing:
                user_info['mailing'] = not (user_info['mailing'])

            await cursor.execute('UPDATE users '
                                 'SET class = ?, mailing = ? '
                                 'WHERE user_id = ?',
                                 (user_info['class'], user_info['mailing'], user_id))

        await db.commit()


async def add_lesson(lesson: dict) -> bool:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            if await get_schedule(lesson['date'], lesson['class'], lesson['lesson']):
                await cursor.execute('UPDATE schedules '
                                     'SET lesson_start = ?, lesson_end = ?, lesson_name = ?, classroom = ? '
                                     'WHERE date = ? AND class = ? AND lesson = ?',
                                     (lesson['lesson_start'], lesson['lesson_end'], lesson['lesson_name'],
                                      lesson['classroom'], lesson['date'], lesson['class'], lesson['lesson']))
                updated = True

            else:
                await cursor.execute('INSERT INTO schedules '
                                     '(date, class, lesson, lesson_start, lesson_end, lesson_name, classroom) '
                                     'VALUES (?, ?, ?, ?, ?, ?, ?)',
                                     (lesson['date'], lesson['class'], lesson['lesson'], lesson['lesson_start'],
                                      lesson['lesson_end'], lesson['lesson_name'], lesson['classroom']))
                updated = False

        await db.commit()

    return updated


async def add_schedule(lessons: list) -> list[int]:
    result = [0, 0]
    for lesson in lessons:
        if await add_lesson(lesson):
            result[1] += 1
        else:
            result[0] += 1

    await add_request('add_schedule',
                      f'{result[0]} lesson(s) added, '
                      f'{result[1]} lesson(s) updated')

    return result


async def get_schedule(date: datetime.date,
                       class_: str = None,
                       lesson: str = None,
                       lesson_name: str = None,
                       classroom: str = None) -> list | None:
    conditions = ['1']
    condition_params = [date]

    if class_:
        conditions.append('class=?')
        condition_params.append(class_)

    if lesson:
        conditions.append('lesson=?')
        condition_params.append(lesson)

    if lesson_name:
        conditions.append('lesson_name=?')
        condition_params.append(lesson_name)

    if classroom:
        conditions.append('classroom=?')
        condition_params.append(classroom)

    await add_request('get_schedule', f'condition_params: {condition_params}')

    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute(f'SELECT date, class, lesson, lesson_start, lesson_end, lesson_name, classroom '
                                 f'FROM schedules '
                                 f'WHERE date=? AND {" AND ".join(conditions)} '
                                 f'ORDER BY lesson, class',
                                 condition_params)
            results = await cursor.fetchall()

    return [
        dict(zip(['date', 'class', 'lesson', 'lesson_start', 'lesson_end', 'lesson_name', 'classroom'], result))
        for result in results
    ] if results else None


async def clear_old_schedule_entries(date: datetime.date) -> int:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            deleted_rows = await cursor.execute(
                'DELETE FROM schedules WHERE date < ?',
                (date,)
            )
            await db.commit()

    return deleted_rows.rowcount


async def get_users(with_mailing: bool = False):
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute(f'SELECT * FROM users {"WHERE mailing = 1" if with_mailing else ""}')
            users = await cursor.fetchall()

    return users


async def add_request(request_type: str, details: str) -> None:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute('INSERT INTO requests (date, request_type, details) '
                                 'VALUES (?, ?, ?)',
                                 (datetime.date.today(), request_type, details))

        await db.commit()


async def get_requests_statistic(start_date: datetime.date, end_date: datetime.date) -> dict:
    async with aiosqlite.connect(config.database_path) as db:
        async with await db.cursor() as cursor:
            await cursor.execute('SELECT request_type, COUNT(*) '
                                 'FROM requests '
                                 'WHERE date BETWEEN ? AND ? '
                                 'GROUP BY request_type',
                                 (start_date, end_date))
            results = await cursor.fetchall()

    return dict(results) if results else {}


async def main() -> None:
    await create_tables()
    for i in range(8):
        await add_request('add_schedule', f'condition_params: {5 + 5}')
    for i in range(654):
        await add_request('get_schedule', f'condition_params: {5+5}')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
