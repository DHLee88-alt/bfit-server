from flask import Flask, request, jsonify, render_template, redirect, url_for
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

# ✅ 루트 페이지 (서버 작동 확인용)
@app.route('/')
def home():
    return '✅ 서버가 정상적으로 실행 중입니다!'

# ✅ 회원가입
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
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

# ✅ 로그인 처리
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    user_pw = data.get('pw')

    if not user_id or not user_pw:
        return jsonify({"success": False, "message": "아이디와 비밀번호를 입력하세요."})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT password FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == user_pw:
        return jsonify({"success": True, "message": "로그인 성공!"})
    else:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호가 일치하지 않습니다."})

# ✅ 로그인 후 이동할 index.html
@app.route('/index.html')
def index_page():
    return render_template('index.html')

# ✅ 운동 선택 페이지 exercise-selection.html
@app.route('/exercise-selection.html')
def exercise_selection_page():
    return render_template('exercise-selection.html')

# ✅ 홈 이동용 home.html
@app.route('/home.html')
def home_page():
    return render_template('home.html')

# ✅ 회원가입 폼 signup.html
@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

# ✅ 로그인 폼 login.html
@app.route('/login.html')
def login_page():
    return render_template('login.html')

# ✅ 운동 화면 exercise.html
@app.route('/exercise.html')
def exercise_page():
    return render_template('exercise.html')

# ✅ 운동 기록 화면 stats.html
@app.route('/stats.html')
def stats_page():
    return render_template('stats.html')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
