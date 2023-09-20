
import psycopg2
import bcrypt
from datetime import datetime
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database import connect_to_database
try:
    # Подключение к существующей базе данных
    connection = connect_to_database()
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