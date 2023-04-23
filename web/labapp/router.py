# Подключаем объект приложения Flask из __init__.py
from labapp import app
# Подключаем библиотеку для "рендеринга" html-шаблонов из папки templates
from flask import render_template, make_response, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import labapp.webservice as webservice   # подключаем модуль с реализацией бизнес-логики обработки запросов
import smtplib

"""
    Модуль регистрации обработчиков маршрутов, т.е. здесь реализуется обработка запросов
    при переходе пользователя на определенные адреса веб-приложения
"""

value_sort = ""
value_city = ""
num_page = 0

col_name_pay = []
name_user_lk = "Вход"
email_user_lk = ""
previous_page = ""
room_inform = []


def soring_by_price():
    global value_sort

    if request.form.get('sort') == 'name_decrease':
        value_sort = "ORDER BY name DESC"
    elif request.form.get('sort') == 'name_increase':
        value_sort = "ORDER BY name  ASC"
    elif request.form.get('sort') == 'null':
        value_sort = "ORDER BY id ASC"


def selection_city(city):
    global value_city
    value_city = ""

    if request.form.get('but_city') == 'Выбрать':
        for i in range(0, len(city)):
            if request.form.get(f'{city[i]}') == city[i]:
                value_city += f"\"{request.form.get(f'{city[i]}')}\" OR city = "


def changing_the_page():
    global num_page

    if request.form.get('page_last') == 'Предыдущая страница':
        if num_page > 0:
            num_page -= 50

    if request.form.get('page_next') == 'Следующая страница':
        if num_page < 150:
            num_page += 50


def registering_new_user():
    """Запись данных нового пользователя в БД"""
    global name_user_lk
    global email_user_lk

    name = request.form.get('name_user')
    email = request.form.get('email')
    password = request.form.get('pswd')
    hash_pswd = generate_password_hash(password)
    if webservice.add_new_user(name, email, hash_pswd) == None:
        return False
    name_user_lk = name
    email_user_lk = email
    subject = "Регистрация"
    message = "Здравствйте! Благодарим Вас за регистрацию на нашем сайте! Надеюсь, мы поможем подобрать Вам нажную гостиницу и оформить в ней бронь!"
    sending_message_user(f"{email}", subject, message)
    return True


def user_authentication():
    """Вход пользователя на сайт"""
    global name_user_lk
    global email_user_lk

    email = request.form.get('email')
    password = request.form.get('pswd')
    data_user = webservice.get_data_user(email)
    save_name = (data_user[0])[0]
    save_password = (data_user[0])[1]
    save_email = (data_user[0])[2]

    if email == save_email:
        if check_password_hash(save_password, password):
            name_user_lk = save_name
            email_user_lk = save_email
            return True
    return False


def sending_message_user(to_addr, subject, text, encode='utf-8'):
    from_addr = "ufa.gentlemen@mail.ru"
    passwd = "3nZKWwtkS8vsi3C6qHqr"
    server = "smtp.mail.ru"
    port = 587
    charset = f'Content-Type: text/plain; charset={encode}'
    mime = 'MIME-Version: 1.0'
    body = "\r\n".join((f"From: {from_addr}", f"To: {to_addr}",
                        f"Subject: {subject}", mime, charset, "", text))

    try:
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(from_addr, passwd)
        smtp.sendmail(from_addr, to_addr, body.encode(encode))
        smtp.quit()

    except smtplib.SMTPException as err:
        raise err


@app.route('/index', methods=['GET', 'POST'])
def index():
    if name_user_lk == "Вход":
        return registration()

    global previous_page
    previous_page = "/index"

    """ Обработка запроса к индексной странице """
    processed_files = webservice.get_source_files_list("", value_sort, num_page)

    tmp = set(webservice.get_source_files_list_city())
    city = []
    for i in range(0, len(tmp)):
        city.append((list(tmp)[i])[0])

    if request.method == 'POST':
        soring_by_price()
        changing_the_page()
        selection_city(city)

        processed_files = webservice.get_source_files_list(value_city[:-10], value_sort, num_page)

    return render_template('index.html',
                           title='Home',
                           navmenu=webservice.navmenu,
                           processed_files=processed_files,
                           num_page=num_page,
                           name_user_lk=name_user_lk,
                           list_city=city)


@app.route('/contact', methods=['GET'])
def contact():
    """ Обработка запроса к странице contact.html """
    global previous_page
    previous_page = "/contact"

    return render_template('contacts.html',
                           title='Contacts',
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu)


@app.route('/about', methods=['GET'])
def about():
    """ Обработка запроса к странице about.html """
    global previous_page
    previous_page = "/about"

    return render_template('about.html',
                           title='About project',
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu)


