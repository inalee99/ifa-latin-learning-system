import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE plants
    ADD COLUMN image_url TEXT
    """)
    print("已新增 image_url 欄位")
except sqlite3.OperationalError:
    print("image_url 欄位可能已經存在")

conn.commit()
conn.close()