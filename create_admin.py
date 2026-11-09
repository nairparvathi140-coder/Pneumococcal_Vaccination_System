
import sqlite3
import os
import hashlib
import secrets
import getpass

# ---------------- DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

ITERATIONS = 310000


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    ).hex()


def create_admin():

    if not os.path.exists(DB_NAME):
        print("Database not found. Check your project folder.")
        return

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        # Check whether an admin already exists
        cursor.execute("""
            SELECT account_id
            FROM User_Account
            WHERE role = 'admin'
        """)

        if cursor.fetchone():
            print("An administrator account already exists.")
            return

        print("\n========== PNEUMOCARE ADMIN SETUP ==========\n")

        username = input("Enter admin username: ").strip()

        if not username:
            print("Username cannot be empty.")
            return

        cursor.execute(
            "SELECT account_id FROM User_Account WHERE username = ?",
            (username,)
        )

        if cursor.fetchone():
            print("This username is already taken.")
            return

        password = getpass.getpass("Enter admin password: ")
        confirm_password = getpass.getpass("Confirm admin password: ")

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        # Generate a unique random salt
        salt = secrets.token_bytes(16)

        password_hash = hash_password(password, salt)

        cursor.execute("""
            INSERT INTO User_Account (
                username,
                password_hash,
                password_salt,
                role,
                patient_id,
                staff_id,
                account_status
            )
            VALUES (?, ?, ?, 'admin', NULL, NULL, 'active')
        """, (
            username,
            password_hash,
            salt.hex()
        ))

        conn.commit()

        print("\nADMIN ACCOUNT CREATED SUCCESSFULLY!")
        print("-----------------------------------")
        print("Username:", username)
        print("Role: Administrator")
        print("Status: Active")
        print("\nKeep your password safe.")

    except sqlite3.Error as e:

        conn.rollback()
        print("Database error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()
