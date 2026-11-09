import sqlite3
conn = sqlite3.connect("pneumococcal.db")
cursor = conn.cursor()
cursor.execute("""
SELECT UA.username, UA.role, UA.account_status, P.full_name, P.email, P.phone
FROM User_Account UA
JOIN Patient P ON UA.patient_id = P.patient_id
WHERE UA.role = 'patient'
""")
records = cursor.fetchall()
print("\nREGISTERED PATIENT ACCOUNTS")
print("-" * 70)
if records:
    for record in records:
        print("Username:", record[0])
        print("Role:", record[1])
        print("Status:", record[2])
        print("Name:", record[3])
        print("Email:", record[4])
        print("Phone:", record[5])
        print("-" * 70)
else:
    print("No patient accounts found.")
conn.close()