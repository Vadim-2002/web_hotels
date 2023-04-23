from abc import ABC, abstractmethod
from typing import Optional

from .connector import StoreConnector
from .mysqlconnector import MySQLStoreConnector
from .sqliteconnector import SQLiteStoreConnector

"""
    В данном модуле реализуется фабрика объектов-соединений (коннекторов) к хранилищу данных (БД).
    Данная фабрика позволяет автоматически инициализировать необходимый тип подключения к БД в 
    зависимости от формата строки подключения (аргумент datastore)
"""


class StoreConnectorFactory(ABC):
    def __init__(self):
        self.instance: Optional[StoreConnector] = None

    @abstractmethod
    def get_connector(self, datastore: str) -> Optional[StoreConnector]:
        """
            get_connector - параметризированный фабричный метод
            для получения объектов соединения с различными типами
            SQL БД (в зависимости от формата строки подключения).

            Допустимые форматы строк подключения datastore:

            SQLite: "sqlite:///test.db" (файл БД в локальной папке приложения)
                    "sqlite:///C:\\databases\\test.db" (полный путь до файла БД)

            MySQL: "pymysql://usr:qwerty@192.168.56.104/testdb"
        """
        pass


class SQLStoreConnectorFactory(StoreConnectorFactory):
    def get_connector(self, datastore):
        if datastore.startswith("sqlite:///"):
            self.instance = SQLiteStoreConnector(datastore)
            if self.instance.connect():
                return self.instance
        elif datastore.startswith("pymysql://"):
            self.instance = MySQLStoreConnector(datastore)
            if self.instance.connect():
                return self.instance
        return None
