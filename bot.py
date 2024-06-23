import telebot
from telebot import types

import database as db_queries

API_TOKEN = '6961515410:AAHNhBjTn0ajhwUs-0qsya1z4F6tnM2nE2w'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}


class States:
    CITY = 1
    THEATER = 2
    DATE = 3
    SESSION = 4
    SEATS = 5
    PHONE = 6
    CONFIRMATION = 7


@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'seats': []}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    cities = db_queries.get_cities()
    for city in cities:
        markup.add(city)
    msg = bot.send_message(message.chat.id, "Вітаємо у нашій системі бронювання квитків! "
                                            "Будь ласка, оберіть місто:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_city_step)


def process_city_step(message):
    user_data[message.chat.id]['city'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    theaters = db_queries.get_theaters_by_city(message.text)
    for theater in theaters:
        markup.add(theater)
    msg = bot.send_message(message.chat.id, "Оберіть кінотеатр:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_theater_step)


def process_theater_step(message):
    user_data[message.chat.id]['theater'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    dates = db_queries.get_dates_by_theater(message.text)
    for date in dates:
        markup.add(date)
    msg = bot.send_message(message.chat.id, "Оберіть дату:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_date_step)


def process_date_step(message):
    user_data[message.chat.id]['date'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    sessions = db_queries.get_sessions_by_date_and_theater(message.text, user_data[message.chat.id]['theater'])
    for session in sessions:
        markup.add(f"{session[0]} - {session[1]} - Зал №{session[2]}")
    msg = bot.send_message(message.chat.id, "Оберіть сеанс:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_session_step)


def process_session_step(message):
    user_data[message.chat.id]['session'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    seats = db_queries.get_available_seats(user_data[message.chat.id]['date'],
                                           user_data[message.chat.id]['session'].split(" - ")[0],
                                           user_data[message.chat.id]['theater'])
    for seat in seats:
        markup.add(seat[0])

    markup.add("Завершити вибір місць")
    msg = bot.send_message(message.chat.id, "Оберіть місця (натисніть 'Завершити вибір місць' після вибору):",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, process_seat_selection_step)


def process_seat_selection_step(message):
    if message.text == "Завершити вибір місць":
        selected_seats = user_data[message.chat.id]['seats']
        if not selected_seats:
            msg = bot.send_message(message.chat.id,
                                   "Ви не обрали жодного місця. Будь ласка, оберіть хоча б одне місце.")
            bot.register_next_step_handler(msg, process_seat_selection_step)
        else:
            bot.send_message(message.chat.id, "Ваш вибір місць: " + ", ".join(selected_seats))
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            button_phone = types.KeyboardButton(text="Надіслати номер телефону", request_contact=True)
            markup.add(button_phone)
            msg = bot.send_message(message.chat.id, "Введіть ваш номер телефону для підтвердження бронювання:",
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, process_phone_step)
    else:
        user_data[message.chat.id]['seats'].append(message.text)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        session_time, _ = user_data[message.chat.id]['session'].split(" - ", 1)

        seats = db_queries.get_available_seats(user_data[message.chat.id]['date'],
                                               user_data[message.chat.id]['session'].split(" - ")[0],
                                               user_data[message.chat.id]['theater'])
        for seat in seats:
            if seat[0] not in user_data[message.chat.id]['seats']:
                markup.add(seat[0])

        markup.add("Завершити вибір місць")
        msg = bot.send_message(message.chat.id, "Оберіть місця (натисніть 'Завершити вибір місць' після вибору):",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, process_seat_selection_step)


def process_phone_step(message):
    user_data[message.chat.id]['phone'] = message.contact.phone_number if message.contact else message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Так', 'Ні')
    msg = bot.send_message(message.chat.id,
                           f"Підтвердити бронювання з номером телефону {user_data[message.chat.id]['phone']}?",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, process_confirmation_step)


def process_confirmation_step(message):
    if message.text == 'Так':
        try:
            booking_id = db_queries.book_seats(user_data[message.chat.id]['date'],
                                               user_data[message.chat.id]['session'].split(" - ")[0],
                                               user_data[message.chat.id]['theater'],
                                               user_data[message.chat.id]['seats'],
                                               user_data[message.chat.id]['phone'])
            bot.send_message(message.chat.id, f"Ваше бронювання успішно підтверджено!\n"
                                              f"ID бронювання: {booking_id}\n"
                                              f"Місто: {user_data[message.chat.id]['city']}\n"
                                              f"Кінотеатр: {user_data[message.chat.id]['theater']}\n"
                                              f"Дата: {user_data[message.chat.id]['date']}\n"
                                              f"Сеанс: {user_data[message.chat.id]['session']}\n"
                                              f"Місця: {', '.join(user_data[message.chat.id]['seats'])}\n"
                                              f"Телефон: {user_data[message.chat.id]['phone']}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Під час обробки вашого запиту виникла помилка: {str(e)}")
    else:
        bot.send_message(message.chat.id,
                         "Бронювання скасовано. Ви можете розпочати процес бронювання знову, використовуючи команду "
                         "/start.")


if __name__ == '__main__':
    bot.polling(none_stop=True)
