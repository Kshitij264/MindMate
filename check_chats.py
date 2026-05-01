import sqlite3

conn = sqlite3.connect("mindmate.db")  # ✅ Use the correct DB name
c = conn.cursor()

c.execute("SELECT * FROM chat_history")
rows = c.fetchall()

for row in rows:
    print(row)

conn.close()
