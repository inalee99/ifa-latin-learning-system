import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE plants
SET image_url = ?
WHERE english_name = ?
""", (
    "/static/images/grapefruit.jpg",
    "Grapefruit"
))

conn.commit()
conn.close()

print("葡萄柚圖片已更新")