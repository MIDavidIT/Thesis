from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import json
import os
import RPi.GPIO as GPIO

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fingerprint_id INTEGER NOT NULL,
            face_image_path TEXT NOT NULL,
            voice_model_path TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route('/command', methods=['GET'])
def handle_command():
    cmd = request.args.get("cmd")
    username = request.args.get("username")

    try:
        if cmd == "capture_fingerprint":
            result = subprocess.run(["python3", "save_fingerprint.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            last_line = output.strip().split('\n')[-1]
            return jsonify(json.loads(last_line))

        elif cmd == "capture_face":
            result = subprocess.run(["python3", "save_face.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            last_line = output.strip().split('\n')[-1]
            return jsonify(json.loads(last_line))

        elif cmd == "capture_voice":
            if not username:
                return jsonify({"status": "error", "message": "Hianyzo felhasznalonev"}), 400
            result = subprocess.run(["python3", "save_voice.py", username], stdout=subprocess.PIPE)
            return jsonify(json.loads(result.stdout.decode("utf-8")))

        elif cmd == "verify_fingerprint":
            # JAVÍTVA: levettük a stderr=subprocess.PIPE részt, hogy a logok megjelenjenek!
            result = subprocess.run(["python3", "verify_fingerprint.py"], stdout=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            return jsonify(json.loads(output.strip().split('\n')[-1]))

        elif cmd == "verify_facepicture":
            if not username: return jsonify({"status": "error", "message": "Hianyzo felhasznalonev"}), 400
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT face_image_path FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
            if row:
                result = subprocess.run(["python3", "verify_face.py", row[0]], stdout=subprocess.PIPE)
                return jsonify(json.loads(result.stdout.decode("utf-8")))
            return jsonify({"status": "error", "message": "Nincs regisztralt arc"}), 404

        elif cmd == "verify_voice":
            if not username: return jsonify({"status": "error", "message": "Hianyzo felhasznalonev"}), 400
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT voice_model_path FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
            if row and row[0]:
                result = subprocess.run(["python3", "verify_voice.py", row[0]], stdout=subprocess.PIPE)
                return jsonify(json.loads(result.stdout.decode("utf-8")))
            return jsonify({"status": "error", "message": "Nincs regisztralt hangminta"}), 404
        
        elif cmd == "unlock":
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.OUT)
            GPIO.output(18, 1)
            print("Zár kinyitva")
            return jsonify({"status": "success", "message": "Zar sikeresen kinyitva!"}), 200
        
        elif cmd == "lock":
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.OUT)
            GPIO.output(18, 0)
            print("Zár bezárva")
            return jsonify({"status": "success", "message": "Zar sikeresen bezarva!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"DEBUG: Beérkező adatok -> {data}")

        username = data.get('username')
        password = data.get('password')
        f_id = data.get('fingerprint', {}).get('id')
        face_p = data.get('face_image', {}).get('path')
        voice_p = data.get('voice_model', {}).get('path')

        if not all([username, password, f_id, face_p, voice_p]):
            return jsonify({"error": "Hianyzo biometrikus adatok!"}), 400

        hashed_pw = generate_password_hash(password)
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password, fingerprint_id, face_image_path, voice_model_path) 
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_pw, f_id, face_p, voice_p))
            conn.commit()
        return jsonify({'message': 'Sikeres regisztracio'}), 201
    except Exception as e:
        print(f"HIBA: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user, pw = data.get("username"), data.get("password")
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (user,))
        res = cursor.fetchone()
        if res and check_password_hash(res[0], pw):
            return jsonify({"message": "Sikeres bejelentkezes"}), 200
    return jsonify({"error": "Hibás adatok"}), 401

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, ssl_context=('certfile.crt', 'keyfile.key'))