import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
DELETE FROM plants
WHERE
    (chinese_name IS NULL OR TRIM(chinese_name) = '')
AND (english_name IS NULL OR TRIM(english_name) = '')
AND (latin_name IS NULL OR TRIM(latin_name) = '')
""")

conn.commit()

print("已刪除空白植物筆數：", cursor.rowcount)

conn.close()