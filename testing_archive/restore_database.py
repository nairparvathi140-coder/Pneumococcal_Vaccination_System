import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

tables = [
"""
CREATE TABLE IF NOT EXISTS Patient (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    dob DATE NOT NULL,
    gender TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    blood_group TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""",
"""
CREATE TABLE IF NOT EXISTS Staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    username TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""",
"""
CREATE TABLE IF NOT EXISTS Doctor (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER UNIQUE NOT NULL,
    specialization TEXT,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
)
""",
"""
CREATE TABLE IF NOT EXISTS Vaccine (
    vaccine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaccine_name TEXT NOT NULL,
    manufacturer TEXT,
    vaccine_type TEXT,
    description TEXT
)
""",
"""
CREATE TABLE IF NOT EXISTS Vaccine_Batch (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaccine_id INTEGER NOT NULL,
    batch_number TEXT UNIQUE NOT NULL,
    manufacturing_date DATE,
    expiry_date DATE,
    quantity_received INTEGER NOT NULL,
    quantity_available INTEGER NOT NULL,
    received_date DATE DEFAULT CURRENT_DATE,
    CHECK (quantity_received >= 0),
    CHECK (quantity_available >= 0),
    CHECK (quantity_available <= quantity_received),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id)
)
""",
"""
CREATE TABLE IF NOT EXISTS Eligibility_Assessment (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    assessed_by INTEGER NOT NULL,
    assessment_date DATE DEFAULT CURRENT_DATE,
    risk_category TEXT,
    eligibility_status TEXT,
    reason TEXT,
    clinical_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (assessed_by) REFERENCES Doctor(doctor_id)
)
""",
"""
CREATE TABLE IF NOT EXISTS Appointment (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_datetime DATETIME NOT NULL,
    status TEXT DEFAULT 'Scheduled',
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
)
""",
"""
CREATE TABLE IF NOT EXISTS Vaccination (
    vaccination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    vaccine_id INTEGER NOT NULL,
    batch_id INTEGER NOT NULL,
    appointment_id INTEGER,
    administered_by INTEGER NOT NULL,
    dose_number INTEGER NOT NULL,
    date_administered DATE NOT NULL,
    next_due_date DATE,
    adverse_reaction_notes TEXT,
    UNIQUE(patient_id, vaccine_id, dose_number),
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id),
    FOREIGN KEY (batch_id) REFERENCES Vaccine_Batch(batch_id),
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id),
    FOREIGN KEY (administered_by) REFERENCES Staff(staff_id)
)
"""
]

try:
    for table_sql in tables:
        cursor.execute(table_sql)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointment_patient ON Appointment(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vaccination_patient ON Vaccination(patient_id)")
    conn.commit()
    print("Missing database tables restored successfully!")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print("\nCURRENT DATABASE TABLES:")
    for row in cursor.fetchall():
        print("-", row[0])
except sqlite3.Error as error:
    conn.rollback()
    print("DATABASE ERROR:", error)
finally:
    conn.close()