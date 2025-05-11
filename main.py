import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.api)
list_operation = []

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton('Мои записи📅'),
        types.KeyboardButton('Запись на приём👨‍⚕️'),
        types.KeyboardButton('Мои бонусы🎁'),
        types.KeyboardButton('Отмена/перенос❌'),
        types.KeyboardButton('Услуги и цены💰'),
        types.KeyboardButton('Отзывы⭐️'),
        types.KeyboardButton('Чат с клиникой💬'),
        types.KeyboardButton('История📝')
    ]
    markup.add(buttons[0], buttons[1])
    markup.add(buttons[2], buttons[3])
    markup.add(buttons[4], buttons[5])
    markup.add(buttons[6], buttons[7])

    inline_markup = types.InlineKeyboardMarkup()
    inline_btn = types.InlineKeyboardButton('Записаться на бесплатную консультацию', callback_data='free_consultation')
    inline_markup.add(inline_btn)


    bot.send_message(message.chat.id, text="<b>🌟 Добро пожаловать в профиль Дантист Бота!</b> 🌟\n"
        "<i>Мы рады видеть вас здесь! \n</i>", reply_markup=markup, parse_mode= 'HTML')
    bot.send_message(message.chat.id, "С помощью этого бота вы можете записаться в клинику и получить всю необходимую информацию о наших услугах.", reply_markup=inline_markup)
    #bot.send_message(message.chat.id,' ', reply_markup=inline_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'free_consultation')
def callback_inline(call):
    bot.send_message(call.message.chat.id, "Отлично! Вы записаны на бесплатную консультацию.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Запись на приём👨‍⚕️':
        service(message)
    elif message.text == 'Отмена/перенос❌':
        cancel_appoint(message)
    elif message.text == 'Услуги и цены💰':
        show_prices(message)
    elif message.text == 'Чат с клиникой💬':
        bot.send_message(message.chat.id, "Напишите ваш вопрос, администратор ответит вам в ближайшее время")
    elif message.text == 'Мои записи📅':
        show_visit_history(message)
    elif message.text == 'Отзывы⭐️':
        show_reviews(message)
    elif message.text == 'Да':
        bot.send_message(message.chat.id, 'Запись успешно отменена.')
        start_message(message)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Запись не отменена. Вы можете продолжить пользоваться ботом.')
        start_message(message)
    elif message.text == 'Отмена':
        start_message(message)
    elif message.text == 'Мои бонусы🎁':
        bot.send_message(message.chat.id,  "1 бонус - 1 рубль\n"
                                                "1000 бонусов при регистрации\n"
                                                "500 бонусов за друга\n"
                                                "500 бонусов за 1(платное) посещение\n")
        bot.send_message(message.chat.id, 'Вы получили 500 бонусов за регистрацию')
    elif message.text == 'История📝':
        bot.send_message(message.chat.id, 'Ваша текущая история посещений:')
    else:
        callback_appoint(message)

def service(message):
    inline_markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton('Протезирование', callback_data='prosthetics'),
        types.InlineKeyboardButton('Чистка', callback_data='cleaning'),
        types.InlineKeyboardButton('Ортодонтия', callback_data='orthodontics'),
        types.InlineKeyboardButton('Консультация', callback_data='consultation'),
        types.InlineKeyboardButton('Имплантация', callback_data='implantation'),
        types.InlineKeyboardButton('Специалисты', callback_data='specialists')
    ]
    inline_markup.add(buttons[3])
    inline_markup.add(buttons[1])
    inline_markup.add(buttons[2])
    inline_markup.add(buttons[0])
    inline_markup.add(buttons[4])
    inline_markup.add(buttons[5])

    bot.send_message(message.chat.id, 'Выберите услугу:', reply_markup=inline_markup)

