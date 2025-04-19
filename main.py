import telebot
from telebot import types

bot = telebot.TeleBot('7761168261:AAGBby_W9zuqezI49tBne_gNsLxkLzeO86o')
list_operation = []


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Запись на приём👨‍⚕️'),
        types.KeyboardButton('Отменить или перенести❌'),
        types.KeyboardButton('Информацияℹ️ и цены💰'),
        types.KeyboardButton('Чат с клиникой💬'),
        types.KeyboardButton('История посещений📅'),
        types.KeyboardButton('Отзывы⭐️')
    )
    bot.send_message(message.chat.id,text='🌟 Добро пожаловать в профиль Дантист Бота! 🌟 Мы рады видеть вас здесь! 🦷 Что я могу для вас сделать?',reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Запись на приём👨‍⚕️':
        service(message)
    elif message.text in ['10:00', '11:00', '12:00', '14:00', '15:00']:
        confirm_appoint(message)
    elif message.text == 'Отменить или перенести❌':
        cancel_appoint(message)
    elif message.text == 'Информацияℹ️ и цены💰':
        show_prices(message)
    elif message.text == 'Чат с клиникой💬':
        bot.send_message(message.chat.id, "Переходите в чат с клиникой: (https://t.me/mgdmer)")
    elif message.text == 'История посещений📅':
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


def service(message):
    markup = types.InlineKeyboardMarkup()

    services = ['Протезирование', 'Чистка', 'Ортодонтия', 'Консультация', 'Имплантация', 'Специалисты']
    for i in services:
        markup.add(types.InlineKeyboardButton(i, callback_data=i.lower()))

    bot.send_message(message.chat.id, 'Выберите услугу:', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)

def callback_appoint(call):
    if call.data == 'Специалисты':
        bot.send_message(call.message.chat.id, 'easfgegsggesgesges')
        bot.send_photo(call.message.chat.id, 'https://specialistlanguagecourses.com/wp-content/uploads/2021/12/shutterstock_519507367-scaled.jpg', 'wfdwf')
    else:
        if call.data == 'консультация':
            bot.send_message(call.message.chat.id, 'Первое посещение бесплатно!')
        markup = create_time_keyboard()
        bot.send_message(call.message.chat.id, 'Выберите время для записи:', reply_markup=markup)


def create_time_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    times = ['10:00', '11:00', '12:00', '14:00', '15:00', 'Отмена']
    for i in times:
        markup.add(i)
    return markup


def confirm_appoint(message):
    global list_operation
    bot.send_message(message.chat.id, f'Вы записаны на приём в {message.text}.')
    bot.send_message(message.chat.id, 'г. Краснодар, ул. Кубанская Набережная, д. 37/1')
    bot.send_message(message.chat.id, 'https://yandex.ru/maps/-/CHFlqLMz')
    list_operation += str(message.text)

def cancel_appoint(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Да', 'Нет')
    bot.send_message(message.chat.id, 'Вы уверены что хотите отменить запись?', reply_markup=markup )

def show_visit_history(message):
    if len(list_operation) != 0:
        bot.send_message(message.chat.id, f'Записи: {list_operation}')
    else:
        bot.send_message(message.chat.id, 'На данный момент у вас нет записей')

def show_reviews(message):
    bot.send_message(message.chat.id, f"Посмотреть отзывы можно по следующей ссылке: https://yandex.ru/maps/org/klinika_yekaterininskaya_tsentr_stomatologii/224189762833/reviews/?ll=38.959189%2C45.025062&z=16")


@bot.message_handler(func=lambda message: message.text == 'Информация и цены')
def show_prices(message):
    prices_info = (
        "Ортодонтия:\n"
        "Прием (осмотр, консультация) врача-ортодонта первичный - 2000 ₽\n"
        "Прием (осмотр, консультация) врача-ортодонта повторный - 1500 ₽\n"

        "Протезирование:\n"
        "Снятие оттиска с одной челюсти (закрытой ложкой) - 2500 ₽\n"
        "Снятие оттиска с одной челюсти (открытой ложкой) - 3500 ₽\n"
        "Протезирование зуба с использованием имплантата (абатмент Emax) - 18000 ₽\n"
        "Протезирование зуба с использованием имплантата (циркониевый абатмент) - 20000 ₽\n"
        "Протезирование зуба с использованием имплантата (временная коронка на временном абатменте) - 20000 ₽\n"
        "Протезирование зуба с использованием имплантата (винтовая фиксация) - 37000 ₽\n"
        "Протезирование зуба с использованием имплантата (Коронка на титановом основании с цементной фиксацией) - 37000 ₽\n\n"

        "Имплантация:\n"
        "Прием (осмотр, консультация) врача-стоматолога-хирурга первичный - 1500 ₽\n"
        "Внутрикостная дентальная имплантация (Paltop (США)) - 52000 ₽\n\n"

        "Консультация:\n"
        "Прием (осмотр, консультация) врача-стоматолога - 700 ₽\n"
        "Профилактический прием (осмотр, консультация) врача-стоматолога - 1000 ₽\n\n"
        "Чистка:\n"

        "Обучение гигиене полости рта и зубов индивидуальное, подбор средств и предметов гигиены полости рта - 600 ₽\n"
        "Прием (осмотр, консультация) врача-стоматолога повторный - 700 ₽\n"
        "Профилактический прием (осмотр, консультация) врача-стоматолога - 1000 ₽"
    )
    bot.send_message(message.chat.id, prices_info)


if __name__ == '__main__':
    bot.infinity_polling()