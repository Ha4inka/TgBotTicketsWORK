# database.py

import random
from datetime import datetime, timedelta


def create_tables():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    # Створення таблиць
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS theaters (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city_id INTEGER NOT NULL,
            number_of_halls INTEGER NOT NULL,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            trailer_url TEXT
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theater_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            film_id INTEGER NOT NULL,
            hall_number INTEGER NOT NULL,
            FOREIGN KEY (theater_id) REFERENCES theaters(id),
            FOREIGN KEY (film_id) REFERENCES films(id)
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            status TEXT NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            theater TEXT NOT NULL,
            date TEXT NOT NULL,
            session TEXT NOT NULL,
            phone TEXT NOT NULL,
            ticket_id TEXT UNIQUE NOT NULL
        )
        ''')

    conn.commit()
    conn.close()


def drop_tables():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS bookings')
    cursor.execute('DROP TABLE IF EXISTS seats')
    cursor.execute('DROP TABLE IF EXISTS sessions')
    cursor.execute('DROP TABLE IF EXISTS theaters')
    cursor.execute('DROP TABLE IF EXISTS cities')
    cursor.execute('DROP TABLE IF EXISTS films')

    conn.commit()
    conn.close()


def init_db():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    # Додаємо міста
    cursor.execute('INSERT OR IGNORE INTO cities (id, name) VALUES (1, "Черкаси")')
    cursor.execute('INSERT OR IGNORE INTO cities (id, name) VALUES (2, "Кривий Ріг")')
    cursor.execute('INSERT OR IGNORE INTO cities (id, name) VALUES (3, "Львів")')

    # Додаємо кінотеатри
    theaters = [
        (1, "Любава", 1, 2),
        (2, "Дніпро Плаза", 1, 2),
        (3, "Victory Plaza", 2, 2),
        (4, "Spartak", 3, 1),
        (5, "Аркадія", 3, 2),
        (6, "Аврора", 1, 1),
        (7, "Галактика", 2, 2)
    ]
    cursor.executemany('INSERT OR IGNORE INTO theaters (id, name, city_id, number_of_halls) VALUES (?,?,?,?)', theaters)

    # Додаємо фільми
    films = [
        (1, "Пірати Карибського моря", "Фентезі пригоди", "https://www.youtube.com/watch?v=trailer1"),
        (2, "Зоряні війни", "Фантастика", "https://www.youtube.com/watch?v=trailer2"),
        (3, "Володар перснів", "Фентезі", "https://www.youtube.com/watch?v=trailer3"),
        (4, "Гаррі Поттер", "Фентезі", "https://www.youtube.com/watch?v=trailer4"),
        (5, "Термінатор", "Наукова фантастика", "https://www.youtube.com/watch?v=trailer5"),
        (6, "Матриця", "Наукова фантастика", "https://www.youtube.com/watch?v=trailer6"),
        (7, "Втеча з Шоушенка", "Драма", "https://www.youtube.com/watch?v=trailer7"),
        (8, "Гра престолів", "Фентезі", "https://www.youtube.com/watch?v=trailer8"),
        (9, "У джазі тільки дівчата", "Мюзикл", "https://www.youtube.com/watch?v=trailer9"),
        (10, "Список Шиндлера", "Драма", "https://www.youtube.com/watch?v=trailer10")
    ]
    cursor.executemany('INSERT OR IGNORE INTO films (id, title, description, trailer_url) VALUES (?,?,?,?)', films)

    # Додаємо сеанси
    sessions = []
    for theater in theaters:
        theater_id = theater[0]
        hall_count = theater[3]
        film_count = len(films)
        dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        times = ["10:00", "14:00", "18:00", "20:00"]

        for date in dates:
            for time in times:
                for hall_number in range(1, hall_count + 1):
                    film_id = random.choice(range(1, film_count + 1))  # Випадковий вибір фільму
                    sessions.append((None, theater_id, date, time, film_id, hall_number))

    cursor.executemany('INSERT OR IGNORE INTO sessions VALUES (?,?,?,?,?,?)', sessions)

    # Генерація місць для кожного сеансу
    rows = range(1, 11)  # Числові обозначення рядів (від 1 до 10)
    seats_per_row = 10  # Кількість місць у кожному ряді

    cursor.execute('SELECT id FROM sessions')
    session_ids = cursor.fetchall()

    for session_id in session_ids:
        for row in rows:
            for seat in range(1, seats_per_row + 1):
                seat_number = f"{row} ряд {seat} місце"
                price = random.randint(5000, 15000)  # Випадкова ціна квитка в копійках
                cursor.execute('INSERT OR IGNORE INTO seats (session_id, seat_number, status, price) VALUES (?,?,?,?)',
                               (session_id[0], seat_number, "вільно", price))

    conn.commit()
    conn.close()


def clear_db():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM bookings')
    cursor.execute('DELETE FROM seats')
    cursor.execute('DELETE FROM sessions')
    cursor.execute('DELETE FROM theaters')
    cursor.execute('DELETE FROM cities')

    conn.commit()
    conn.close()


def get_cities():
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM cities')
    cities = cursor.fetchall()
    conn.close()
    return [city[0] for city in cities]


def get_theaters_by_city(city_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM theaters WHERE city_id = (SELECT id FROM cities WHERE name = ?)', (city_name,))
    theaters = cursor.fetchall()
    conn.close()
    return [theater[0] for theater in theaters]


def get_dates_by_theater(theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT date FROM sessions WHERE theater_id = (SELECT id FROM theaters WHERE name = ?)',
                   (theater_name,))
    dates = cursor.fetchall()
    conn.close()
    return [date[0] for date in dates]


def get_sessions_by_date_and_theater(date, theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT time, films.title, sessions.hall_number
                      FROM sessions
                      JOIN films ON sessions.film_id = films.id
                      WHERE date = ?
                      AND theater_id = (SELECT id FROM theaters WHERE name = ?)''',
                   (date, theater_name))
    sessions = cursor.fetchall()
    conn.close()
    return sessions


