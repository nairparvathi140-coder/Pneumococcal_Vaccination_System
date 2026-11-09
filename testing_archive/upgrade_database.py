
import sqlite3
import os
import sys

# ---------------- DATABASE PATH ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")


def upgrade_database():

    # Prevent accidentally creating a new empty database.
    if not os.path.isfile(DB_NAME):
        print("ERROR: pneumococcal.db was not found.")
        print("Check that this script is in your main project folder.")
        return

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")

    try:

        cursor = conn.cursor()

        # ---------------- USER ACCOUNT ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User_Account (

                account_id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                password_salt TEXT NOT NULL,

                role TEXT NOT NULL
                    CHECK (role IN ('admin', 'staff', 'patient')),

                patient_id INTEGER UNIQUE,

                staff_id INTEGER UNIQUE,

                account_status TEXT NOT NULL DEFAULT 'active'
                    CHECK (
                        account_status IN (
                            'pending',
                            'active',
                            'disabled'
                        )
                    ),

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (patient_id)
                    REFERENCES Patient(patient_id),

                FOREIGN KEY (staff_id)
                    REFERENCES Staff(staff_id),

                CHECK (
                    (role = 'admin'
                        AND patient_id IS NULL
                        AND staff_id IS NULL)

                    OR

                    (role = 'patient'
                        AND patient_id IS NOT NULL
                        AND staff_id IS NULL)

                    OR

                    (role = 'staff'
                        AND staff_id IS NOT NULL
                        AND patient_id IS NULL)
                )
            )
        """)

        # ---------------- PATIENT ALLERGY ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patient_Allergy (

                allergy_id INTEGER PRIMARY KEY AUTOINCREMENT,

                patient_id INTEGER NOT NULL,

                allergy_name TEXT NOT NULL,

                reaction TEXT,

                severity TEXT
                    CHECK (
                        severity IS NULL OR
                        severity IN (
                            'Mild',
                            'Moderate',
                            'Severe',
                            'Unknown'
                        )
                    ),

                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (patient_id)
                    REFERENCES Patient(patient_id)
            )
        """)

        # ---------------- PATIENT MEDICAL HISTORY ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patient_Medical_History (

                history_id INTEGER PRIMARY KEY AUTOINCREMENT,

                patient_id INTEGER NOT NULL,

                history_type TEXT NOT NULL
                    CHECK (
                        history_type IN (
                            'Medical Condition',
                            'Adverse Reaction',
                            'Other'
                        )
                    ),

                details TEXT NOT NULL,

                recorded_date TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (patient_id)
                    REFERENCES Patient(patient_id)
            )
        """)

        # ---------------- PATIENT VACCINE HISTORY ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patient_Vaccine_History (

                history_id INTEGER PRIMARY KEY AUTOINCREMENT,

                patient_id INTEGER NOT NULL,

                vaccine_name TEXT NOT NULL,

                vaccination_date TEXT,

                dose_number INTEGER,

                administered_elsewhere TEXT DEFAULT 'Yes',

                notes TEXT,

                FOREIGN KEY (patient_id)
                    REFERENCES Patient(patient_id)
            )
        """)

        # ---------------- INDEXES ----------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_account_username
            ON User_Account(username)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_allergy_patient
            ON Patient_Allergy(patient_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_medical_history_patient
            ON Patient_Medical_History(patient_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vaccine_history_patient
            ON Patient_Vaccine_History(patient_id)
        """)

        conn.commit()

        print("\nDATABASE UPGRADE SUCCESSFUL!")
        print("--------------------------------")

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        for table in cursor.fetchall():
            print(table[0])

        print("\nNew account and medical-history tables are ready.")

    except sqlite3.Error as e:

        conn.rollback()

        print("\nDATABASE UPGRADE FAILED!")
        print("Error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    upgrade_database()
