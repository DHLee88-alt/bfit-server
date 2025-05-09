from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# 데이터베이스 경로 (절대경로로 안정성 확보)
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

# 루트 페이지 (Render 헬스 체크용)
@app.route('/')
def index():
    return 'B-Fit Server is Running!'

# 회원가입
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"success": False, "message": "필수 데이터 없음"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "이미 존재하는 아이디"})

    c.execute('INSERT INTO users (id, password, exercise_count, last_exercise_date) VALUES (?, ?, 0, NULL)', (user_id, password))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "회원가입 성공"})

# 운동 기록 저장
@app.route('/save-exercise', methods=['POST'])
def save_exercise():
    data = request.json
    user_id = data.get('id')
    today = data.get('date')

    if not user_id or not today:
        return jsonify({"success": False, "message": "필수 데이터 없음"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET exercise_count = exercise_count + 3, last_exercise_date = ?
        WHERE id = ?
    ''', (today, user_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "운동 기록 저장 완료"})

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

# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
