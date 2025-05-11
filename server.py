from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
import secrets

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
CORS(app)

DB_PATH = 'users.db'
ADMIN_EMAIL = "dark6936@gmail.com"

# 환경 변수에서 메일 정보 가져오기
MAIL_ADDRESS = os.environ.get("MAIL_ADDRESS")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

# ✅ DB 초기화
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
            last_exercise_date TEXT,
            is_verified INTEGER DEFAULT 0,
            verify_token TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ 인증 메일 발송 함수
def send_verification_email(user_email, token):
    link = f"https://bfit-server.onrender.com/verify?token={token}"
    body = f"""비핏(B-Fit) 회원가입을 환영합니다!\n\n
아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n{link}"""

    msg = MIMEText(body)
    msg["Subject"] = "비핏 - 이메일 인증"
    msg["From"] = MAIL_ADDRESS
    msg["To"] = user_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(MAIL_ADDRESS, MAIL_PASSWORD)
    server.sendmail(MAIL_ADDRESS, [user_email], msg.as_string())
    server.quit()

# ✅ HTML 라우팅
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
    if session.get("user_email") != ADMIN_EMAIL:
        return redirect(url_for('home_page'))
    return render_template('admin.html')

# ✅ 이메일 인증 처리
@app.route('/verify')
def verify():
    token = request.args.get("token")
    if not token:
        return "토큰이 없습니다.", 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE verify_token = ?", (token,))
    user = c.fetchone()

    if user:
        c.execute("UPDATE users SET is_verified = 1, verify_token = NULL WHERE verify_token = ?", (token,))
        conn.commit()
        msg = "✅ 이메일 인증이 완료되었습니다. 이제 로그인할 수 있습니다."
    else:
        msg = "❌ 유효하지 않은 토큰입니다."

    conn.close()
    return msg

# ✅ 회원가입
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    name = data.get('name')
    birth = data.get('birth')
    affiliation = data.get('affiliation')

    if not user_id or not password:
        return jsonify({"success": False, "message": "필수 항목 누락"})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})

    token = secrets.token_urlsafe(16)

    c.execute('''
        INSERT INTO users (id, password, name, birth, affiliation, exercise_count, last_exercise_date, is_verified, verify_token)
        VALUES (?, ?, ?, ?, ?, 0, NULL, 0, ?)
    ''', (user_id, password, name, birth, affiliation, token))
    conn.commit()
    conn.close()

    send_verification_email(user_id, token)

    return jsonify({"success": True, "message": "회원가입 성공. 이메일을 확인해주세요."})

# ✅ 로그인
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('pw')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password, is_verified FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()

    if result:
        if result[0] != password:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."})
        if result[1] == 0:
            return jsonify({"success": False, "message": "이메일 인증이 필요합니다."})
        session["user_email"] = user_id
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "존재하지 않는 아이디입니다."})

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

# ✅ 관리자 전용 회원 목록
@app.route('/admin-users')
def admin_users():
    if session.get("user_email") != ADMIN_EMAIL:
        return jsonify({"success": False, "message": "접근 권한 없음"}), 403

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
            "last_exercise_date": row[5]
        })
    return jsonify({"success": True, "users": user_list})

# ✅ 서버 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
