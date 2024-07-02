import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart, Command
from confreader import config
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile, Message
import sqlite3
from datetime import datetime, date

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
        [types.KeyboardButton(text="/get_photo")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f"Hello, {message.from_user.full_name}", reply_markup=keyboard)


@dp.message(Command("help"))
async def get_help(message: types.Message):
    await message.answer(f"Список комонд...")

@dp.message(F.photo)
async def f_text(message: types.Message):
    await message.answer(message.photo[-1].file_id)
    value_data = datetime.now().date()
    query = """INSERT INTO photo(photo_id, date) VALUES(?,?);"""
    value = (message.photo[-1].file_id, value_data)
    cur.execute(query, value)
    conn.commit()


@dp.message(Command("get_photo"))
async def get_photo(message: types.Message):
    album_builder = MediaGroupBuilder(caption="Подборка дня")
    value_data = datetime.now().date()
    query = f"""SELECT photo_id FROM photo WHERE date='{value_data}'"""
    cur.execute(query)
    fetchdata = cur.fetchall()
    print(fetchdata)
    for id_photo in fetchdata:
        album_builder.add_photo(media=id_photo[0])
    await message.answer_media_group(media=album_builder.build())


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())