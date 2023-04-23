from abc import ABC, abstractmethod
from typing import Optional, Any

"""
    В данном модуле реализуется родительский класс, определяющий  интерфейс 
    для реализации соединений (классов-коннекторов) для различных баз данных (БД).
    
    ВАЖНО! Если реализация классов-потомков занимает большое 
    количество строк, то необходимо оформлять каждый класс в отдельном файле
    
    Все методы, помеченные декоратором @abstractmethod, ОБЯЗАТЕЛЬНЫ для переопределения
"""


class StoreConnector(ABC):
    """ Родительский класс для коннекторов БД """
    def __init__(self, datastore: str):
        # общие атрибуты
        self._datastore = datastore   # путь к хранилищу данных (БД)
        self.connection = None       # данный атрибут хранит инициализированное в методе connect() подключение к БД

    @abstractmethod
    def connect(self) -> bool:
        """ Инициализация соединение с БД """
        pass

    @abstractmethod
    def execute(self, query: str) -> Optional[Any]:
        """ Выполнение SQL-запроса """
        pass

    @abstractmethod
    def start_transaction(self) -> None:
        """ Метод, подготавливающий коннектор к выполнению запросов в БД (начало транзакции) """
        pass

    @abstractmethod
    def end_transaction(self) -> None:
        """ Метод, завершающий выполнение запросов в БД (завершение транзакции) """
        pass

    @abstractmethod
    def close(self) -> None:
        """ Завершение соединения с БД """
        pass

