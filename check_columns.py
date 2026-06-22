# check_columns.py

import sqlite3

conn = sqlite3.connect("ifa.db")

cursor = conn.cursor()

cursor.execute("PRAGMA table_info(plants)")

for row in cursor.fetchall():
    print(row)

conn.close()