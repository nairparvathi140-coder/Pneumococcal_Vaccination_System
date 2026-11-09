
import sqlite3

conn = sqlite3.connect("pneumococcal.db")
cursor = conn.cursor()

vaccines = [
    ("PCV15", "Merck", "Conjugate", "Pneumococcal conjugate vaccine"),
    ("PCV20", "Pfizer", "Conjugate", "Pneumococcal conjugate vaccine"),
    ("PPSV23", "Merck", "Polysaccharide", "Pneumococcal polysaccharide vaccine")
]

cursor.executemany("""
INSERT INTO Vaccine
(vaccine_name, manufacturer, vaccine_type, description)
VALUES (?, ?, ?, ?)
""", vaccines)

conn.commit()
conn.close()

print("Sample vaccine records inserted!")
