import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def connect_to_database():
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
               DROP TABLE IF EXISTS "Booking"
           """)
        # Очистка таблицы "User"
        cur.execute("""
               DROP TABLE IF EXISTS "User"
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
                    user_id integer REFERENCES "User" (id) ON DELETE CASCADE,
                    start_time text NOT NULL,
                    end_time text NOT NULL,
                    comment text
                )
            """)
        return connection
    except (Exception, Error) as error:
        print("Ошибка при подключении к PostgreSQL", error)
        return None
