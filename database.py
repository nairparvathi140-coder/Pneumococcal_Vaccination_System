
import sqlite3

DB_NAME = "pneumococcal.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        username TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Doctor (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL UNIQUE,
        specialization TEXT,
        FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vaccine (
        vaccine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vaccine_name TEXT NOT NULL,
        manufacturer TEXT,
        vaccine_type TEXT,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vaccine_Batch (
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vaccine_id INTEGER NOT NULL,
        batch_number TEXT NOT NULL UNIQUE,
        manufacturing_date DATE,
        expiry_date DATE NOT NULL,
        quantity_received INTEGER NOT NULL CHECK(quantity_received >= 0),
        quantity_available INTEGER NOT NULL CHECK(quantity_available >= 0),
        received_date DATE,
        CHECK(quantity_available <= quantity_received),
        FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Eligibility_Assessment (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        assessed_by INTEGER,
        assessment_date DATE NOT NULL,
        risk_category TEXT,
        eligibility_status TEXT NOT NULL,
        reason TEXT,
        clinical_notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
        FOREIGN KEY (assessed_by) REFERENCES Doctor(doctor_id)
    )
    """)

    cursor.execute("""
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
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vaccination (
        vaccination_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        vaccine_id INTEGER NOT NULL,
        batch_id INTEGER NOT NULL,
        appointment_id INTEGER,
        administered_by INTEGER NOT NULL,
        dose_number INTEGER NOT NULL CHECK(dose_number > 0),
        date_administered DATETIME NOT NULL,
        next_due_date DATE,
        adverse_reaction_notes TEXT,
        UNIQUE(patient_id, vaccine_id, dose_number),
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
        FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id),
        FOREIGN KEY (batch_id) REFERENCES Vaccine_Batch(batch_id),
        FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id),
        FOREIGN KEY (administered_by) REFERENCES Staff(staff_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database and tables created successfully!")


if __name__ == "__main__":
    create_tables()
