import sqlite3

conn = sqlite3.connect("pneumococcal.db")

for row in conn.execute("SELECT * FROM Vaccine"):
    print(row)

conn.close()