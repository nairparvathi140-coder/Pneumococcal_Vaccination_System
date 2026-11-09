
import sqlite3
import os
import hashlib
import hmac
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")
ITERATIONS = 310000

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password, salt=None):
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    if salt is None:
        salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    ).hex()
    return password_hash, salt.hex()

def verify_password(password, stored_hash, stored_salt):
    try:
        if not isinstance(password, str) or not stored_hash or not stored_salt:
            return False
        salt = bytes.fromhex(stored_salt)
        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            ITERATIONS
        ).hex()
        return hmac.compare_digest(calculated_hash, stored_hash)
    except (ValueError, TypeError, AttributeError):
        return False

def ensure_recovery_table():
    conn = None
    try:
        conn = get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Admin_Recovery (
                account_id INTEGER PRIMARY KEY,
                recovery_hash TEXT NOT NULL,
                recovery_salt TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id)
                    REFERENCES User_Account(account_id)
                    ON DELETE CASCADE
            )
        """)
        conn.commit()
        return True
    except sqlite3.Error:
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def authenticate_user(username, password, selected_role):
    username = (username or "").strip()

    if not username or not password:
        return {
            "success": False,
            "message": "Enter both username and password."
        }

    if selected_role not in ("admin", "staff", "patient"):
        return {
            "success": False,
            "message": "Invalid account type."
        }

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT account_id, username, password_hash, password_salt,
                   role, patient_id, staff_id, account_status
            FROM User_Account
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
        """, (username,))
        account = cursor.fetchone()

        if not account:
            return {
                "success": False,
                "message": "Invalid username or password."
            }

        (
            account_id,
            account_username,
            stored_hash,
            stored_salt,
            actual_role,
            patient_id,
            staff_id,
            account_status
        ) = account

        if not verify_password(password, stored_hash, stored_salt):
            return {
                "success": False,
                "message": "Invalid username or password."
            }

        if actual_role != selected_role:
            return {
                "success": False,
                "message": "This account does not belong to the selected login type."
            }

        if account_status == "pending":
            return {
                "success": False,
                "message": "Your account is awaiting administrator approval."
            }

        if account_status == "disabled":
            return {
                "success": False,
                "message": "Your account has been disabled. Contact the administrator."
            }

        if account_status != "active":
            return {
                "success": False,
                "message": "This account is not active. Contact the administrator."
            }

        return {
            "success": True,
            "message": "Login successful!",
            "account_id": account_id,
            "username": account_username,
            "role": actual_role,
            "patient_id": patient_id,
            "staff_id": staff_id
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "message": f"Database error: {error}"
        }
    finally:
        if conn:
            conn.close()

def normalize_phone(phone):
    return "".join(character for character in str(phone or "") if character.isdigit())

# VERIFY PATIENT OR STAFF RECOVERY DETAILS
def verify_recovery_details(username, selected_role, email, phone):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = normalize_phone(phone)

    if not username or not email or not phone:
        return False

    if selected_role not in ("patient", "staff"):
        return False

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if selected_role == "patient":
            cursor.execute("""
                SELECT UA.account_id
                FROM User_Account UA
                JOIN Patient P ON UA.patient_id = P.patient_id
                WHERE LOWER(TRIM(UA.username)) = LOWER(TRIM(?))
                  AND UA.role = 'patient'
                  AND UA.account_status = 'active'
                  AND LOWER(TRIM(P.email)) = ?
                  AND REPLACE(REPLACE(REPLACE(REPLACE(
                      TRIM(P.phone), ' ', ''), '-', ''), '+', ''), '(', '') = ?
            """, (username, email, phone))
        else:
            cursor.execute("""
                SELECT UA.account_id
                FROM User_Account UA
                JOIN Staff S ON UA.staff_id = S.staff_id
                WHERE LOWER(TRIM(UA.username)) = LOWER(TRIM(?))
                  AND UA.role = 'staff'
                  AND UA.account_status = 'active'
                  AND LOWER(TRIM(S.email)) = ?
                  AND REPLACE(REPLACE(REPLACE(REPLACE(
                      TRIM(S.phone), ' ', ''), '-', ''), '+', ''), '(', '') = ?
            """, (username, email, phone))

        record = cursor.fetchone()
        if not record:
            return False

        # Compare phone numbers after removing common formatting characters.
        table = "Patient" if selected_role == "patient" else "Staff"
        id_column = "patient_id" if selected_role == "patient" else "staff_id"

        cursor.execute(f"""
            SELECT T.phone
            FROM User_Account UA
            JOIN {table} T ON UA.{id_column} = T.{id_column}
            WHERE UA.account_id = ?
        """, (record[0],))

        stored_phone = cursor.fetchone()
        return bool(stored_phone and normalize_phone(stored_phone[0]) == phone)

    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()

