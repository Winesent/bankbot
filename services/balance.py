from decimal import Decimal
from database.db import get_connection
from database.models import User

class BalanceService:
    @staticmethod
    def get_user(user_id: int) -> User | None:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username, balance, created_at FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None

    @staticmethod
    def create_user(user_id: int, username: str | None) -> User:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (user_id, username, balance) VALUES (?, ?, 0) RETURNING user_id, username, balance, created_at',
                (user_id, username))
            row = cursor.fetchone()
            conn.commit()
            return User(*row)

    @staticmethod
    def get_or_create_user(user_id: int, username: str | None) -> User:
        user = BalanceService.get_user(user_id)
        if not user:
            user = BalanceService.create_user(user_id, username)
        return user

    @staticmethod
    def update_balance(user_id: int, amount: Decimal) -> User:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET balance = balance + ? WHERE user_id = ? RETURNING user_id, username, balance, created_at',
                (float(amount), user_id))
            row = cursor.fetchone()
            conn.commit()
            if not row:
                raise ValueError("User not found")
            return User(*row)

    @staticmethod
    def transfer(from_user_id: int, to_username: str, amount: Decimal) -> tuple[User, User]:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with get_connection() as conn:
            cursor = conn.cursor()

            # Получаем отправителя
            cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (from_user_id,))
            from_user = cursor.fetchone()
            if not from_user:
                raise ValueError("Sender not found")

            # Проверяем баланс
            if Decimal(from_user[2]) < amount:
                raise ValueError("Insufficient funds")

            # Получаем получателя
            cursor.execute('SELECT user_id, username, balance FROM users WHERE username = ?', (to_username,))
            to_user = cursor.fetchone()
            if not to_user:
                raise ValueError("Recipient not found")

            # Проверяем что не перевод самому себе
            if from_user[0] == to_user[0]:
                raise ValueError("Cannot transfer to yourself")

            # Выполняем перевод
            cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?',
                          (float(amount), from_user_id))
            cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?',
                          (float(amount), to_user[0]))

            # Записываем транзакцию
            cursor.execute(
                'INSERT INTO transactions (from_user_id, to_user_id, amount) VALUES (?, ?, ?)',
                (from_user_id, to_user[0], float(amount)))

            conn.commit()

            # Возвращаем обновленные данные пользователей
            cursor.execute('SELECT user_id, username, balance, created_at FROM users WHERE user_id = ?', (from_user_id,))
            updated_from = User(*cursor.fetchone())

            cursor.execute('SELECT user_id, username, balance, created_at FROM users WHERE user_id = ?', (to_user[0],))
            updated_to = User(*cursor.fetchone())

            return updated_from, updated_to

    @staticmethod
    def admin_update_balance(username: str, amount: Decimal) -> User:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET balance = balance + ? WHERE username = ? RETURNING user_id, username, balance, created_at',
                (float(amount), username))
            row = cursor.fetchone()
            conn.commit()
            if not row:
                raise ValueError("User not found")
            return User(*row)

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username, balance, created_at FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None