
import psycopg2
import logging
from typing import List
import bcrypt
from datetime import datetime
from sqlalchemy import create_engine, text
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database import connect_to_database
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
try:
    app = FastAPI()
    # Подключение к существующей базе данных
    connection = connect_to_database()
    # Курсор для выполнения операций с базой данных
    cur = connection.cursor()


    # Модели данных для API
    class User(BaseModel):
        username: str
        password: str
        created_at: datetime
        updated_at: datetime


    class Booking(BaseModel):
        user_id: int
        start_time: str
        end_time: str
        comment: str = None


    logger = logging.getLogger(__name__)


    # Получение всех существующих Booking
    def get_all_booking():
        # SQL-запрос для извлечения всех пользователей
        cur.execute("SELECT * FROM \"Booking\"")

        # Извлекаем всех пользователей в виде кортежей
        booking_records = cur.fetchall()

        return booking_records

    # Создание пользователя
    @app.post("/users/", response_model=User)
    def create_user(user: User):
        try:
            # Генерируем соль для bcrypt (обычно соль хранится вместе с зашифрованным паролем)
            salt = bcrypt.gensalt()

            # Хешируем пароль с использованием соли
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)

            cur.execute(
                "INSERT INTO \"User\" (username, password) VALUES (%s, %s) RETURNING id",
                (user.username, hashed_password.decode('utf-8'))
            )
            user_id = cur.fetchone()[0]
            connection.commit()
            return {"user_id": user_id, **user.dict()}
        except Exception as e:
            connection.rollback()
            logger.error("Error creating booking: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


    # Получение пользователя по ID
    @app.get("/users/{user_id}", response_model=User)
    def read_user(user_id: int):
        try:
            cur.execute("SELECT * FROM \"User\" WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                user = User(username=user_data[1], password=user_data[2],
                                created_at=user_data[3].strftime("%Y-%m-%dT%H:%M:%S"),
                                updated_at=user_data[4].strftime("%Y-%m-%dT%H:%M:%S"))
                return {"user_id": user_id, **user.dict()}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")


    # Удаление пользователя по ID
    @app.delete("/users/{user_id}", response_model=dict)
    def delete_user(user_id: int):
        try:
            cur.execute("DELETE FROM \"User\" WHERE id = %s", (user_id,))
            connection.commit()
            return {"message": "User deleted successfully"}
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


    # Обновление пользователя по ID
    @app.put("/users/{user_id}", response_model=User)
    def update_user(user_id: int, user: User):
        try:
            # Получите текущее время
            current_time = datetime.now()

            # Генерируем соль для bcrypt (обычно соль хранится вместе с зашифрованным паролем)
            salt = bcrypt.gensalt()

            # Хешируем пароль с использованием соли
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)

            cur.execute(
                "UPDATE \"User\" SET username = %s, password = %s, updated_at = %s WHERE id = %s RETURNING id",
                (user.username, hashed_password.decode('utf-8'), current_time, user_id)
            )
            updated_user_id = cur.fetchone()[0]
            connection.commit()
            return {"user_id": updated_user_id, **user.dict()}
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


    # Создание бронирования
    @app.post("/bookings/", response_model=Booking)
    def create_booking(booking: Booking):
        try:
            cur.execute(
                "INSERT INTO \"Booking\" (user_id, start_time, end_time, comment) VALUES (%s, %s, %s, %s) RETURNING id",
                (booking.user_id, booking.start_time, booking.end_time, booking.comment)
            )
            booking_id = cur.fetchone()[0]
            connection.commit()
            return {"booking_id": booking_id, **booking.dict()}
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")


    #Получения бронирования по ID
    @app.get("/bookings/{booking_id}", response_model=Booking)
    def read_booking(booking_id: int):
        try:
            cur.execute("SELECT * FROM \"Booking\" WHERE id = %s", (booking_id,))
            booking_data = cur.fetchone()
            if booking_data:
                booking = Booking(
                    user_id=booking_data[1],
                    start_time=booking_data[2],
                    end_time=booking_data[3],
                    comment=booking_data[4]
                )
                return {"booking_id": booking_id, **booking.dict()}
            else:
                raise HTTPException(status_code=404, detail="Booking not found")
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to retrieve booking: {str(e)}")

    # Получение всех существующих booking
    @app.get("/bookings/", response_model=List[Booking])
    def read_all_bookings():
        try:
            bookings_data = get_all_booking()
            if bookings_data:
                bookings = []
                for booking_data in bookings_data:
                    booking = Booking(
                        user_id=booking_data[1],
                        start_time=booking_data[2],
                        end_time=booking_data[3],
                        comment=booking_data[4]
                    )
                    bookings.append(booking)
                return bookings
            else:
                raise HTTPException(status_code=404, detail="No bookings found")
        except Exception as e:
            logger.error("Error retrieving users: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

    # Удаление бронирования по ID
    @app.delete("/bookings/{booking_id}", response_model=dict)
    def delete_booking(booking_id: int):
        try:
            cur.execute("DELETE FROM \"Booking\" WHERE id = %s", (booking_id,))
            connection.commit()
            return {"message": "Booking deleted successfully"}
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete booking: {str(e)}")


    # Обновление бронирования по ID
    @app.put("/bookings/{booking_id}", response_model=Booking)
    def update_booking(booking_id: int, booking: Booking):
        try:
            cur.execute(
                "UPDATE \"Booking\" SET user_id = %s, start_time = %s, end_time = %s, comment = %s WHERE id = %s RETURNING id",
                (booking.user_id, booking.start_time, booking.end_time, booking.comment, booking_id)
            )
            updated_booking_id = cur.fetchone()[0]
            connection.commit()
            return {"booking_id": updated_booking_id, **booking.dict()}
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")


    # Запуск FastAPI приложения
    if __name__ == "__main__":
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cur.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")