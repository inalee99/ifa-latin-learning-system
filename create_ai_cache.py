import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_cache (
    plant_id INTEGER PRIMARY KEY,
    ai_explanation TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("ai_cache 建立完成")