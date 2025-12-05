from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot

user_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Мои записи📅"), KeyboardButton(text="Запись на приём👨‍⚕️")],
    [KeyboardButton(text="Чат с клиникой💬"), KeyboardButton(text="Отзывы⭐️")],
    [KeyboardButton(text="Услуги и цены💰"), KeyboardButton(text="История📝")]
])


async def start_user(bot: Bot, message: Message):
    inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться на бесплатную консультацию", callback_data="free_consultation")]
    ])
    await bot.send_message(message.chat.id, "<b>🌟 Добро пожаловать!</b>\n<i>Вы можете записаться прямо сейчас</i>",
                           reply_markup=user_menu)
    await bot.send_message(message.chat.id, "Нажмите на кнопку ниже:", reply_markup=inline)