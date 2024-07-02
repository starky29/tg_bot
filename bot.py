import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart, Command
from confreader import config
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile, Message
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler


conn = sqlite3.connect('photo.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS photo(
            photo_id TEXT,
            date TIMESTAMP);
            """)
conn.commit()


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="/start")],
        [types.KeyboardButton(text="/help")],
        # [types.KeyboardButton(text="/get_photo")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f"Hello, {message.from_user.full_name}", reply_markup=keyboard)


@dp.message(Command("help"))
async def get_help(message: types.Message):
    await message.answer("Данный бот автоматически отправляет подборки из случайных 10 фотографий"
                         " за предыдущий день, неделю и месяц. Главное что бы это были фотографии."
                         "Для того что бы он их отправлял нужно ему в личку кидать фотографии, тогда он их запишит за данный день")

@dp.message(F.photo)
async def f_text(message: types.Message):
    await message.answer(message.photo[-1].file_id)
    value_data = datetime.now().date()
    query = """INSERT INTO photo(photo_id, date) VALUES(?,?);"""
    value = (message.photo[-1].file_id, value_data)
    cur.execute(query, value)
    conn.commit()


# @dp.message(Command("get_photo"))
# async def get_photo(message: types.Message):
#
#     album_builder = MediaGroupBuilder(caption="Подборка дня")
#     value_data = datetime.now().date()
#     query = f"""SELECT photo_id FROM photo WHERE date='{value_data}'"""
#     cur.execute(query)
#     fetchdata = cur.fetchall()
#     if len(fetchdata) >= 10:
#         fetchdata = random.sample(fetchdata, 10)
#     else:
#         fetchdata = random.sample(fetchdata, len(fetchdata)-1)
#     if len(fetchdata) > 0:
#         for id_photo in fetchdata:
#             album_builder.add_photo(media=id_photo[0])
#         await message.answer_media_group(media=album_builder.build())
#     else:
#         await message.answer(f"За сегодня нет фото")


async def scheduled(interval):
    match interval:
        case 'day':
            value = 'за прошедний ДЕНЬ'
            value_data = datetime.now().date() - timedelta(days=1)
            query = f"""SELECT photo_id FROM photo WHERE date='{value_data}'"""
        case 'weekly':
            value = 'за прошедшую НЕДЕЛЮ'
            value_data_end = datetime.now().date() - timedelta(days=1)
            value_data = datetime.now().date() - timedelta(days=7)
            query = f"""SELECT photo_id FROM photo WHERE date BETWEEN '{value_data}' and '{value_data_end}'"""
        case 'month':
            value = 'за прошедший МЕСЯЦ'
            value_data_end = datetime.now().date() - timedelta(days=1)
            value_data = datetime.now().date() - timedelta(days=30)
            query = f"""SELECT photo_id FROM photo WHERE date BETWEEN '{value_data}' and '{value_data_end}'"""

    album_builder = MediaGroupBuilder(caption=f"Подборка {value}")
    cur.execute(query)
    fetchdata = cur.fetchall()
    if len(fetchdata) >= 10:
        fetchdata = random.sample(fetchdata, 10)
    else:
        fetchdata = random.sample(fetchdata, len(fetchdata))
    if len(fetchdata) > 0:
        for id_photo in fetchdata:
            album_builder.add_photo(media=id_photo[0])
        await bot.send_media_group("693032292", media=album_builder.build())
    else:
        await bot.send_message("693032292","Нет фото")


# Запуск процесса поллинга новых апдейтов
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled, 'cron', hour=12, minute=00, args=('day',))
    scheduler.add_job(scheduled, 'cron', day_of_week='mon', args=('weekly',))
    scheduler.add_job(scheduled, 'cron', day=1, args=('month',))
    scheduler.start()

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())