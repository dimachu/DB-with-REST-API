
import psycopg2
import bcrypt
from datetime import datetime
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user="postgres",
                                  password="1111",
                                  host="127.0.0.1",
                                  port="5432")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # Курсор для выполнения операций с базой данных
    cur = connection.cursor()
    # Очистка таблицы "Booking"
    cur.execute("""
        TRUNCATE TABLE "Booking" RESTART IDENTITY CASCADE
    """)
    # Очистка таблицы "User"
    cur.execute("""
        TRUNCATE TABLE "User" RESTART IDENTITY CASCADE
    """)
    # Создание таблицы User
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
            id serial PRIMARY KEY,
            username text NOT NULL,
            password text NOT NULL,
            created_at timestamp DEFAULT current_timestamp,
            updated_at timestamp DEFAULT current_timestamp
        )
    """)

    # Создание таблицы Booking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "Booking" (
            id serial PRIMARY KEY,
            user_id integer REFERENCES "User" (id),
            start_time text NOT NULL,
            end_time text NOT NULL,
            comment text
        )
    """)

    # Хешируем пароль пользователя с использованием bcrypt
    password = "sample_password".encode('utf-8')  # Преобразовываем пароль в байты
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # Вставляем хешированный пароль в таблицу User
    cur.execute("""
        INSERT INTO "User" (username, password) VALUES (%s, %s)
        RETURNING id
    """, ("sample_user", hashed_password.decode('utf-8')))

    user_id = cur.fetchone()[0]

    # Вставка данных в таблицу Booking
    cur.execute("""
        INSERT INTO "Booking" (user_id, start_time, end_time, comment) VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, "2023-09-20 10:00:00", "2023-09-20 12:00:00", "Sample booking comment"))

    booking_id = cur.fetchone()[0]

    # Применение изменений к базе данных
    connection.commit()

    # Запрос данных о пользователе и бронировании
    cur.execute("""
        SELECT * FROM "User" WHERE id = %s
    """, (user_id,))

    user_data = cur.fetchone()

    cur.execute("""
        SELECT * FROM "Booking" WHERE id = %s
    """, (booking_id,))

    booking_data = cur.fetchone()

    # Получаем значение времени из базы данных
    created_at = user_data[3]
    updated_at = user_data[4]

    # Форматируем время без миллисекунд
    created_at_formatted = created_at.strftime('%Y-%m-%d %H:%M:%S')
    updated_at_formatted = updated_at.strftime('%Y-%m-%d %H:%M:%S')

    # Вывод информации на экран
    print("User Data:")
    print("ID:", user_data[0])
    print("Username:", user_data[1])
    print("Password:", user_data[2])
    print("Created At:", created_at_formatted)
    print("Updated At:", updated_at_formatted)

    print("\nBooking Data:")
    print("ID:", booking_data[0])
    print("User ID:", booking_data[1])
    print("Start Time:", booking_data[2])
    print("End Time:", booking_data[3])
    print("Comment:", booking_data[4])
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cur.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")