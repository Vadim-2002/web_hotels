from flask import Flask


# Регистрируем приложение Flask
app = Flask(__name__)


# Подключаем маршрутизатор HTTP запросов
from labapp import router
