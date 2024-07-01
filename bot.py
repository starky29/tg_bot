import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart, Command
from confreader import config
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile, Message

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
    with open('photo_id.txt', 'a') as f:
        f.write(message.photo[-1].file_id+"\n")


@dp.message(Command("get_photo"))
async def get_photo(message: types.Message):
    with open('photo_id.txt') as f:
        album_builder = MediaGroupBuilder(caption="Общая подпись для будущего альбома")
        for id_photo in f.readlines():


            album_builder.add_photo(media=id_photo.strip())
        # await message.answer_media_group(media=album_builder.build())
        await bot.send_media_group(chat_id="890394784", media=album_builder.build())
        # await bot.send_photo(chat_id="784072988", photo=id_photo.strip())

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())