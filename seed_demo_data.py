
import sqlite3
import hashlib
import os
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pneumococcal.db")
DEMO_PASSWORD = "Demo@123"

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310000)
    return password_hash.hex(), salt.hex()

def shift_date(start_date, days):
    result = start_date + timedelta(days=days)
    while result.weekday() == 6:
        result += timedelta(days=1)
    return result

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.cursor()

        # Safety checks: never overwrite existing records or admin credentials.
        cur.execute("SELECT username FROM User_Account WHERE role = 'admin'")
        admins = cur.fetchall()
        if not admins:
            raise Exception("No admin account found. Seeding cancelled.")
        cur.execute("SELECT COUNT(*) FROM User_Account WHERE role <> 'admin'")
        if cur.fetchone()[0] != 0:
            raise Exception("Non-admin accounts already exist. Seeding cancelled.")
        for table in ["Patient", "Staff", "Doctor", "Vaccine", "Vaccine_Batch", "Eligibility_Assessment", "Appointment", "Vaccination", "Patient_Allergy", "Patient_Medical_History", "Patient_Vaccine_History"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            if cur.fetchone()[0] != 0:
                raise Exception(f"{table} is not empty. Seeding cancelled to prevent duplicate data.")

        # 1. PATIENTS: 50 fictional patients
        first_names = [
            "Aarav","Aditi","Aditya","Ananya","Arjun","Bhavana","Charan","Deepa","Divya","Girish",
            "Harish","Ishita","Kavya","Kiran","Lakshmi","Manoj","Meera","Nandini","Nikhil","Pooja",
            "Pranav","Priya","Rahul","Radhika","Rakesh","Riya","Rohan","Sanjay","Shreya","Sneha",
            "Srinivas","Suhas","Tanvi","Varun","Vidya","Vikram","Yash","Anil","Chitra","Dinesh",
            "Farhan","Geetha","Hemant","Jyothi","Madhav","Neha","Prakash","Rekha","Suresh","Vani"
        ]
        last_names = [
            "Rao","Sharma","Reddy","Nair","Shetty","Kumar","Patil","Gowda","Iyer","Menon",
            "Desai","Kulkarni","Murthy","Joshi","Bhat","Naidu","Pillai","Hegde","Shah","Mishra"
        ]
        areas = [
            "Jayanagar","Indiranagar","Whitefield","Malleshwaram","Rajajinagar",
            "Basavanagudi","Banashankari","BTM Layout","HSR Layout","Koramangala",
            "Hebbal","Yelahanka","JP Nagar","Vijayanagar","Electronic City"
        ]
        genders = ["Male","Female","Female","Male","Other"]
        blood_groups = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
        patients = []
        patient_ids = []
        patient_account_ids = []

        for i in range(50):
            full_name = f"{first_names[i]} {last_names[(i * 7) % len(last_names)]}"
            dob = date(1945 + (i * 11) % 46, 1 + (i * 5) % 12, 1 + (i * 7) % 27)
            phone = f"900000{1000 + i:04d}"
            email = f"patient{i + 1:03d}@example.test"
            address = f"{10 + i}, {areas[i % len(areas)]}, Bengaluru, Karnataka"
            cur.execute("""
                INSERT INTO Patient (full_name, dob, gender, phone, email, address, blood_group)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (full_name, dob.isoformat(), genders[i % len(genders)], phone, email, address, blood_groups[i % len(blood_groups)]))
            patient_id = cur.lastrowid
            patient_ids.append(patient_id)
            patients.append((full_name, dob.isoformat(), email, phone, address))

            password_hash, password_salt = hash_password(DEMO_PASSWORD)
            username = f"patient{i + 1:03d}"
            cur.execute("""
                INSERT INTO User_Account
                (username, password_hash, password_salt, role, patient_id, staff_id, account_status)
                VALUES (?, ?, ?, 'patient', ?, NULL, 'active')
            """, (username, password_hash, password_salt, patient_id))
            patient_account_ids.append(cur.lastrowid)

        # 2. STAFF: 6 doctors and 4 other staff members
        staff_data = [
            ("Dr. Ananya Rao","Doctor","9845001001","doctor1@example.test","Consultant Physician"),
            ("Dr. Vikram Shetty","Doctor","9845001002","doctor2@example.test","Geriatric Medicine"),
            ("Dr. Meera Nair","Doctor","9845001003","doctor3@example.test","Internal Medicine"),
            ("Dr. Arjun Reddy","Doctor","9845001004","doctor4@example.test","Pulmonology"),
            ("Dr. Kavya Iyer","Doctor","9845001005","doctor5@example.test","Family Medicine"),
            ("Dr. Rohan Kumar","Doctor","9845001006","doctor6@example.test","General Medicine"),
            ("Suma Patil","Nurse","9845001007","nurse1@example.test",""),
            ("Ramesh Gowda","Nurse","9845001008","nurse2@example.test",""),
            ("Divya Menon","Vaccination Officer","9845001009","staff1@example.test",""),
            ("Kiran Murthy","Receptionist","9845001010","staff2@example.test","")
        ]
        staff_ids = []
        doctor_ids = []
        staff_account_usernames = []

        for i, (name, role, phone, email, specialization) in enumerate(staff_data):
            username = f"staff{i + 1:02d}"
            cur.execute("""
                INSERT INTO Staff (full_name, role, phone, email, username)
                VALUES (?, ?, ?, ?, ?)
            """, (name, role, phone, email, username))
            staff_id = cur.lastrowid
            staff_ids.append(staff_id)
            staff_account_usernames.append(username)

            password_hash, password_salt = hash_password(DEMO_PASSWORD)
            cur.execute("""
                INSERT INTO User_Account
                (username, password_hash, password_salt, role, patient_id, staff_id, account_status)
                VALUES (?, ?, ?, 'staff', NULL, ?, 'active')
            """, (username, password_hash, password_salt, staff_id))

            if role == "Doctor":
                cur.execute("""
                    INSERT INTO Doctor (staff_id, specialization)
                    VALUES (?, ?)
                """, (staff_id, specialization))
                doctor_ids.append(cur.lastrowid)

        # 3. VACCINES
        vaccine_data = [
            ("Pneumococcal Conjugate Vaccine PCV10","Serum Institute of India","Conjugate","10-valent pneumococcal conjugate vaccine"),
            ("Pneumococcal Conjugate Vaccine PCV13","Pfizer","Conjugate","13-valent pneumococcal conjugate vaccine"),
            ("Pneumococcal Conjugate Vaccine PCV15","Merck","Conjugate","15-valent pneumococcal conjugate vaccine"),
            ("Pneumococcal Conjugate Vaccine PCV20","Pfizer","Conjugate","20-valent pneumococcal conjugate vaccine"),
            ("Pneumococcal Polysaccharide Vaccine PPSV23","Merck","Polysaccharide","23-valent pneumococcal polysaccharide vaccine")
        ]
        vaccine_ids = []
        for name, manufacturer, vaccine_type, description in vaccine_data:
            cur.execute("""
                INSERT INTO Vaccine (vaccine_name, manufacturer, vaccine_type, description)
                VALUES (?, ?, ?, ?)
            """, (name, manufacturer, vaccine_type, description))
            vaccine_ids.append(cur.lastrowid)

        # 4. VACCINE BATCHES: 2 batches for each vaccine
        batch_ids = {}
        today = date.today()
        for vaccine_index, vaccine_id in enumerate(vaccine_ids):
            batch_ids[vaccine_id] = []
            for batch_index in range(2):
                batch_number = f"PC{vaccine_index + 1:02d}-2026-{batch_index + 1:02d}"
                manufacturing_date = date(2025, 1 + vaccine_index, 10 + batch_index)
                expiry_date = date(2028 + batch_index, 6 + (vaccine_index % 6), 15)
                cur.execute("""
                    INSERT INTO Vaccine_Batch
                    (vaccine_id, batch_number, manufacturing_date, expiry_date,
                     quantity_received, quantity_available, received_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    vaccine_id, batch_number, manufacturing_date.isoformat(),
                    expiry_date.isoformat(), 100, 100, today.isoformat()
                ))
                batch_ids[vaccine_id].append(cur.lastrowid)

        # 5. ALLERGIES
        allergy_options = [
            ("Penicillin","Skin rash","Moderate"),
            ("Dust","Sneezing and irritation","Mild"),
            ("Latex","Skin irritation","Mild"),
            ("Sulfa drugs","Rash","Moderate"),
            ("Egg","Hives","Moderate"),
            ("Pollen","Sneezing","Mild"),
            ("Aspirin","Stomach discomfort","Moderate"),
            ("Adhesive tape","Local skin redness","Mild")
        ]
        for i in range(18):
            patient_id = patient_ids[(i * 3) % 50]
            allergy, reaction, severity = allergy_options[i % len(allergy_options)]
            cur.execute("""
                INSERT INTO Patient_Allergy (patient_id, allergy_name, reaction, severity)
                VALUES (?, ?, ?, ?)
            """, (patient_id, allergy, reaction, severity))

        # 6. MEDICAL HISTORY
        medical_conditions = [
            "Hypertension managed with regular follow-up.",
            "Type 2 diabetes mellitus, under routine monitoring.",
            "History of asthma with occasional symptoms.",
            "Chronic obstructive pulmonary disease, under specialist care.",
            "Chronic kidney disease, monitored by physician.",
            "History of cardiovascular disease.",
            "No significant chronic medical condition reported.",
            "History of recurrent respiratory infections.",
            "Hyperlipidaemia managed through regular review.",
            "Chronic bronchitis, currently stable."
        ]
        for i in range(30):
            cur.execute("""
                INSERT INTO Patient_Medical_History
                (patient_id, history_type, details, recorded_date)
                VALUES (?, 'Medical Condition', ?, ?)
            """, (patient_ids[(i * 7) % 50], medical_conditions[i % len(medical_conditions)], (today - timedelta(days=20 + i)).isoformat()))

        for i in range(8):
            cur.execute("""
                INSERT INTO Patient_Medical_History
                (patient_id, history_type, details, recorded_date)
                VALUES (?, 'Adverse Reaction', ?, ?)
            """, (patient_ids[(i * 5 + 2) % 50], "Previous mild injection-site soreness; resolved without treatment.", (today - timedelta(days=100 + i)).isoformat()))

        # 7. PREVIOUS VACCINE HISTORY
        previous_vaccines = ["Influenza vaccine","Pneumococcal vaccine","COVID-19 vaccine","Influenza vaccine","PPSV23"]
        for i in range(25):
            vaccination_date = today - timedelta(days=180 + i * 23)
            cur.execute("""
                INSERT INTO Patient_Vaccine_History
                (patient_id, vaccine_name, vaccination_date, dose_number, administered_elsewhere, notes)
                VALUES (?, ?, ?, ?, 'Yes', ?)
            """, (
                patient_ids[(i * 2) % 50],
                previous_vaccines[i % len(previous_vaccines)],
                vaccination_date.isoformat(),
                1 if i % 3 else 2,
                "Previous vaccination reported by patient; details recorded for clinical review."
            ))

        # 8. APPOINTMENTS: 35 completed, 5 cancelled, 10 scheduled
        appointment_ids = []
        completed_appointments = []
        appointment_records = []

        # Historical appointments
        for i in range(40):
            patient_id = patient_ids[i]
            doctor_id = doctor_ids[i % len(doctor_ids)]
            appointment_date = shift_date(today, -(i + 2))
            appointment_time = f"{9 + (i % 8):02d}:{(i % 2) * 30:02d}"
            status = "Completed" if i < 35 else "Cancelled"
            notes = "Routine pneumococcal vaccination consultation." if status == "Completed" else "Appointment cancelled by patient."
            cur.execute("""
                INSERT INTO Appointment
                (patient_id, doctor_id, appointment_datetime, status, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, f"{appointment_date.isoformat()} {appointment_time}", status, notes))
            appointment_id = cur.lastrowid
            appointment_ids.append(appointment_id)
            appointment_records.append((patient_id, doctor_id, appointment_date, status, appointment_id))
            if status == "Completed":
                completed_appointments.append((patient_id, doctor_id, appointment_date, appointment_id))

        # Future scheduled appointments
        for i in range(10):
            patient_id = patient_ids[40 + i]
            doctor_id = doctor_ids[i % len(doctor_ids)]
            appointment_date = shift_date(today, i + 1)
            appointment_time = f"{9 + (i % 8):02d}:{(i % 2) * 30:02d}"
            cur.execute("""
                INSERT INTO Appointment
                (patient_id, doctor_id, appointment_datetime, status, notes)
                VALUES (?, ?, ?, 'Scheduled', ?)
            """, (patient_id, doctor_id, f"{appointment_date.isoformat()} {appointment_time}", "Scheduled pneumococcal vaccination consultation."))
            appointment_ids.append(cur.lastrowid)

        # 9. ELIGIBILITY ASSESSMENTS: one for each patient
        risk_categories = ["Low","Moderate","High","Very High"]
        eligibility_statuses = ["Eligible","Eligible","Eligible","Pending Review","Not Eligible"]
        reasons = [
            "Patient meets the assessment criteria based on age and available medical history.",
            "Patient has a documented chronic condition and requires vaccination review.",
            "Risk factors identified; vaccination recommended following clinical assessment.",
            "Additional clinical review is required before a final eligibility decision.",
            "Vaccination deferred pending review of current clinical circumstances."
        ]
        for i, patient_id in enumerate(patient_ids):
            cur.execute("""
                INSERT INTO Eligibility_Assessment
                (patient_id, assessed_by, assessment_date, risk_category,
                 eligibility_status, reason, clinical_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                doctor_ids[i % len(doctor_ids)],
                (today - timedelta(days=i % 25)).isoformat(),
                risk_categories[i % len(risk_categories)],
                eligibility_statuses[i % len(eligibility_statuses)],
                reasons[i % len(reasons)],
                "Demonstration assessment record. Final decisions require review by the treating clinician."
            ))

        # 10. VACCINATIONS: 35 records linked to completed appointments
        for i, (patient_id, doctor_id, appointment_date, appointment_id) in enumerate(completed_appointments):
            vaccine_id = vaccine_ids[i % len(vaccine_ids)]
            batch_id = batch_ids[vaccine_id][i % 2]
            administered_by = staff_ids[i % len(staff_ids)]
            next_due = appointment_date + timedelta(days=365 * 5) if i % 3 == 0 else None
            cur.execute("""
                INSERT INTO Vaccination
                (patient_id, vaccine_id, batch_id, appointment_id, administered_by,
                 dose_number, date_administered, next_due_date, adverse_reaction_notes)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (
                patient_id, vaccine_id, batch_id, appointment_id, administered_by,
                appointment_date.isoformat(),
                next_due.isoformat() if next_due else None,
                "No adverse reaction reported at the time of recording." if i % 4 else "Mild injection-site soreness reported; resolved."
            ))
            cur.execute("""
                UPDATE Vaccine_Batch
                SET quantity_available = quantity_available - 1
                WHERE batch_id = ?
            """, (batch_id,))

        # Validate foreign keys before committing.
        violations = cur.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise Exception(f"Foreign key validation failed: {violations[:5]}")

        conn.commit()

        print("\nDEMO DATA CREATED SUCCESSFULLY")
        print("--------------------------------")
        tables = [
            "Patient","Staff","Doctor","Vaccine","Vaccine_Batch",
            "Patient_Allergy","Patient_Medical_History","Patient_Vaccine_History",
            "Eligibility_Assessment","Appointment","Vaccination","User_Account"
        ]
        for table in tables:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count}")
        print("--------------------------------")
        print("Existing admin account preserved:", ", ".join(row[0] for row in admins))
        print("Demo patient/staff password:", DEMO_PASSWORD)
        print("Patient usernames: patient001 to patient050")
        print("Staff usernames: staff01 to staff10")
        print("All demo accounts are active.")

    except Exception as error:
        conn.rollback()
        print("\nSEEDING FAILED. All changes were rolled back.")
        print("Reason:", error)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
