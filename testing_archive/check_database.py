
import sqlite3

conn = sqlite3.connect("pneumococcal.db")
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

print("\n===== DATABASE TABLES =====")

cursor.execute("""
SELECT name FROM sqlite_master
WHERE type = 'table'
ORDER BY name
""")

for table in cursor.fetchall():
    print("✔", table[0])

print("\n===== TABLE STRUCTURE =====")

for table in [
    "Patient", "Staff", "Doctor", "Vaccine",
    "Vaccine_Batch", "Eligibility_Assessment",
    "Appointment", "Vaccination"
]:
    cursor.execute(f"PRAGMA table_info({table})")
    print(f"\n{table}:")
    for column in cursor.fetchall():
        print("  ", column[1], "-", column[2])

conn.close()
