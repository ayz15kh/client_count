from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


async def start_admin(bot, message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Все записи📅"), KeyboardButton(text="Чат💬")],
        [KeyboardButton(text="История📝"), KeyboardButton(text="Поиск")]
    ])
    await bot.send_message(message.chat.id, "Добро пожаловать в админ-панель", reply_markup=keyboard)