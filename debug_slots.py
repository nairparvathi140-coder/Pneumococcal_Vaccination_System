import sqlite3
conn=sqlite3.connect("pneumococcal.db")
conn.row_factory=sqlite3.Row
cursor=conn.cursor()
print("\n--- REGISTERED DOCTORS ---")
cursor.execute("""
SELECT D.doctor_id,S.full_name
FROM Doctor D JOIN Staff S ON D.staff_id=S.staff_id
""")
for row in cursor.fetchall():
    print(dict(row))
print("\n--- APPOINTMENT RECORDS ---")
cursor.execute("""
SELECT appointment_id,patient_id,doctor_id,appointment_datetime,status,
date(appointment_datetime) AS extracted_date
FROM Appointment
ORDER BY appointment_datetime
""")
for row in cursor.fetchall():
    print(dict(row))
conn.close()