# RESET PATIENT OR STAFF PASSWORD
def reset_password_by_contact(username, selected_role, email, phone, new_password):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    phone = normalize_phone(phone)

    if not username or not email or not phone:
        return False, "Enter all account verification details."

    if selected_role not in ("patient", "staff"):
        return False, "Invalid account type."

    if not isinstance(new_password, str) or len(new_password) < 8:
        return False, "Password must contain at least 8 characters."

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        if selected_role == "patient":
            cursor.execute("""
                SELECT UA.account_id, P.phone
                FROM User_Account UA
                JOIN Patient P ON UA.patient_id = P.patient_id
                WHERE LOWER(TRIM(UA.username)) = LOWER(TRIM(?))
                  AND UA.role = 'patient'
                  AND UA.account_status = 'active'
                  AND LOWER(TRIM(P.email)) = ?
            """, (username, email))
        else:
            cursor.execute("""
                SELECT UA.account_id, S.phone
                FROM User_Account UA
                JOIN Staff S ON UA.staff_id = S.staff_id
                WHERE LOWER(TRIM(UA.username)) = LOWER(TRIM(?))
                  AND UA.role = 'staff'
                  AND UA.account_status = 'active'
                  AND LOWER(TRIM(S.email)) = ?
            """, (username, email))

        account = cursor.fetchone()

        if not account or normalize_phone(account[1]) != phone:
            conn.rollback()
            return False, "The account details could not be verified."

        password_hash, password_salt = hash_password(new_password)

        cursor.execute("""
            UPDATE User_Account
            SET password_hash = ?, password_salt = ?
            WHERE account_id = ? AND account_status = 'active'
        """, (password_hash, password_salt, account[0]))

        if cursor.rowcount != 1:
            conn.rollback()
            return False, "The account could not be updated."

        conn.commit()
        return True, "Your password has been reset successfully."

    except sqlite3.Error as error:
        if conn:
            conn.rollback()
        return False, f"Database error: {error}"
    finally:
        if conn:
            conn.close()

# SET ADMIN RECOVERY KEY
def set_admin_recovery_key(username, current_password, recovery_key):
    username = (username or "").strip()

    if not username or not current_password:
        return False, "Enter your username and current password."

    if not isinstance(recovery_key, str) or len(recovery_key) < 12:
        return False, "Recovery key must contain at least 12 characters."

    if not ensure_recovery_table():
        return False, "Could not prepare the administrator recovery system."

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT account_id, password_hash, password_salt
            FROM User_Account
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
              AND role = 'admin'
              AND account_status = 'active'
        """, (username,))

        account = cursor.fetchone()

        if not account or not verify_password(current_password, account[1], account[2]):
            conn.rollback()
            return False, "Administrator username or current password is incorrect."

        recovery_hash, recovery_salt = hash_password(recovery_key)

        cursor.execute("""
            INSERT INTO Admin_Recovery (
                account_id, recovery_hash, recovery_salt
            )
            VALUES (?, ?, ?)
            ON CONFLICT(account_id) DO UPDATE SET
                recovery_hash = excluded.recovery_hash,
                recovery_salt = excluded.recovery_salt,
                updated_at = CURRENT_TIMESTAMP
        """, (account[0], recovery_hash, recovery_salt))

        conn.commit()
        return True, "Administrator recovery key saved successfully."

    except sqlite3.Error as error:
        if conn:
            conn.rollback()
        return False, f"Database error: {error}"
    finally:
        if conn:
            conn.close()

# RESET ADMIN PASSWORD USING RECOVERY KEY
def reset_admin_password(username, recovery_key, new_password):
    username = (username or "").strip()

    if not username or not recovery_key:
        return False, "Enter your administrator username and recovery key."

    if not isinstance(new_password, str) or len(new_password) < 8:
        return False, "Password must contain at least 8 characters."

    if not ensure_recovery_table():
        return False, "Could not prepare the administrator recovery system."

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT UA.account_id, AR.recovery_hash, AR.recovery_salt
            FROM User_Account UA
            JOIN Admin_Recovery AR ON UA.account_id = AR.account_id
            WHERE LOWER(TRIM(UA.username)) = LOWER(TRIM(?))
              AND UA.role = 'admin'
              AND UA.account_status = 'active'
        """, (username,))

        account = cursor.fetchone()

        if not account or not verify_password(recovery_key, account[1], account[2]):
            conn.rollback()
            return False, "Administrator username or recovery key is incorrect."

        password_hash, password_salt = hash_password(new_password)

        cursor.execute("""
            UPDATE User_Account
            SET password_hash = ?, password_salt = ?
            WHERE account_id = ? AND role = 'admin'
              AND account_status = 'active'
        """, (password_hash, password_salt, account[0]))

        if cursor.rowcount != 1:
            conn.rollback()
            return False, "The administrator password could not be updated."

        conn.commit()
        return True, "Administrator password has been reset successfully."

    except sqlite3.Error as error:
        if conn:
            conn.rollback()
        return False, f"Database error: {error}"
    finally:
        if conn:
            conn.close()
