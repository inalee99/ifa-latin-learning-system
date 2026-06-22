import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM attempts
ORDER BY id DESC
LIMIT 20
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()