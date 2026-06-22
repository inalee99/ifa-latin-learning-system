import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE attempts
SET user_id = 1
WHERE user_id IS NULL
""")

conn.commit()
conn.close()

print("舊答題紀錄已補上 user_id = 1")