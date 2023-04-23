from typing import List

from config import DB_URL                       # параметры подключения к БД из модуля конфигурации config.py
from config import DB_URL_2
from .repository import sql_api                 # подключаем API для работы с БД
from .repository.connectorfactory import SQLStoreConnectorFactory

"""
    В данном модуле реализуются бизнес-логика обработки клиентских запросов.
    Здесь также могут применяться SQL-методы, представленные в модуле repository.sql_api
"""

# Структура основного навигационнго меню (<nav>) веб-приложения,
# оформленное в виде объекта dict
navmenu = [
    {
        'name': 'Главная',
        'addr': '/'
    },
    {
        'name': 'О проекте',
        'addr': '/about'
    },
    {
        'name': 'Контакты',
        'addr': '/contact'
    },
]


def get_source_files_list(city_name: str = "", value_sort: str = "", page_num: int = 0) -> List[tuple]:
    """ Получаем список обработанных файлов """
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.select_all_from_source_files(db_connector, city_name, value_sort, page_num)  # получаем список всех обработанных файлов
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def get_source_files_list_city() -> List[tuple]:
    """ Получаем список обработанных файлов """
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.select_city_from_source_files(db_connector)  # получаем список всех обработанных файлов
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def get_sorting_files(str_of_columns: str, value_cat: int = None, value_sort: str = "", str_join: str = '', num_page: int = 0) -> List[tuple]:
    """ Получаем список обработанных файлов """
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.sorting_by_price(db_connector, str_of_columns, value_cat, value_sort, str_join, num_page)  # получаем список всех обработанных файлов
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def get_processed_data(source_file: int, page_num: int = None) -> List[tuple]:
    """ Получаем обработанные данные из основной таблицы """
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL)
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.select_rows_from_processed_data(db_connector, source_file=source_file, offset=page_num)
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def add_new_user(name: str, email: str, password: str):
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL_2)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.insert_into_client_base(db_connector, name, email, password)
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def get_data_user(email: str) -> List[tuple]:
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL_2)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.get_user_login(db_connector, email)
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result


def delete_user(email: str) -> List[tuple]:
    db_connector = SQLStoreConnectorFactory().get_connector(DB_URL_2)  # инициализируем соединение
    db_connector.start_transaction()  # начинаем выполнение запросов (открываем транзакцию)
    result = sql_api.delete_user(db_connector, email)
    db_connector.end_transaction()  # завершаем выполнение запросов (закрываем транзакцию)
    db_connector.close()
    return result
