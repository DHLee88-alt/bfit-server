from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = 'users.db'

# DB 초기화 (users 테이블 만들기)
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    user_pw = data.get('pw')

    if not user_id or not user_pw:
        return jsonify({"success": False, "message": "아이디와 비밀번호가 필요합니다."})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 아이디 중복 체크
    c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    existing_user = c.fetchone()

    if existing_user:
        conn.close()
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})

    # 새 유저 저장
    c.execute('INSERT INTO users (id, password) VALUES (?, ?)', (user_id, user_pw))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
