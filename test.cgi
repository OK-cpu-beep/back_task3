#!/usr/bin/python3

import os
import sys
import re
import logging
from datetime import datetime
from urllib.parse import parse_qs

# По какой-то причине test.cgi не хочет импортировать database.propert
# поэтому я просто запихнул класс сюда

class SQL_con():
    config = {
        'host': 'localhost',       # Адрес сервера БД
        'user': 'u68835',          # Имя пользователя
        'password': '2995354',     # Пароль
        'database': 'u68835',      # Название БД
        'ssl_disabled': True
    }
    @staticmethod
    def post_user(data):

        conn = sq_con.connect(**SQL_con.config)
        curr = conn.cursor()
        curr.execute(f'''
            INSERT INTO users (fio, phone, email, birth_date, gender, bio)
            VALUES ('{data["fio"]}','{data["phone"]}','{data["email"]}',
            '{data["birth_date"]}' , {data["gender"]}, '{data["bio"]}');
            ''')
        conn.commit()
        conn.close()

    @staticmethod    
    def get_user_id(data):
        conn = sq_con.connect(**SQL_con.config)
        curr = conn.cursor()
        curr.execute(f'''
            SELECT * FROM users WHERE (fio='{data["fio"]}' AND phone = '{data["phone"]}'
            AND email = '{data["email"]}' AND birth_date = '{data["birth_date"]}'
            AND gender = {data["gender"]} AND bio = '{data["bio"]}');
            ''')
        user = curr.fetchall()
        conn.close()
        if(len(user)!=0):
            return user[0][0]
        return -1
    @staticmethod
    def post_language(user_id, data):
        conn = sq_con.connect(**SQL_con.config)
        curr = conn.cursor()
        for i in data:
            curr.execute(f'''
                INSERT INTO users_languages VALUES ({user_id}, {i});
                ''')
        conn.commit()
        conn.close()
#os.environ получает инфу о переменных окружениях
method = os.environ.get('REQUEST_METHOD', '')
sys.stdout.reconfigure(encoding='utf-8')
try:
    if method=="POST":
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        post_data = sys.stdin.read(content_length)
        new_data = parse_qs(post_data)
        
        #Валидация
        errors = {}

        #Имя
        try:
            fio = new_data['field-fio'][0]
            if fio == '':
                errors['fio'] = "ФИО обязательно для заполнения"
            elif not re.match(r'^[A-Za-zА-Яа-яёЁ\s-]{1,150}$', fio):
                errors['fio'] = 'ФИО должно содержать только буквы, пробелы и дефисы (макс. 150 символов)'
        except:
            errors['fio'] = "Поле Фио не может быть пустым"

        #email
        try:
            email = new_data['field-email'][0]
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                errors['email'] = 'Введите корректный email'
        except:
            errors['email'] = "Поле email не может быть пустым"


        #ЯП

        try:
            languages = new_data["languages"]
        except:
            errors['languages'] = 'Выберете хотя бы 1 язык программирования'

        #Дата рождения

        try:
            birth_date = datetime.strptime(new_data['field-birthday'][0], '%Y-%m-%d').date()
            print(birth_date)
            if birth_date > datetime.now().date():
                errors['birth_date'] = 'Дата рождения не может быть в будущем'
        except ValueError:
            errors['birth_date'] = 'Некорректный формат даты. Используйте ГГГГ-ММ-ДД'
        except KeyError:
            errors['birth_date'] = 'Поле даты не может быть пустым'

        #телефон
        try:
            phone = new_data['field-tel'][0]
            cleaned_phone = re.sub(r'[^\d]', '', phone)
            # Проверяем основные форматы для России
            if not re.fullmatch(r'^(\+7|8)\d{10}$', cleaned_phone):
                errors['phone'] = "Введите корректный номер телефона(Россия)"
        except:
            errors["phone"] = "Поле email не может быть пустым"


        #Cогласие
        if not new_data["check-1"]:
            errors['contract_agreed'] = "Ознакомьтесь с контрактом для отправки"

        #Пол
        gender = new_data["radio-group-1"][0]

        #Биография
        try:
            bio = new_data["bio"][0]
        except:
            bio = ""

        if errors:
            error_html = '''
                        <!DOCTYPE html>
        <head>
            <meta charset="UTF-8">
            <link href="static/styles.css" rel="stylesheet" type="text/css"/>
            <title> Дом Баззиков </title>
        </head>
        <header>
                <div class = "title_block">
                    <a href="/">
                        <img class = "img-header" src="static/hyperbuzz_pin.png"/>
                    </a>
                    <h1> ДОМ БАЗЗИЛ </h1>
                </div>
                <nav>
                    <div class = "a-1"><a href = "#">О сайте</a></div>
                    <div class = "a-2"><a href = "#">Добавить статью</a></div>
                    <div class = "a-3"> <a href = "#">Тех поддежка</a></div>
                </nav>
            </header>
            <div class="main_block">
            <form id = "tablo">
            <label><b>ФОРМА НЕ ОТПРАВЛЕНА</b></label><br>
            '''
            for field, message in errors.items():
                error_html += f"<label>{message}</label><br>"

            error_html +='''
                        </form>
                        </div>
        <body>
            <footer>
                <p> Ковязин Кирилл (c)</p>
            </footer>
        </body> 
            '''
            print("Status: 400 Bad Request\r")
            print("Content-Type: text/html; charset=UTF-8\r\n\r\n")
            print(error_html)
        else:
            #Переделываем данные
            new_data = {
                    "fio": fio,
                    "phone": phone,
                    "email": email,
                    "birth_date": birth_date,
                    "gender": gender,
                    "bio": bio,
                }
            #Закидываем данные в бд
            user_id = SQL_con().get_user_id(new_data)
            if (user_id==-1):
                SQL_con().post_user(new_data)
                SQL_con().post_language(SQL_con().get_user_id(new_data), languages)
                phrase = "Форма успешно отправлена"
            else:
                phrase = "Вы уже отправляли форму"

            print("Status: 200 OK\r")
            print("Content-Type: text/html\r\n\r\n")
            
            Success_html = f'''
    <head>
    <meta charset="UTF-8">
    <link href="static/styles.css" rel="stylesheet" type="text/css"/>
    <title> Дом Баззиков </title>
    </head>
    <body>
    <header>
    <div class = "title_block">
        <a href="/">
            <img class = "img-header" src="static/hyperbuzz_pin.png"/>
        </a>
        <h1> ДОМ БАЗЗИЛ </h1>
    </div>
    <nav>
        <div class = "a-1"><a href = "#">О сайте</a></div>
        <div class = "a-2"><a href = "#">Добавить статью</a></div>
        <div class = "a-3"> <a href = "#">Тех поддежка</a></div>
    </nav>
    </header>
    <div class="main_block">
    <form id = "tablo">
    <label>{phrase}</label>
    </form>
    </div>
    <footer>
    <p> Ковязин Кирилл (c)</p>
    </footer>
    </body> 
            '''
            print(Success_html)
    else:
        print("Status: 404 Not Found\r")
        print("Content-Type: text/html\r\n\r\n")
        print("Wrong url (Change url to '/' pls)")
except Exception as e:
    error_msg = f"Critical error: {str(e)}"
    file = open("logs.txt", "w")
    file.write(error_msg)
    file.close()
    print("Status: 500 Internal Server Error\r")
    print("Content-Type: text/html\r\n\r\n")
    print("<h1>500 Server Error</h1>")
    print("<p>Произошла ошибка. Администратор уведомлен.</p>")
