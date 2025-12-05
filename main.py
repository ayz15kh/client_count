import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from datetime import datetime, timedelta
from typing import Dict, List

import config
from admin_panel import start_admin
from user_panel import start_user, user_menu


# Храним записи по пользователям: user_id -> список записей
user_appointments: Dict[int, List[dict]] = {}
# Промежуточные данные для создания записи (service/date/time)
pending_booking: Dict[int, dict] = {}


user_router = Router()
admin_router = Router()


# ========= Утилиты для клавиатур/форматирования =========


def build_date_keyboard(days: int = 7) -> InlineKeyboardMarkup:
    today = datetime.now().date()
    buttons = []
    for i in range(days):
        day = today + timedelta(days=i)
        label = day.strftime("%d.%m (%a)")
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"date:{day.isoformat()}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_time_keyboard() -> InlineKeyboardMarkup:
    times = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    row = [InlineKeyboardButton(text=t, callback_data=f"time:{t}") for t in times]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def fmt_one(ap: dict) -> str:
    date = ap.get("date")
    time = ap.get("time")
    service = ap.get("service", "услуга")
    return f"{date} {time} — {service}"


def format_appointments(appointments: List[dict]) -> str:
    lines = ["Ваши записи:"]
    for idx, ap in enumerate(appointments, start=1):
        lines.append(f"{idx}. {fmt_one(ap)}")
    return "\n".join(lines)


def build_manage_keyboard(appointments: List[dict]) -> InlineKeyboardMarkup:
    rows = []
    for idx, ap in enumerate(appointments):
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Удалить {fmt_one(ap)}",
                    callback_data=f"del:{idx}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else InlineKeyboardMarkup(inline_keyboard=[])


# ==== Пользовательская часть ====


@user_router.message(CommandStart())
async def cmd_start_user(message: Message, bot: Bot) -> None:
    await start_user(bot, message)


@user_router.callback_query(F.data == "free_consultation")
async def callback_free_consultation(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    pending_booking[user_id] = {"service": "Бесплатная консультация"}
    await bot.send_message(
        call.message.chat.id,
        "Выберите дату для бесплатной консультации:",
        reply_markup=build_date_keyboard(),
    )


@user_router.message(F.text == "Запись на приём👨‍⚕️")
async def handle_appointment(message: Message, bot: Bot) -> None:
    inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Консультация", callback_data="consultation")],
            [InlineKeyboardButton(text="Чистка", callback_data="cleaning")],
            [InlineKeyboardButton(text="Ортодонтия", callback_data="orthodontics")],
            [InlineKeyboardButton(text="Протезирование", callback_data="prosthetics")],
            [InlineKeyboardButton(text="Имплантация", callback_data="implantation")],
            [InlineKeyboardButton(text="Специалисты", callback_data="specialists")],
        ]
    )
    await bot.send_message(message.chat.id, "Выберите услугу:", reply_markup=inline_markup)


@user_router.callback_query(F.data.in_(["prosthetics", "cleaning", "orthodontics", "consultation", "implantation", "specialists"]))
async def callback_appoint(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    if call.data == "specialists":
        await bot.send_message(call.message.chat.id, "Информация о специалистах")
        await bot.send_message(call.message.chat.id, "https://dental.clinic23.ru/nashi-spetsialisty")
    else:
        pending_booking[user_id] = {"service": call.data}
        await bot.send_message(
            call.message.chat.id,
            "Выберите дату:",
            reply_markup=build_date_keyboard(),
        )


@user_router.callback_query(F.data.startswith("date:"))
async def pick_date(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    if user_id not in pending_booking:
        await bot.send_message(call.message.chat.id, "Сначала выберите услугу.")
        return

    date_iso = call.data.split("date:")[1]
    pending_booking[user_id]["date"] = date_iso
    await bot.send_message(
        call.message.chat.id,
        f"Дата: {date_iso}. Теперь выберите время:",
        reply_markup=build_time_keyboard(),
    )


@user_router.callback_query(F.data.startswith("time:"))
async def pick_time(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    data = pending_booking.get(user_id)
    if not data or "date" not in data:
        await bot.send_message(call.message.chat.id, "Сначала выберите дату.")
        return

    time_val = call.data.split("time:")[1]
    data["time"] = time_val

    # Сохраняем запись
    appt = {
        "service": data.get("service", "Услуга"),
        "date": data["date"],
        "time": data["time"],
    }
    user_appointments.setdefault(user_id, []).append(appt)
    pending_booking.pop(user_id, None)

    await bot.send_message(
        call.message.chat.id,
        f"Запись создана: {fmt_one(appt)}",
        reply_markup=user_menu,
    )


@user_router.message(F.text == "Отмена/перенос❌")
async def cancel_appoint(message: Message, bot: Bot) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="cancel_yes"),
                InlineKeyboardButton(text="Нет", callback_data="cancel_no"),
            ]
        ]
    )
    await bot.send_message(message.chat.id, "Вы уверены что хотите отменить последнюю запись?", reply_markup=markup)


