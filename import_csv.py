import csv
import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS plants")

cursor.execute("""
CREATE TABLE plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chinese_name TEXT,
    english_name TEXT,
    latin_name TEXT,
    genus TEXT,
    species TEXT,
    family TEXT,
    plant_part TEXT,
    extraction_method TEXT,
    chemical_family TEXT,
    notes TEXT
)
""")

with open("plants.csv", "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cursor.execute("""
        INSERT INTO plants (
            chinese_name,
            english_name,
            latin_name,
            genus,
            species,
            family,
            plant_part,
            extraction_method,
            chemical_family,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["中文名"],
            row["英文名"],
            row["拉丁學名"],
            row["屬名"],
            row["種名"],
            row["科別"],
            row["萃取部位"],
            row["萃取方式"],
            row["化學家族"],
            row["備註"]
        ))

conn.commit()
conn.close()

print("匯入完成")