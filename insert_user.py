import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
INSERT OR IGNORE INTO users (username)
VALUES (?)
""", ("Ina",))

conn.commit()
conn.close()

print("使用者建立完成")