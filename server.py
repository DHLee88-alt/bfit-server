from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'super-secret-key'  # 세션을 위한 시크릿 키

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

# 홈 페이지 (로그인 여부에 따라 표시 변경 가능)
@app.route('/')
def home():
    user = session.get('user')
    return render_template('home.html', user=user)

# 회원가입 페이지
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json or request.form
        user_id = data.get('id')
        user_pw = data.get('pw')

        if not user_id or not user_pw:
            return jsonify({"success": False, "message": "아이디와 비밀번호를 입력하세요."})

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        existing = c.fetchone()
        if existing:
            conn.close()
            return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})

        c.execute('INSERT INTO users (id, password) VALUES (?, ?)', (user_id, user_pw))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "회원가입 완료!"})

    return render_template('signup.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id')
        user_pw = request.form.get('pw')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()

        if user and user[0] == user_pw:
            session['user'] = user_id
            return redirect(url_for('home'))
        else:
            return '❌ 로그인 실패. 아이디 또는 비밀번호가 잘못되었습니다.'

    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
