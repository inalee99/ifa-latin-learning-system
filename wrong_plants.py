import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    p.chinese_name,
    p.latin_name,
    COUNT(*) AS wrong_count
FROM attempts a
JOIN plants p
ON a.plant_id = p.id
WHERE a.is_correct = 0
GROUP BY a.plant_id
ORDER BY wrong_count DESC
LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()