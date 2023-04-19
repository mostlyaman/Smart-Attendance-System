import mysql.connector as db
from mysql.connector.errors import Error as dbError
from mysql.connector import errorcode
import json
import dotenv
import os

dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'))

host = os.getenv('DB_URL')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')

connectUsers = db.connect(host=host, user=user, password=password)

def connectDB():
    global connectUsers
    try:
        connectUsers = db.connect(host = host, user = user, password = password)
    except dbError as err:
        connectUsers = {}
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            connectUsers['ERROR'] = "DB_ACCESS_DENIED"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            connectUsers['ERROR'] = "BAD_DATABASE"
        else:
            connectUsers['ERROR'] = str(err)

def getCursor():
    try:
        db_cursor = connectUsers.cursor()
    except dbError:
        connectDB()
        db_cursor = connectUsers.cursor()
    finally:
        if isinstance(connectUsers, dict):
            return ['ERROR', json.dumps({'status':'ERROR', 'ERROR': connectUsers['ERROR']})]
        else:
            return ['OK', db_cursor]

def run_query(query, api='', data=''):
    status, cursor = getCursor()
    if status == 'OK':
        try:
            cursor.execute(query)
            res = list(cursor)
            connectUsers.commit()
            return res, 200
        except dbError as err:
            cursor.execute(f'insert into errors(api, params, error) values({api}, {str(data)}, {str(err)})')
            connectUsers.commit()
            return json.dumps({"status":"error", "message": "Something went wrong.", "error": f"{str(err)}"}), 500
            
    else:
        return cursor, 500


def create_attendance_table(user_name, course_name):
    table_name = "att_"
    for i in user_name:
        if i.isalpha():
            table_name += i
    
    table_name += "_"

    for i in course_name:
        if i.isalpha():
            table_name += i
    
    query = f'create table if not exists {table_name}(id int PRIMARY_KEY AUTO_INCREMENT, att_datetime datetime NOT NULL, user int NOT NULL, foreign key (user) references users(id))'
    res, code = run_query(query)
    
