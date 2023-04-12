from flask import Flask
from flask import request
from model import face_search
import cv2
import numpy as np

import json

import mysql.connector as db

app = Flask(__name__)

@app.route('/api/v1/test', methods=['GET'])
def test_server():
    return "Server is running."


@app.route('/api/v1/face_recognition', methods=['POST'])
def face_recognition():
    try:
        if 'image' in request.files:
            image = request.files['image']
            frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
            return json.dumps({"status": "ok", "result": face_search(frame)})
        else:
            return json.dumps({"status":"error", "message": "No Image Selected."}), 400
    except Exception as e:
        return json.dumps({"status":"error", "message":"Something went wrong.", "error": str(e)}), 500