@bot.callback_query_handler(func=lambda call: call.data in ['prosthetics', 'cleaning', 'orthodontics', 'consultation', 'implantation', 'specialists'])
def callback_appoint(call):
    if call.data == 'specialists':
        bot.send_message(call.message.chat.id, 'Информация о специалистах')
        bot.send_message(call.message.chat.id, 'https://dental.clinic23.ru/nashi-spetsialisty')
    else:
        if call.data == 'consultation':
            bot.send_message(call.message.chat.id, 'Первое посещение бесплатно!')
        bot.send_message(call.message.chat.id, "Пожалуйста, введите желаемую дату приема")
def process_time(message, date):
    time = message.text
    confirm_appoint(message, date, time)

def confirm_appoint(message, date, time):
    global list_operation
    appointment = f'{date} в {time}'
    bot.send_message(message.chat.id, f'Вы записаны на приём {appointment}.')
    bot.send_message(message.chat.id, 'г. Краснодар, ул. Кубанская Набережная, д. 37/1')
    bot.send_message(message.chat.id, 'https://yandex.ru/maps/-/CHFlqLMz')
    list_operation.append(appointment)

def create_time_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    times = ['10:00', '11:00', '12:00', '14:00', '15:00', 'Отмена']
    markup.add(*times)
    return markup

def cancel_appoint(message):
    markup = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton('Да', callback_data = 'Yes')
    b2 = types.InlineKeyboardButton('Нет', callback_data='No')
    markup.add(b1, b2)
    bot.send_message(message.chat.id, 'Вы уверены что хотите отменить запись?', reply_markup=markup)

def process_cancel_step(message):
    if message.text == 'Да':
        global list_operation
        if list_operation:
            list_operation.pop()
            bot.send_message(message.chat.id, 'Последняя запись успешно отменена.')
        else:
            bot.send_message(message.chat.id, 'У вас нет активных записей для отмены.')
        start_message(message)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Запись не отменена. Вы можете продолжить пользоваться ботом.')
        start_message(message)

def show_visit_history(message):
    if list_operation:
        bot.send_message(message.chat.id, f'Записи: {", ".join(list_operation)}')
    else:
        bot.send_message(message.chat.id, 'На данный момент у вас нет записей')


def show_reviews(message):
    bot.send_message(message.chat.id,f"Посмотреть отзывы можно по следующей ссылке: https://yandex.ru/maps/org/klinika_yekaterininskaya_tsentr_stomatologii/224189762833/reviews/?ll=38.959189%2C45.025062&z=16")


@bot.message_handler(func=lambda message: message.text == 'Услуги и цены💰')
def show_prices(message):
    prices_info = """
    🦷ОРТОДОНТИЯ
    - Первичный прием (осмотр, консультация): Бесплатно
    - Повторный прием (осмотр, консультация): 1500 ₽

    🦷ПРОТЕЗИРОВАНИЕ
    - Снятие оттиска с одной челюсти (закрытой ложкой): 2500 ₽
    - Протезирование зуба с использованием имплантата (абатмент Emax): 18000 ₽
    - Протезирование зуба с использованием имплантата (винтовая фиксация): 37000 ₽
    - Протезирование зуба с использованием имплантата (временная коронка на временном абатменте) - 20000 ₽
    - Протезирование зуба с использованием имплантата (Коронка на титановом основании с цементной фиксацией) - 37000 ₽

    🦷ИМПЛАНТАЦИЯ
    - Прием (осмотр, консультация) врача-стоматолога-хирурга: Бесплатно
    - Внутрикостная дентальная имплантация (Paltop (США)): 52000

    🦷КОНСУЛЬТАЦИЯ
    - Прием (осмотр, консультация) врача-стоматолога: Бесплатно

    🦷ЧИСТКА
    - Обучение гигиене полости рта и зубов, подбор средств и предметов гигиены: 600 ₽

    ✨Мы готовы помочь вам с уходом за зубами и восстановлением улыбки.
    """

    bot.send_message(message.chat.id, prices_info)

if __name__ == '__main__':
    bot.infinity_polling()