from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = 'users.db'

# DB 초기화
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

# 루트 페이지 (홈 화면)
@app.route('/')
def home():
    return render_template('home.html')  # 템플릿 폴더의 home.html을 렌더링

# 회원가입 라우트
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')  # GET 요청 시 signup.html 보여줌

    data = request.json or request.form
    user_id = data.get('id')
    user_pw = data.get('pw')

    if not user_id or not user_pw:
        return jsonify({"success": False, "message": "아이디와 비밀번호가 필요합니다."})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    existing_user = c.fetchone()

    if existing_user:
        conn.close()
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})

    c.execute('INSERT INTO users (id, password) VALUES (?, ?)', (user_id, user_pw))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "회원가입 성공!"})

# 통계 페이지 (운동 기록 확인)
@app.route('/stats')
def stats():
    return render_template('stats.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
