import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE plants
SET image_url = ?
WHERE english_name = ?
""", (
    "https://upload.wikimedia.org/wikipedia/commons/8/8f/Boswellia_sacra_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-022.jpg",
    "Frankincense"
))

conn.commit()
conn.close()

print("乳香圖片已更新")