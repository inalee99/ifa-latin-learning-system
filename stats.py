import sqlite3

conn = sqlite3.connect("ifa.db")
cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM attempts
""")

total = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM attempts
WHERE is_correct = 1
""")

correct = cursor.fetchone()[0]

wrong = total - correct

if total > 0:
    accuracy = round(correct / total * 100, 2)
else:
    accuracy = 0

print("總答題數：", total)
print("答對：", correct)
print("答錯：", wrong)
print("正確率：", accuracy, "%")

conn.close()