import sqlite3


def get_available_seats(date, time, theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT seat_number 
                      FROM seats 
                      WHERE session_id = (
                          SELECT id 
                          FROM sessions 
                          WHERE date = ? 
                          AND time = ? 
                          AND theater_id = (
                              SELECT id FROM theaters WHERE name = ?
                          )
                      ) AND status = 'вільно' ''',
                   (date, time, theater_name))
    seats = cursor.fetchall()

    conn.close()

    return seats


def book_seats(date, time, theater_name, seats, phone):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()

    booking_id = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

    cursor.execute(
        'INSERT INTO bookings (city, theater, date, session, phone, ticket_id) VALUES (?, ?, ?, ?, ?, ?)',
        (get_city_by_theater(theater_name), theater_name, date,
         f"{time} - {get_movie_by_date_time_theater(date, time, theater_name)} - Зал №{get_hall_by_date_time_theater(date, time, theater_name)}",
         phone, booking_id))

    cursor.execute('''UPDATE seats SET status = 'заброньовано'
                      WHERE session_id = (SELECT id FROM sessions
                                          WHERE date = ?
                                          AND time = ?
                                          AND theater_id = (SELECT id FROM theaters WHERE name = ?))
                      AND seat_number IN ({})'''.format(",".join(["?"] * len(seats))),
                   [date, time, theater_name] + seats)

    conn.commit()
    conn.close()

    return booking_id  # Return the booking_id


def get_city_by_theater(theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT cities.name FROM theaters JOIN cities ON theaters.city_id = cities.id WHERE theaters.name = ?',
        (theater_name,))
    city = cursor.fetchone()[0]
    conn.close()
    return city


def get_movie_by_date_time_theater(date, time, theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT films.title
                      FROM sessions
                      JOIN films ON sessions.film_id = films.id
                      WHERE sessions.date = ?
                      AND sessions.time = ?
                      AND sessions.theater_id = (SELECT id FROM theaters WHERE name = ?)''',
                   (date, time, theater_name))
    movie = cursor.fetchone()[0]
    conn.close()
    return movie


def get_hall_by_date_time_theater(date, time, theater_name):
    conn = sqlite3.connect('cinema_booking.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT sessions.hall_number
                      FROM sessions
                      WHERE sessions.date = ?
                      AND sessions.time = ?
                      AND sessions.theater_id = (SELECT id FROM theaters WHERE name = ?)''',
                   (date, time, theater_name))
    hall = cursor.fetchone()[0]
    conn.close()
    return hall


if __name__ == "__main__":
    create_tables()
    init_db()