@app.route('/regist', methods=['GET', 'POST'])
def registration():
    global name_user_lk
    global previous_page
    previous_page = "/regist"

    if name_user_lk != "Вход":
        return personal()

    if request.method == 'POST':
        if request.form.get('new_user') == 'True':
            if registering_new_user():
                return registration()
            else:
                message = "Пользователь с такой почтой уже существует!"
                return acc_errors(message)

        if request.form.get('input_user') == 'True':
            if user_authentication():
                return registration()
            else:
                message = "Неверный пароль!"
                return acc_errors(message)

    return render_template('registration.html',
                           title='Login',
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu)


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    global name_user_lk
    global email_user_lk
    global previous_page
    previous_page = "/personal"

    if request.method == 'POST':
        if request.form.get('exit') == 'True':
            name_user_lk = "Вход"
            email_user_lk = ""
            return registration()

        if request.form.get('delete') == 'True':
            webservice.delete_user(email_user_lk)
            name_user_lk = "Вход"
            email_user_lk = ""
            return registration()

    return render_template('lk.html',
                           title='Personal account',
                           name_user_lk=name_user_lk,
                           email_user_lk=email_user_lk,
                           navmenu=webservice.navmenu)


@app.route('/acc_errors', methods=['GET', 'POST'])
def acc_errors(message):
    if request.method == 'POST':
        if request.form.get('exit') == 'True':
            return registration()

    return render_template('acc_errors.html',
                           title='Hotels',
                           name_user_lk=name_user_lk,
                           message=message,
                           navmenu=webservice.navmenu)


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if name_user_lk == "Вход":
        return registration()

    room_inform.append(col_name_pay[0])
    room_inform.append(col_name_pay[1])
    room_inform.append(col_name_pay[2])

    if request.method == 'POST':
        if request.form.get('btn_ofrm_stand') == 'True':
            room_inform.append("Стандартный")
            room_inform.append(col_name_pay[6])

        if request.form.get('btn_ofrm_luks') == 'True':
            room_inform.append("Люкс")
            room_inform.append(col_name_pay[7])

        if request.form.get('btn_ofrm_vip') == 'True':
            room_inform.append("Президентский")
            room_inform.append(col_name_pay[8])

        if request.form.get('btn_ofrm') == 'True':
            subject = "Чек"
            message = f"Поздравляем! Вы оформили бронь в \"{room_inform[0]}\", регион: {room_inform[1]}, город: {room_inform[2]}. Тип номера: \"{room_inform[3]}\", цена: {room_inform[4]} рублей"
            sending_message_user(email_user_lk, subject, message)
            room_inform.clear()

        if request.form.get('back') == 'True':
            return index()

    return render_template('pay.html',
                           title='Pay',
                           col_name_pay=room_inform,
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu,
                           prev_page=previous_page)


@app.route('/room', methods=['GET', 'POST'])
def room_design():
    if name_user_lk == "Вход":
        return registration()

    global col_name_pay
    col_name_pay = []

    name_hotel = ""
    price_stand = 0
    count_stand = 0
    price_luks = 0
    count_luks = 0
    price_vip = 0
    count_vip = 0

    if request.method == 'POST':
        name_hotel = request.form.get('col_1')
        price_stand = request.form.get('col_7')
        count_stand = request.form.get('col_4')
        price_luks = request.form.get('col_8')
        count_luks = request.form.get('col_5')
        price_vip = request.form.get('col_9')
        count_vip = request.form.get('col_6')

        col_name_pay.append(name_hotel)
        col_name_pay.append(request.form.get('col_2'))
        col_name_pay.append(request.form.get('col_3'))
        col_name_pay.append(count_stand)
        col_name_pay.append(count_luks)
        col_name_pay.append(count_vip)
        col_name_pay.append(price_stand)
        col_name_pay.append(price_luks)
        col_name_pay.append(price_vip)

        if request.form.get('back') == 'True':
            return index()

    return render_template('room_design.html',
                           title='Room design',
                           col_name_pay=col_name_pay,
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu,
                           name_hotel=name_hotel,
                           price_stand=price_stand,
                           count_stand=count_stand,
                           price_luks=price_luks,
                           count_luks=count_luks,
                           price_vip=price_vip,
                           count_vip=count_vip,
                           prev_page=previous_page)


@app.route('/', methods=['GET'])
def homepage():
    return render_template('main.html',
                           title='Hotels',
                           name_user_lk=name_user_lk,
                           navmenu=webservice.navmenu)


@app.route('/notfound', methods=['GET'])
def not_found_html():
    """ Возврат html-страницы с кодом 404 (Не найдено) """
    return render_template('404.html', title='404', err={'error': 'Not found', 'code': 404})


def bad_request():
    """ Формирование json-ответа с ошибкой 400 протокола HTTP (Неверный запрос) """
    return make_response(jsonify({'message': 'Bad request !'}), 400)
