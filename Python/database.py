import mysql.connector as sq_con
from datetime import datetime

class SQL_con():
    config = {
        'host': 'localhost',      # Адрес сервера БД
        'user': 'root',           # Имя пользователя
        'password': '1234',       # Пароль
        'database': 'web_back'    # Название БД
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
        

        



