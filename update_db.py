import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# 누락된 컬럼 추가
try:
    c.execute("ALTER TABLE users ADD COLUMN name TEXT")
except:
    print("name 컬럼은 이미 존재합니다.")

try:
    c.execute("ALTER TABLE users ADD COLUMN birth TEXT")
except:
    print("birth 컬럼은 이미 존재합니다.")

try:
    c.execute("ALTER TABLE users ADD COLUMN affiliation TEXT")
except:
    print("affiliation 컬럼은 이미 존재합니다.")

try:
    c.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
except:
    print("is_verified 컬럼은 이미 존재합니다.")

try:
    c.execute("ALTER TABLE users ADD COLUMN verify_token TEXT")
except:
    print("verify_token 컬럼은 이미 존재합니다.")

conn.commit()
conn.close()
print("✅ DB 컬럼 추가 완료")
