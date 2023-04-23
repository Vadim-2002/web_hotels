# Подключаем приложение Flask из пакета labapp (см. модуль инициализации __init__.py)
from labapp import app

"""
    Этот модуль запускает web-приложение
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
