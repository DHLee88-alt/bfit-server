# PostgreSQL 전환 버전 server.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import smtplib
from email.mime.text import MIMEText
import secrets
import requests

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
CORS(app)

# PostgreSQL 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')  # Render 환경변수에 설정
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 사용자 모델 정의
class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    birth = db.Column(db.String(100))
    affiliation = db.Column(db.String(100))
    exercise_count = db.Column(db.Integer, default=0)
    last_exercise_date = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    verify_token = db.Column(db.String(200))

def send_verification_email(user_email, token):
    link = f"https://bfit-server.onrender.com/verify?token={token}"
    body = f"비핏(B-Fit) 회원가입을 환영합니다!\n\n아래 링크를 클릭하여 이메일 인증을 완료해주세요:\n{link}"
    msg = MIMEText(body)
    msg['Subject'] = "비핏 - 이메일 인증"
    msg['From'] = os.environ.get("MAIL_ADDRESS")
    msg['To'] = user_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(os.environ.get("MAIL_ADDRESS"), os.environ.get("MAIL_PASSWORD"))
    server.sendmail(os.environ.get("MAIL_ADDRESS"), [user_email], msg.as_string())
    server.quit()

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
    if session.get("user_email") != "dark6936@gmail.com":
        return redirect(url_for('home_page'))
    return render_template('admin.html')

@app.route('/color-response')
def color_response():
    return render_template('color-response.html')

@app.route('/verify')
def verify():
    token = request.args.get("token")
    user = User.query.filter_by(verify_token=token).first()
    if user:
        user.is_verified = True
        user.verify_token = None
        db.session.commit()
        return "✅ 이메일 인증이 완료되었습니다. 이제 로그인할 수 있습니다."
    else:
        return "❌ 유효하지 않은 토큰입니다."

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

    if User.query.get(user_id):
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})

    token = secrets.token_urlsafe(16)
    new_user = User(id=user_id, password=password, name=name, birth=birth, affiliation=affiliation, verify_token=token)
    db.session.add(new_user)
    db.session.commit()

    send_verification_email(user_id, token)
    return jsonify({"success": True, "message": "회원가입 성공. 이메일을 확인해주세요."})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('pw')
    user = User.query.get(user_id)

    if user:
        if user.password != password:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."})
        if not user.is_verified:
            return jsonify({"success": False, "message": "이메일 인증이 필요합니다."})
        session["user_email"] = user.id
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "존재하지 않는 아이디입니다."})

@app.route('/save-exercise', methods=['POST'])
def save_exercise():
    data = request.json
    user_id = data.get('id')
    today = data.get('date')
    user = User.query.get(user_id)

    if not user:
        return jsonify({"success": False, "message": "사용자 없음"})

    user.exercise_count += 3
    user.last_exercise_date = today
    db.session.commit()
    return jsonify({"success": True, "message": "운동 기록 저장 완료"})

@app.route('/get-exercise-data', methods=['GET'])
def get_exercise_data():
    user_id = request.args.get('id')
    user = User.query.get(user_id)

    if user:
        return jsonify({
            "success": True,
            "total_count": user.exercise_count,
            "last_date": user.last_exercise_date or "기록 없음"
        })
    else:
        return jsonify({"success": False, "message": "사용자 없음"})

@app.route('/admin-users')
def admin_users():
    if session.get("user_email") != "dark6936@gmail.com":
        return jsonify({"success": False, "message": "접근 권한 없음"}), 403

    users = User.query.all()
    user_list = [
        {
            "id": u.id,
            "name": u.name,
            "birth": u.birth,
            "affiliation": u.affiliation,
            "exercise_count": u.exercise_count,
            "last_exercise_date": u.last_exercise_date
        } for u in users
    ]
    return jsonify({"success": True, "users": user_list})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

@app.route('/debug-users')
def debug_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "birth": u.birth,
            "affiliation": u.affiliation,
            "verified": u.is_verified,
            "exercise_count": u.exercise_count,
            "last_exercise_date": u.last_exercise_date
        }
        for u in users
    ])
