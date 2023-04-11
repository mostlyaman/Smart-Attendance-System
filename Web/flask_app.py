from flask import Flask
from flask import request

import json

import mysql.connector as db

app = Flask(__name__)

@app.route('/api/v1/test', methods=['GET'])
def test_server():
    return "Server is running."


@app.route('/api/v1/face_recognition', methods=['GET'])
def face_recognition():
    try:
        return json.dumps({"status":"ok"}), 200
    except Exception as e:
        return json.dumps({"status":"error", "message":"Something went wrong."}), 500
