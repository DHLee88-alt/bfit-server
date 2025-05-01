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
                password TEXT NOT NULL,
                exercise_count INTEGER DEFAULT 0,
                last_exercise_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

# 루트
@app.route('/')
def index():
    return render_template('index.html')

# 회원가입
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

# 로그인
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

# 운동 기록 저장
@app.route('/save-exercise', methods=['POST'])
def save_exercise():
    data = request.json
    user_id = data.get('id')
    today = data.get('date')

    if not user_id or not today:
        return jsonify({"success": False, "message": "필수 데이터가 없습니다."})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET exercise_count = exercise_count + 3, last_exercise_date = ?
        WHERE id = ?
    ''', (today, user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "운동 기록 저장 완료!"})

# 운동 기록 가져오기
@app.route('/get-exercise-data', methods=['GET'])
def get_exercise_data():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"success": False, "message": "아이디 없음"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT exercise_count, last_exercise_date FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return jsonify({"success": True, "total_count": result[0], "last_date": result[1]})
    else:
        return jsonify({"success": False, "message": "사용자 없음"})

# HTML 페이지 렌더링
@app.route('/home.html')
def home_page():
    return render_template('home.html')

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/exercise-selection.html')
def exercise_selection_page():
    return render_template('exercise-selection.html')

@app.route('/exercise.html')
def exercise_page():
    return render_template('exercise.html')

@app.route('/stats.html')
def stats_page():
    return render_template('stats.html')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
