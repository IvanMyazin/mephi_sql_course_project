# ФИО студента: Иван Мязин
# Вариант: 19, информационная система таксопарка.
# Условие варианта: заменить таблицы people и phone на автомобили и водителей.
# Для автомобилей реализовать просмотр, добавление, изменение и удаление.
# Для выбранного автомобиля реализовать просмотр, добавление и удаление водителей.
# В интерфейсе нельзя показывать и запрашивать значения суррогатных ключей.
# Все запросы с данными пользователя должны быть защищены от SQL-инъекций.

import re
from datetime import date, datetime

import psycopg2
import yaml
from psycopg2.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from dbconnection import DbConnection
from dbtable import DbTable
from project_config import ProjectConfig
from tables.drivers_table import DriversTable
from tables.vehicles_table import VehiclesTable


CANCEL = object()
NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё -]+$")
NUMBER_PATTERN = re.compile(r"^[АВЕКМНОРСТУХ][0-9]{3}[АВЕКМНОРСТУХ]{2}[0-9]{2,3}$")


class Main:
    def __init__(self):
        self.config = ProjectConfig()
        self.connection = DbConnection(self.config)
        DbTable.dbconn = self.connection
        self.vehicles = VehiclesTable()
        self.drivers = DriversTable()

    def db_init(self):
        self.vehicles.create()
        self.drivers.create()

    def db_reset(self):
        self.drivers.drop()
        self.vehicles.drop()
        self.db_init()
        self.add_demo_data()

    def add_demo_data(self):
        vehicle_ids = []
        vehicle_ids.append(self.vehicles.insert_one("Hyundai Solaris", "эконом", "А123ВС777", "желтый", 2021))
        vehicle_ids.append(self.vehicles.insert_one("Kia Rio", "эконом", "Е456КМ799", "белый", 2020))
        vehicle_ids.append(self.vehicles.insert_one("Skoda Octavia", "комфорт", "М789ОР797", "черный", 2022))
        vehicle_ids.append(self.vehicles.insert_one("Toyota Camry", "бизнес", "С321ТА777", "черный", 2021))
        vehicle_ids.append(self.vehicles.insert_one("Volkswagen Polo", "эконом", "У654ХК799", "желтый", 2019))

        self.drivers.insert_one("Иванов", "Алексей", "Сергеевич", date(1987, 4, 12), "770100000001", "4501000001", vehicle_ids[0])
        self.drivers.insert_one("Петров", "Михаил", "Андреевич", date(1991, 9, 23), "770100000002", "4501000002", vehicle_ids[1])
        self.drivers.insert_one("Соколов", "Денис", "Игоревич", date(1984, 1, 17), "770100000003", "4501000003", vehicle_ids[2])
        self.drivers.insert_one("Кузнецов", "Роман", "Олегович", date(1989, 7, 5), "770100000004", "4501000004", vehicle_ids[3])
        self.drivers.insert_one("Морозов", "Павел", "Викторович", date(1993, 11, 28), "770100000005", "4501000005", vehicle_ids[4])

    def read_position(self, count, prompt):
        while True:
            value = input(prompt).strip()

            if value == "0":
                return None
            if not value.isdigit():
                print("Введите номер строки.")
                continue

            position = int(value)
            if position < 1 or position > count:
                print("Строки с таким номером нет.")
                continue

            return position - 1

    def read_text(self, prompt, max_length, default=None, allow_empty=False):
        while True:
            value = input(prompt).strip()

            if value == "0":
                return CANCEL
            if value == "" and default is not None:
                return default
            if value == "" and allow_empty:
                return ""
            if value == "":
                print("Поле не может быть пустым.")
                continue
            if len(value) > max_length:
                print("Допустимо не более %d символов." % max_length)
                continue

            return value

    def read_name(self, prompt, default=None, allow_empty=False):
        while True:
            value = self.read_text(prompt, 50, default, allow_empty)

            if value is CANCEL or value == "":
                return value
            if not NAME_PATTERN.fullmatch(value):
                print("Используйте только буквы, пробел и дефис.")
                continue

            return value

    def read_segment(self, default=None):
        segments = {"1": "эконом", "2": "комфорт", "3": "бизнес"}

        while True:
            text = "Класс: 1 - эконом, 2 - комфорт, 3 - бизнес"
            if default:
                text += " [%s]" % default
            value = input(text + " (0 - отмена): ").strip()

            if value == "0":
                return CANCEL
            if value == "" and default:
                return default
            if value in segments:
                return segments[value]

            print("Выберите 1, 2 или 3.")

    def read_registration_number(self, default=None):
        while True:
            text = "Госномер"
            if default:
                text += " [%s]" % default
            value = input(text + " (0 - отмена): ").strip().upper().replace(" ", "")

            if value == "0":
                return CANCEL
            if value == "" and default:
                return default
            if not NUMBER_PATTERN.fullmatch(value):
                print("Пример правильного госномера: А123ВС777.")
                continue

            return value

    def read_year(self, default=None):
        while True:
            text = "Год выпуска"
            if default:
                text += " [%s]" % default
            value = input(text + " (0 - отмена): ").strip()

            if value == "0":
                return CANCEL
            if value == "" and default:
                return default
            if not value.isdigit():
                print("Год должен быть целым числом.")
                continue

            year = int(value)
            if year < 1900 or year > date.today().year + 1:
                print("Укажите корректный год выпуска.")
                continue

            return year

    def read_digits(self, prompt, length):
        while True:
            value = input(prompt).strip()

            if value == "0":
                return CANCEL
            if len(value) != length or not value.isdigit():
                print("Значение должно состоять из %d цифр." % length)
                continue

            return value

    def read_birth_date(self):
        while True:
            value = input("Дата рождения в формате ДД.ММ.ГГГГ (0 - отмена): ").strip()

            if value == "0":
                return CANCEL

            try:
                birth_date = datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                print("Введите существующую дату в формате ДД.ММ.ГГГГ.")
                continue

            today = date.today()
            try:
                adult_date = today.replace(year=today.year - 18)
            except ValueError:
                adult_date = today.replace(year=today.year - 18, day=28)

            if birth_date < date(1900, 1, 1) or birth_date > adult_date:
                print("Водитель должен быть старше 18 лет.")
                continue

            return birth_date

    def show_vehicles(self, vehicles=None):
        if vehicles is None:
            vehicles = self.vehicles.all()

        print("\nАвтомобили")
        print("№ | Марка | Класс | Госномер | Цвет | Год")
        for number, vehicle in enumerate(vehicles, 1):
            print("%d | %s | %s | %s | %s | %s" % (
                number, vehicle[1], vehicle[2], vehicle[3], vehicle[4], vehicle[5]
            ))

        if not vehicles:
            print("Список пуст.")

        return vehicles

    def select_vehicle(self):
        vehicles = self.show_vehicles()
        if not vehicles:
            return None

        position = self.read_position(len(vehicles), "Номер автомобиля (0 - отмена): ")
        if position is None:
            return None

        return vehicles[position]

    def add_vehicle(self):
        print("\nДобавление автомобиля")
        brand = self.read_text("Марка (0 - отмена): ", 50)
        if brand is CANCEL:
            return
        segment = self.read_segment()
        if segment is CANCEL:
            return
        registration_number = self.read_registration_number()
        if registration_number is CANCEL:
            return
        colour = self.read_text("Цвет (0 - отмена): ", 30)
        if colour is CANCEL:
            return
        prod_year = self.read_year()
        if prod_year is CANCEL:
            return

        self.vehicles.insert_one(brand, segment, registration_number, colour, prod_year)
        print("Автомобиль добавлен.")

    def edit_vehicle(self):
        vehicle = self.select_vehicle()
        if vehicle is None:
            return

        print("Пустая строка оставляет старое значение.")
        brand = self.read_text("Марка [%s] (0 - отмена): " % vehicle[1], 50, vehicle[1])
        if brand is CANCEL:
            return
        segment = self.read_segment(vehicle[2])
        if segment is CANCEL:
            return
        registration_number = self.read_registration_number(vehicle[3])
        if registration_number is CANCEL:
            return
        colour = self.read_text("Цвет [%s] (0 - отмена): " % vehicle[4], 30, vehicle[4])
        if colour is CANCEL:
            return
        prod_year = self.read_year(vehicle[5])
        if prod_year is CANCEL:
            return

        self.vehicles.update_one(vehicle[0], brand, segment, registration_number, colour, prod_year)
        print("Автомобиль изменен.")

    def delete_vehicle(self):
        vehicle = self.select_vehicle()
        if vehicle is None:
            return

        drivers_count = self.drivers.count_by_vehicle(vehicle[0])
        print("Автомобиль: %s, %s" % (vehicle[1], vehicle[3]))
        print("Связанных водителей: %d. Они тоже будут удалены." % drivers_count)
        answer = input("Для удаления введите ДА: ").strip().upper()

        if answer != "ДА":
            print("Удаление отменено.")
            return

        self.vehicles.delete_one(vehicle[0])
        print("Автомобиль удален.")

    def show_drivers(self, vehicle):
        drivers = self.drivers.all_by_vehicle(vehicle[0])
        print("\nВодители автомобиля %s, %s" % (vehicle[1], vehicle[3]))
        print("№ | ФИО | Дата рождения | ИНН | Паспорт")

        for number, driver in enumerate(drivers, 1):
            full_name = "%s %s %s" % (driver[1], driver[2], driver[3] or "")
            print("%d | %s | %s | %s | %s" % (
                number,
                full_name.strip(),
                driver[4].strftime("%d.%m.%Y"),
                driver[5],
                driver[6],
            ))

        if not drivers:
            print("Список пуст.")

        return drivers

    def add_driver(self, vehicle):
        print("\nДобавление водителя")
        surname = self.read_name("Фамилия (0 - отмена): ")
        if surname is CANCEL:
            return
        name = self.read_name("Имя (0 - отмена): ")
        if name is CANCEL:
            return
        middle_name = self.read_name("Отчество, можно оставить пустым (0 - отмена): ", allow_empty=True)
        if middle_name is CANCEL:
            return
        if middle_name == "":
            middle_name = None
        birth_date = self.read_birth_date()
        if birth_date is CANCEL:
            return
        inn = self.read_digits("ИНН, 12 цифр (0 - отмена): ", 12)
        if inn is CANCEL:
            return
        passport = self.read_digits("Серия и номер паспорта, 10 цифр (0 - отмена): ", 10)
        if passport is CANCEL:
            return

        self.drivers.insert_one(
            surname, name, middle_name, birth_date, inn, passport, vehicle[0]
        )
        print("Водитель добавлен.")

    def delete_driver(self, vehicle):
        drivers = self.show_drivers(vehicle)
        if not drivers:
            return

        position = self.read_position(len(drivers), "Номер водителя (0 - отмена): ")
        if position is None:
            return

        driver = drivers[position]
        answer = input("Для удаления водителя %s %s введите ДА: " % (
            driver[1], driver[2]
        )).strip().upper()

        if answer != "ДА":
            print("Удаление отменено.")
            return

        self.drivers.delete_one(driver[0])
        print("Водитель удален.")

    def drivers_menu(self):
        vehicle = self.select_vehicle()
        if vehicle is None:
            return

        while True:
            self.show_drivers(vehicle)
            print("\n1 - добавить водителя")
            print("2 - удалить водителя")
            print("0 - вернуться к автомобилям")
            choice = input("=> ").strip()

            if choice == "1":
                self.run_action(self.add_driver, vehicle)
            elif choice == "2":
                self.run_action(self.delete_driver, vehicle)
            elif choice == "0":
                return
            else:
                print("Выберите пункт из меню.")

    def vehicles_menu(self):
        while True:
            self.show_vehicles()
            print("\n1 - добавить автомобиль")
            print("2 - изменить автомобиль")
            print("3 - удалить автомобиль")
            print("4 - водители выбранного автомобиля")
            print("0 - главное меню")
            choice = input("=> ").strip()

            if choice == "1":
                self.run_action(self.add_vehicle)
            elif choice == "2":
                self.run_action(self.edit_vehicle)
            elif choice == "3":
                self.run_action(self.delete_vehicle)
            elif choice == "4":
                self.run_action(self.drivers_menu)
            elif choice == "0":
                return
            else:
                print("Выберите пункт из меню.")

    def reset_menu(self):
        answer = input("Все автомобили и водители будут удалены. Введите ДА: ").strip().upper()
        if answer != "ДА":
            print("Сброс отменен.")
            return

        self.db_reset()
        print("Таблицы созданы заново и заполнены тестовыми данными.")

    def show_db_error(self, error):
        if isinstance(error, UniqueViolation):
            print("Такая запись уже существует. Проверьте госномер, ИНН и паспорт.")
        elif isinstance(error, CheckViolation):
            print("Данные не прошли проверку. Проверьте введенные значения.")
        elif isinstance(error, ForeignKeyViolation):
            print("Связанная запись не найдена или используется в другой таблице.")
        else:
            print("Не удалось выполнить действие с базой данных.")

    def run_action(self, action, *args):
        try:
            action(*args)
        except psycopg2.Error as error:
            self.connection.conn.rollback()
            self.show_db_error(error)
        except ValueError as error:
            print("Ошибка:", error)

    def run(self):
        self.db_init()

        while True:
            print("\nТаксопарк")
            print("1 - автомобили")
            print("2 - пересоздать таблицы и добавить тестовые данные")
            print("9 - выход")
            choice = input("=> ").strip()

            if choice == "1":
                self.vehicles_menu()
            elif choice == "2":
                self.run_action(self.reset_menu)
            elif choice == "9":
                print("До свидания!")
                return
            else:
                print("Выберите пункт из меню.")


def main():
    app = None

    try:
        app = Main()
        app.run()
    except psycopg2.OperationalError:
        print("Не удалось подключиться к PostgreSQL. Проверьте config.yaml и сервер БД.")
    except psycopg2.Error:
        print("Не удалось подготовить таблицы в PostgreSQL.")
    except (KeyError, ValueError, OSError, yaml.YAMLError) as error:
        print("Ошибка конфигурации:", error)
    except (KeyboardInterrupt, EOFError):
        print("\nРабота завершена.")
    finally:
        if app:
            app.connection.close()


if __name__ == "__main__":
    main()
