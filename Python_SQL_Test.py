import sqlite3
conn = sqlite3.connect("finanzen.db")
with open("schema.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()