from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

DB_PATH = 'users.db'

# ✅ DB 초기화 (테이블 및 누락 컬럼 자동 생성)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT,
            birth TEXT,
            affiliation TEXT,
            exercise_count INTEGER DEFAULT 0,
            last_exercise_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ HTML 페이지 렌더링
@app.route('/')
def root():
    return render_template('login.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

@app.route('/home.html')
def home_page():
    return render_template('home.html')

@app.route('/exercise-selection.html')
def selection_page():
    return render_template('exercise-selection.html')

@app.route('/exercise.html')
def exercise_page():
    return render_template('exercise.html')

@app.route('/stats.html')
def stats_page():
    return render_template('stats.html')

@app.route('/admin.html')
def admin_page():
    return render_template('admin.html')

# ✅ 회원가입 API
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    name = data.get('name')
    birth = data.get('birth')
    affiliation = data.get('affiliation')

    if not user_id or not password:
        return jsonify({"success": False, "message": "필수 입력 누락"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "이미 존재하는 아이디"})

    c.execute('''
        INSERT INTO users (id, password, name, birth, affiliation, exercise_count, last_exercise_date)
        VALUES (?, ?, ?, ?, ?, 0, NULL)
    ''', (user_id, password, name, birth, affiliation))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "회원가입 성공"})

# ✅ 로그인 API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('pw')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == password:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호가 일치하지 않습니다."})

# ✅ 운동 기록 저장
@app.route('/save-exercise', methods=['POST'])
def save_exercise():
    data = request.json
    user_id = data.get('id')
    today = data.get('date')

    if not user_id or not today:
        return jsonify({"success": False, "message": "필수 데이터 누락"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET exercise_count = exercise_count + 3,
            last_exercise_date = ?
        WHERE id = ?
    ''', (today, user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "운동 기록 저장 완료"})

# ✅ 운동 기록 조회
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
        return jsonify({
            "success": True,
            "total_count": result[0],
            "last_date": result[1] or "기록 없음"
        })
    else:
        return jsonify({"success": False, "message": "사용자 없음"})

# ✅ 관리자용 회원 목록 확인 (JSON)
@app.route('/admin/users')
def admin_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, birth, affiliation, exercise_count, last_exercise_date FROM users')
    rows = c.fetchall()
    conn.close()

    user_list = []
    for row in rows:
        user_list.append({
            "id": row[0],
            "name": row[1],
            "birth": row[2],
            "affiliation": row[3],
            "exercise_count": row[4],
            "last_date": row[5]
        })
    return jsonify(user_list)

# ✅ 서버 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
