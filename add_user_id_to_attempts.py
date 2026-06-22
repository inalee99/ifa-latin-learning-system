import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE attempts
ADD COLUMN user_id INTEGER
""")

conn.commit()
conn.close()

print("attempts 已新增 user_id 欄位")