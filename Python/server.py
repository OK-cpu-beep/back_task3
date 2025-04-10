from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from database import SQL_con
import re
import os
from datetime import datetime

class HttpProcessor(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            try:
                with open("index.html", "rb") as f:
                    html_content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html_content)
            except FileNotFoundError:
                self.send_error(404, "File Not Found", "index.html не найден")
            except Exception as e:
                self.send_error(500, "Server Error", str(e))
        elif self.path[:8] == "/static/":
            try:
                self.send_response(200) 
                if (self.path.endswith(".css")):
                    self.send_header("Content-type", "text/css")
                if (self.path.endswith(".png")):
                    self.send_header("Content-type", "image/png")
                self.end_headers()
                with open(self.path[1:], "rb") as f:
                    self.wfile.write(f.read())
            except:
                self.send_error(404, "Static file not found")
        else:
            print(self.path[:8])
            self.send_error(404, "Wrong url (Change url to '/' pls)")
            
    def do_POST(self):
        print(self.path)
        if self.path == '/submit':
            # Парсим данные
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            new_data = parse_qs(post_data)
            print(new_data)

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
                self.send_response(400)  # Bad Request
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(error_html.encode('utf-8'))
                return
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

                    '''
                    SELECT * FROM users WHERE (fio='{data["fio"]}' AND phone = '{data["phone"]}'
            AND email = '{data["email"]}' AND birth_date = '{data["birth_date"]}'
            AND gender = {data["gender"]} AND bio = '{data["bio"]}');
                    '''
                    SQL_con().post_user(new_data)
                    SQL_con().post_language(SQL_con().get_user_id(new_data), languages)
                    phrase = "Форма успешно отправлена"
                else:
                    phrase = "Вы уже отправляли форму"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                Success_html = f'''
                <!DOCTYPE html>
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
                self.wfile.write(Success_html.encode('utf-8'))
            print("nobug")
            '''
            {'field-fio': ['Иванов Иван Иванович'], 'field-tel': ['88005553535'], 'field-email': ['test@gmail.com'], 'radio-group-1': ['Значение1'], 'languages': ['Pascal', 'C', 'C++'], 'biography': ['фывфывыв'], 'check-1': ['on']}
            '''
        else:
            self.send_error(404, "Wrong url (Change url to '/' pls)")


        

serv = HTTPServer(("localhost", 8888), HttpProcessor)
serv.serve_forever() 

#Для работы с MySQL используйте mysql.connector и подготовленные запросы (prepared statements).
