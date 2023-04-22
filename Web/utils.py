import mysql.connector as db
from mysql.connector.errors import Error as dbError
from mysql.connector import errorcode
import json
import dotenv
import os
import sys
import traceback
import cv2
import face_recognition
import numpy as np

dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'))

host = os.getenv('DB_URL')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')


connectUsers = db.connect(host=host, user=user, password=password, database=db_name)

def connectDB():
    global connectUsers
    try:
        connectUsers = db.connect(host = host, user = user, password = password, database=db_name)
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
            cursor.execute(f'insert into {db_name}.errors(api, params, error) values({api}, {str(data)}, {str(err)})')
            connectUsers.commit()
            return json.dumps({"status":"error", "message": "Something went wrong.", "error": f"{str(err)}", "traceback":traceback.format_exc()}), 500
            
    else:
        return cursor, 500


def create_attendance_table(user_name, course_name):
    table_name = generate_table_name(user_name, course_name)
    query = f'create table if not exists {db_name}.{table_name}(id int PRIMARY KEY AUTO_INCREMENT, att_datetime datetime DEFAULT NULL, user int NOT NULL, foreign key (user) references users(id))'
    res, code = run_query(query)
    if code != 200:
        return res, code
    
    return table_name, code

def generate_table_name(user_name, course_name):
    table_name = "att_"
    for i in user_name:
        if i.isalnum():
            table_name += i
    
    table_name += "_"

    for i in course_name:
        if i.isalnum():
            table_name += i

    return table_name


def encode_face(image, user_id):
    frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    enc = face_recognition.face_encodings(frame)[0]
    enc = json.dumps(enc.tolist())

    query = f'update {db_name}.users set image_data = "{enc}" where id={user_id}'
    res, code = run_query(query)
    return res, code
