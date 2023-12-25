import json
from datetime import datetime

from sqlalchemy.orm import joinedload

from db_conn import DBConnector
from models import User, BankAccount
from db_engine import url_engine
from sqlalchemy import or_, and_
import hashlib




class Queries:
    def create_user(self, session, user_data):
        try:
            new_user = User(**user_data)
            session.add(new_user)
            session.commit()
            print("Пользователь Успешно создан!")
            return new_user.user_id  # Возвращаем user_id только что созданного пользователя
        except Exception as e:
            session.rollback()
            print(f"Ошибка при создании пользователя: {e}")
            return None

    def write_bank_info(self, session, bank_data):
        try:
            new_bank_account = BankAccount(**bank_data)
            session.add(new_bank_account)
            session.commit()
            print("Банковская Информация успешно записана!")
        except Exception as e:
            session.rollback()
            print(f"Ошибка при записи банковской информации: {e}")

    def find_user_by_phone(self, session, phone_number):
        try:
            user = session.query(User).filter_by(phone=phone_number).first()
            return user
        except Exception as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None

    def update_phone_number(self, session, phone_number, new_phone_number, pin):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account and bank_account.PIN == hashlib.sha256(pin.encode()).hexdigest():
                    user.phone = new_phone_number
                    user.updated_at = datetime.now()
                    session.commit()
                    print("Номер телефона успешно изменен.")
                else:
                    print("Неверный PIN или информация о банковском аккаунте не найдена !")
            else:
                print("Пользователь не найден.")
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении телефона: {e}")


    def update_pin(self, session, phone_number, pin, new_pin):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account and bank_account.PIN == hashlib.sha256(pin.encode()).hexdigest():
                    bank_account.PIN = hashlib.sha256(new_pin.encode()).hexdigest()
                    bank_account.updated_at = datetime.now()
                    session.commit()
                    print("PIN-код успешно изменен.")
                else:
                    print("Неверный PIN или информация о банковском аккаунте не найдена !")
            else:
                print("Пользователь не найден")
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении PIN-кода: {e}")

    def login_user(self, session, phone_number, pin):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account and bank_account.PIN == hashlib.sha256(pin.encode()).hexdigest():
                    print(f"Добро пожаловать, {user.name}")
                    return True
                else:
                    print("Неверный PIN или информация о банковском аккаунте не найдена !")
                    return False
            else:
                print("Пользователь не найден")
        except Exception as e:
            session.rollback()
            print(f"Ошибка при входе : {e}")

    def check_balance(self, session, phone_number):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account:
                    print(f"Баланс ---> {bank_account.balance}")
                else:
                    print("Информация о банковском аккаунте не найдена")
            else:
                print("Пользователь не найден")
        except Exception as e:
            session.rollback()
            print(f"Ошибка проверки баланса: {e}")

    def withdraw_cash(self, session, phone_number, cash_amount):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account:
                    if bank_account.balance >= cash_amount:
                        bank_account.balance -= cash_amount
                        session.commit()
                        print(f"Вы сняли {cash_amount} $")
                    else:
                        print("Недостаточно средств.")
                else:
                    print("Информация о банковском аккаунте не найдена")
            else:
                print("Пользователь не найден")
        except Exception as e:
            session.rollback()
            print(f"Ошибка снятия наличных: {e}")

    def deposit_cash(self, session, phone_number, deposit):
        try:
            user = self.find_user_by_phone(session, phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if bank_account:
                    bank_account.balance += deposit
                    session.commit()
                    print(f"Вы пополнили баланс на сумму {deposit} $")
                else:
                    print("Информация о банковском аккаунте не найдена")
            else:
                print("Пользователь не найден")
        except Exception as e:
            session.rollback()
            print(f"Ошибка снятия наличных: {e}")

    def send_money(self, session, phone_number, other_phone_number, cash_amount):
        try:
            user = self.find_user_by_phone(session, phone_number)
            user2 = self.find_user_by_phone(session, other_phone_number)
            if user:
                bank_account = session.query(BankAccount).filter_by(user_id=user.user_id).first()
                if user2:
                    bank_account2 = session.query(BankAccount).filter_by(user_id=user2.user_id).first()
                    if bank_account and bank_account2:
                        if bank_account.balance >= cash_amount:
                            bank_account.balance -= cash_amount
                            bank_account2.balance += cash_amount
                            session.commit()
                            print(f"Вы успешно перевели {cash_amount}$ пользователю, с именем {user2.name}")
                        else:
                            print("Недостаточно средств.")
                    else:
                        print("Информация о банковских аккаунтах не найдена.")
                else:
                    print("Получатель не найден.")
            else:
                print("Пользователь (отправитель) не найден.")
        except Exception as e:
            session.rollback()
            print(f"Ошибка банковской операции : {e}")


# Создаем экземпляр класса
result_queries = Queries()

while True:
    print("Добро пожаловать !")
    print("1. Создать пользователя и банковский счет")
    print("2. Войти в систему")
    print("3. Выход")

    user_input = input("Выберите действие (1, 2, 3): ")
    if user_input == '1':
        with DBConnector(db_url=url_engine) as session:
            # Запрос данных с клавиатуры для создания пользователя
            user_data = {
                "name": input("Введите имя пользователя: "),
                "surname": input("Введите фамилию пользователя: "),
                "phone": input("Введите номер телефона пользователя: "),
            }

            user_id = result_queries.create_user(session, user_data)

            # Если пользователь успешно создан, запрашиваем данные для создания банковской информации
            if user_id is not None:
                bank_data = {
                    "user_id": user_id,  # Используем полученный user_id
                    "balance": float(input("Введите баланс счета: ")),
                    "card_number": input("Введите номер карты: "),
                    "PIN": input("Введите PIN-код: ")
                }
                hashed_pin = hashlib.sha256(bank_data['PIN'].encode()).hexdigest()
                bank_data['PIN'] = hashed_pin
                result_queries.write_bank_info(session, bank_data)
    if user_input == '2':
        with DBConnector(db_url=url_engine) as session:
            print("Вход в систему...")
            phone_number = input("Введите номер телефона: ")
            pin_code = input("Введите Ваш PIN-код: ")
            if result_queries.login_user(session, phone_number, pin_code):
                while True:
                    print("1. Просмотр баланса")
                    print("2. Положить деньги на счет")
                    print("3. Снять наличные")
                    print("4. Перевод денег")
                    print("5. Изменить данные")
                    print("6. Выход")
                    action = input("Выберите действие (1, 2, 3, 4, 5): ")

                    if action == '1':
                        with DBConnector(db_url=url_engine) as session:
                            phone = phone_number
                            result_queries.check_balance(session, phone)
                    elif action == '2':
                        with DBConnector(db_url=url_engine) as session:
                            phone = phone_number
                            deposit = float(input("Введите сумму пополнения: "))
                            result_queries.deposit_cash(session, phone, deposit)
                    elif action == '3':
                        with DBConnector(db_url=url_engine) as session:
                            phone = phone_number
                            cash = float(input("Введите сумму для снятия: "))
                            result_queries.withdraw_cash(session, phone, cash)
                    elif action == '4':
                        with DBConnector(db_url=url_engine) as session:
                            phone = phone_number
                            other_phone = input("Введите номер телефона получателя: ")
                            cash_amount1 = float(input("Введите сумму для перевода: "))
                            result_queries.send_money(session, phone, other_phone, cash_amount1)
                    elif action == '5':
                        while True:
                            print("1. Изменить номер телефона")
                            print("2. Изменить PIN-код")
                            print("3. Выход")
                            action = input("Выберите действие (1, 2, 3): ")
                            if action == '1':
                                with DBConnector(db_url=url_engine) as session:
                                    phone = phone_number
                                    new_phone = input("Введите новый номер телефона: ")
                                    pin_code = input("Введите Ваш PIN-код: ")
                                    result_queries.update_phone_number(session, phone, new_phone, pin_code)
                            elif action == '2':
                                with DBConnector(db_url=url_engine) as session:
                                    phone = phone_number
                                    pin_code = input("Введите Ваш PIN-код: ")
                                    new_pin = input("Введите новый PIN-код: ")
                                    result_queries.update_pin(session, phone, pin_code, new_pin)
                            elif action == '3':
                                print("Вы вышли")
                                break
                    elif action == '6':
                        print("Вы вышли")
                        break
                    else:
                        print("Неверный выбор")
    if user_input == '3':
        print("Вы вышли из программы.")
        break