@user_router.callback_query(F.data == "cancel_yes")
async def process_cancel_yes(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    appointments = user_appointments.get(user_id, [])
    if appointments:
        appointments.pop()
        await bot.send_message(call.message.chat.id, "Последняя запись успешно отменена.")
    else:
        await bot.send_message(call.message.chat.id, "У вас нет активных записей для отмены.")


@user_router.callback_query(F.data == "cancel_no")
async def process_cancel_no(call: CallbackQuery, bot: Bot) -> None:
    await bot.send_message(call.message.chat.id, "Запись не отменена. Вы можете продолжить пользоваться ботом.")


@user_router.message(F.text == "Мои записи📅")
async def show_visit_history(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    appointments = user_appointments.get(user_id, [])
    if appointments:
        await bot.send_message(
            message.chat.id,
            format_appointments(appointments),
            reply_markup=build_manage_keyboard(appointments),
        )
    else:
        await bot.send_message(message.chat.id, "На данный момент у вас нет записей")


@user_router.message(F.text == "Мои бонусы🎁")
async def show_bonuses(message: Message, bot: Bot) -> None:
    await bot.send_message(
        message.chat.id,
        "1 бонус - 1 рубль\n"
        "1000 бонусов при регистрации\n"
        "500 бонусов за друга\n"
        "500 бонусов за 1 (платное) посещение\n",
    )
    await bot.send_message(message.chat.id, "Вы получили 500 бонусов за регистрацию")


@user_router.message(F.text == "Услуги и цены💰")
async def show_prices(message: Message, bot: Bot) -> None:
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
- Внутрикостная дентальная имплантация (Paltop (США)): 52000 ₽

🦷КОНСУЛЬТАЦИЯ
- Прием (осмотр, консультация) врача-стоматолога: Бесплатно

🦷ЧИСТКА
- Обучение гигиене полости рта и зубов, подбор средств и предметов гигиены: 600 ₽

✨Мы готовы помочь вам с уходом за зубами и восстановлением улыбки.
"""
    await bot.send_message(message.chat.id, prices_info)


@user_router.message(F.text == "Отзывы⭐️")
async def show_reviews(message: Message, bot: Bot) -> None:
    await bot.send_message(
        message.chat.id,
        "Посмотреть отзывы можно по следующей ссылке: "
        "https://yandex.ru/maps/org/klinika_yekaterininskaya_tsentr_stomatologii/224189762833/reviews/"
        "?ll=38.959189%2C45.025062&z=16",
    )


@user_router.message(F.text == "Чат с клиникой💬")
async def clinic_chat(message: Message, bot: Bot) -> None:
    await bot.send_message(
        message.chat.id,
        "Напишите ваш вопрос, администратор ответит вам в ближайшее время.",
    )


@user_router.message(F.text == "История📝")
async def history_stub(message: Message, bot: Bot) -> None:
    await bot.send_message(message.chat.id, "Ваша текущая история посещений будет здесь позже.")


@user_router.callback_query(F.data.startswith("del:"))
async def delete_appointment(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    appointments = user_appointments.get(user_id, [])
    try:
        idx = int(call.data.split("del:")[1])
    except ValueError:
        await bot.send_message(call.message.chat.id, "Некорректный номер записи.")
        return

    if 0 <= idx < len(appointments):
        removed = appointments.pop(idx)
        await bot.send_message(call.message.chat.id, f"Удалено: {fmt_one(removed)}")
    else:
        await bot.send_message(call.message.chat.id, "Запись не найдена.")


# ==== Админ-панель ====


@admin_router.message(Command("admin"))
async def cmd_start_admin(message: Message, bot: Bot) -> None:
    await start_admin(bot, message)


@admin_router.message(F.text == "Все записи📅")
async def admin_all_records(message: Message, bot: Bot) -> None:
    # Сводка по всем пользователям
    if any(user_appointments.values()):
        lines = []
        for uid, items in user_appointments.items():
            lines.append(f"Пользователь {uid}:")
            lines.extend([f" • {fmt_one(a)}" for a in items])
        await bot.send_message(message.chat.id, "\n".join(lines))
    else:
        await bot.send_message(message.chat.id, "Записей пока нет.")


@admin_router.message(F.text == "История📝")
async def admin_history(message: Message, bot: Bot) -> None:
    if any(user_appointments.values()):
        lines = ["История записей:"]
        for uid, items in user_appointments.items():
            lines.append(f"Пользователь {uid}:")
            lines.extend([f" • {fmt_one(a)}" for a in items])
        await bot.send_message(message.chat.id, "\n".join(lines))
    else:
        await bot.send_message(message.chat.id, "История пока пуста.")


@admin_router.message(F.text == "Чат💬")
async def admin_chat(message: Message, bot: Bot) -> None:
    await bot.send_message(message.chat.id, "Здесь в будущем будет чат с пациентами.")


@admin_router.message(F.text == "Поиск")
async def admin_search(message: Message, bot: Bot) -> None:
    await bot.send_message(message.chat.id, "Функция поиска будет добавлена позже.")


async def main() -> None:
    bot = Bot(
        config.api,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())