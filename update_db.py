import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# is_verified 컬럼 추가 (있으면 건너뜀)
try:
    c.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
except:
    print("✅ is_verified 컬럼 이미 있음")

# verify_token 컬럼 추가
try:
    c.execute("ALTER TABLE users ADD COLUMN verify_token TEXT")
except:
    print("✅ verify_token 컬럼 이미 있음")

conn.commit()
conn.close()
print("DB 컬럼 추가 완료")
