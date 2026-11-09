import os
import sqlite3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")
print("DATABASE PATH:", DB_NAME)
if not os.path.exists(DB_NAME):
    print("ERROR: Database file does not exist!")
else:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print("\nTABLES FOUND:")
    for table in tables:
        print("-", table[0])
    conn.close()