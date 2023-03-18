import sqlite3
from dadata import Dadata
import os.path
import httpx

db_file_path = "sqlite_python.db"
menu_items = ("1) Ввести адрес", "2) Настройки конфигурации", "3) Выход")

if not os.path.exists(db_file_path):
    file = open("sqlite_python.db", "a")
    file.close()

try:
    sqlite_connection = sqlite3.connect('sqlite_python.db')
    cursor = sqlite_connection.cursor()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)

cursor.execute("CREATE TABLE IF NOT EXISTS config(ID TEXT, Value TEXT);")
cursor.execute("SELECT count(*) FROM config;")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO config(ID, Value) VALUES ('URL', 'https://dadata.ru/'),('API key', 'NONE'), ('Language', 'ru');")


def menu():
    try:
        cursor.execute("SELECT Value FROM config WHERE ID = 'API key';")
        token = cursor.fetchone()[0]
        dadata = Dadata(token)
        while(True):
            print("__________MAIN MENU__________")
            print(menu_items[0])
            print(menu_items[1])
            print(menu_items[2])
            choise = input("Введите номер команды из меню: ")

            try:
                menu_num = int(choise)
                if menu_num == 1:

                    cursor.execute(
                        "SELECT Value FROM config WHERE ID = 'Language'")
                    language = cursor.fetchone()[0]
                    while(True):
                        address_str = input("Введите адрес: ")
                        result = dadata.suggest(
                            "address", address_str, language=language)
                        print("Список подходящих адресов: ")
                        for item in result:
                            print(result.index(item) + 1, ") ", item['value'])
                        print("0) Задать другой адрес")
                        choise_address_num = int(
                            input("Введите номер нужного адреса: "))
                        if choise_address_num == 0:
                            break
                        elif choise_address_num >= 1 and choise_address_num <= len(result):
                            result_geo = dadata.suggest(
                                "address", result[choise_address_num-1]['value'], count=1, language=language)
                            print(result_geo[0]['value'])
                            print(result_geo[0]['data']['geo_lat'],
                                  result_geo[0]['data']['geo_lon'])
                            break
                elif menu_num == 2:
                    menu_sql()
                elif menu_num == 3:
                    dadata.close()
                    break
                else:
                    print("Указанной команды нет в меню")
                    continue
            except ValueError:
                print("Пожалуйста, введите число")
    except httpx.HTTPStatusError as exc:
        print(
            f"Ошибочный код запроса {exc.response.status_code} при выполнени запроса {exc.request.url!r}.")
        print("P.S. Проверьте задан ли токекн")
    except httpx.RequestError as exc:
        print(f"Произошла ошибка при запросе {exc.request.url!r}.")


def menu_sql():
    flag_sql_chenged = False
    while(True):
        print("__________CONFIG MENU__________")
        print("1) Просмотр таблицы")
        print("2) Изменить базовый URL")
        print("3) Задать API ключ")
        print("4) Задать язык вывода ru/en")
        print("5) Выйти в главное меню")
        menu_config_num = int(
            input("Введите номер команды из меню: "))
        if menu_config_num == 1:
            cursor.execute("SELECT * FROM config")
            result_view = cursor.fetchall()
            for item in result_view:
                print(item[0], "\t", item[1])
        elif menu_config_num == 2:
            url_new = input("Введите новый URL: ")
            cursor.execute(
                f"UPDATE config SET Value = '{url_new}' WHERE ID = 'URL';")
            flag_sql_chenged = True
        elif menu_config_num == 3:
            key_new = input("Введите новый API ключ: ")
            cursor.execute(
                f"UPDATE config SET Value = '{key_new}' WHERE ID = 'API key';")
            flag_sql_chenged = True
        elif menu_config_num == 4:
            lang_new = input("Задайте язык вывода ru/en: ")
            if lang_new == "ru" or lang_new == "en":
                cursor.execute(
                    f"UPDATE config SET Value = '{lang_new}' WHERE ID = 'Language';")
                flag_sql_chenged = True
            else:
                print("Введен неверный язык")
        elif menu_config_num == 5:
            if flag_sql_chenged:
                save_flag = input(
                    "Сохранить изменения в таблицу config (y/n)? ")
                if save_flag == "y":
                    sqlite_connection.commit()
                elif save_flag == "n":
                    break
                else:
                    print("Введен неверный знак")
            break
        else:
            print("Указанной команды нет в меню")
            continue


menu()

cursor.close()
if (sqlite_connection):
    sqlite_connection.close()
    print("Соединение с SQLite закрыто")
