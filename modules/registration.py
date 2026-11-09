
import os
import re
import sqlite3
import hashlib
import secrets
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")
ITERATIONS = 310000

# PNEUMOCARE THEME
NAVY = "#172B4D"
BLUE = "#2878D0"
BLUE_DARK = "#1D5FA8"
WHITE = "#FFFFFF"
BG = "#F2F6FC"
LIGHT = "#EAF1FA"
BORDER = "#DFE7F1"
MUTED = "#718096"
TEXT = "#26364A"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )
    return password_hash.hex(), salt.hex()


def username_exists(username):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT account_id
            FROM User_Account
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (username,)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def valid_email(email):
    return re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ) is not None


def valid_phone(phone):
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 15


def configure_styles(parent):
    style = ttk.Style(parent)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Registration.TEntry",
        fieldbackground=WHITE,
        foreground=TEXT,
        padding=9,
        bordercolor=BORDER
    )
    style.configure(
        "Registration.TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=TEXT,
        padding=8,
        bordercolor=BORDER
    )
    style.map(
        "Registration.TCombobox",
        fieldbackground=[("readonly", WHITE)],
        selectbackground=[("readonly", WHITE)],
        selectforeground=[("readonly", TEXT)]
    )
    style.configure(
        "Registration.TButton",
        font=("Segoe UI", 9, "bold"),
        padding=(15, 9)
    )
    style.configure(
        "Registration.Horizontal.TProgressbar",
        troughcolor=LIGHT,
        background=BLUE,
        bordercolor=LIGHT,
        lightcolor=BLUE,
        darkcolor=BLUE
    )


def clear_parent(parent):
    for widget in parent.winfo_children():
        widget.destroy()


def make_header(parent, title, subtitle):
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(5, 18))

    tk.Label(
        header,
        text="PneumoCare",
        bg=BG,
        fg=BLUE,
        font=("Segoe UI", 11, "bold")
    ).pack()

    tk.Label(
        header,
        text=title,
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 23, "bold")
    ).pack(pady=(6, 3))

    subtitle_label = tk.Label(
        header,
        text=subtitle,
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    )
    subtitle_label.pack()

    return subtitle_label


def make_label(parent, text):
    return tk.Label(
        parent,
        text=text,
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 9, "bold")
    )


def make_entry(parent, variable, show=None):
    return ttk.Entry(
        parent,
        textvariable=variable,
        show=show,
        style="Registration.TEntry",
        font=("Segoe UI", 10)
    )


def make_button(parent, text, command, primary=True):
    if primary:
        bg = BLUE
        fg = WHITE
        active_bg = BLUE_DARK
    else:
        bg = LIGHT
        fg = BLUE
        active_bg = "#DCE8F7"

    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=active_bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        font=("Segoe UI", 9, "bold" if primary else "normal"),
        padx=18,
        pady=10,
        cursor="hand2"
    )


# ============================================================
# STAFF REGISTRATION
# ============================================================

def show_staff_registration(parent, on_back=None):
    clear_parent(parent)
    configure_styles(parent)

    main_frame = tk.Frame(parent, bg=BG)
    main_frame.pack(fill="both", expand=True, padx=25, pady=18)

    make_header(
        main_frame,
        "Staff Registration",
        "Submit your professional details for administrator approval"
    )

    card = tk.Frame(
        main_frame,
        bg=WHITE,
        padx=35,
        pady=25,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True, padx=35, pady=(0, 15))

    tk.Label(
        card,
        text="Professional Information",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", pady=(0, 4))

    tk.Label(
        card,
        text="Fields marked with * are required.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(0, 14))

    form = tk.Frame(card, bg=WHITE)
    form.pack(fill="x")

    full_name_var = tk.StringVar()
    role_var = tk.StringVar(value="Doctor")
    specialization_var = tk.StringVar()
    phone_var = tk.StringVar()
    email_var = tk.StringVar()
    username_var = tk.StringVar()
    password_var = tk.StringVar()
    confirm_password_var = tk.StringVar()

    def add_staff_field(label_text, variable, row, show=None):
        make_label(form, label_text).grid(
            row=row,
            column=0,
            sticky="w",
            padx=(0, 22),
            pady=9
        )

        entry = make_entry(form, variable, show)
        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=9
        )
        return entry

    form.columnconfigure(1, weight=1)

    add_staff_field("Full Name *", full_name_var, 0)

    make_label(form, "Staff Role *").grid(
        row=1,
        column=0,
        sticky="w",
        padx=(0, 22),
        pady=9
    )

    role_dropdown = ttk.Combobox(
        form,
        textvariable=role_var,
        values=["Doctor", "Nurse", "Vaccination Staff"],
        state="readonly",
        style="Registration.TCombobox",
        font=("Segoe UI", 10)
    )
    role_dropdown.grid(row=1, column=1, sticky="ew", pady=9)

    specialization_entry = add_staff_field(
        "Specialization *",
        specialization_var,
        2
    )
    add_staff_field("Phone Number *", phone_var, 3)
    add_staff_field("Email Address *", email_var, 4)
    add_staff_field("Username *", username_var, 5)
    add_staff_field("Password *", password_var, 6, "*")
    add_staff_field("Confirm Password *", confirm_password_var, 7, "*")

    def update_specialization(event=None):
        if role_var.get() == "Doctor":
            specialization_entry.configure(state="normal")
        else:
            specialization_var.set("")
            specialization_entry.configure(state="disabled")

    role_dropdown.bind(
        "<<ComboboxSelected>>",
        update_specialization
    )
    update_specialization()

    tk.Frame(card, bg=BORDER, height=1).pack(
        fill="x",
        pady=(18, 12)
    )

    tk.Label(
        card,
        text="Staff accounts remain inactive until approved by an administrator.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9),
        wraplength=650,
        justify="left"
    ).pack(anchor="w")

    def submit_registration():
        full_name = full_name_var.get().strip()
        role = role_var.get()
        specialization = specialization_var.get().strip()
        phone = phone_var.get().strip()
        email = email_var.get().strip()
        username = username_var.get().strip()
        password = password_var.get()
        confirm_password = confirm_password_var.get()

        if not all([
            full_name,
            role,
            phone,
            email,
            username,
            password,
            confirm_password
        ]):
            messagebox.showerror(
                "Missing Information",
                "Please complete all required fields.",
                parent=parent
            )
            return

        if role == "Doctor" and not specialization:
            messagebox.showerror(
                "Missing Information",
                "Please enter the doctor's specialization.",
                parent=parent
            )
            return

        if not valid_phone(phone):
            messagebox.showerror(
                "Invalid Phone",
                "Enter a valid phone number containing 10 to 15 digits.",
                parent=parent
            )
            return

        if not valid_email(email):
            messagebox.showerror(
                "Invalid Email",
                "Enter a valid email address.",
                parent=parent
            )
            return

        if len(password) < 8:
            messagebox.showerror(
                "Weak Password",
                "Password must contain at least 8 characters.",
                parent=parent
            )
            return

        if password != confirm_password:
            messagebox.showerror(
                "Password Error",
                "Passwords do not match.",
                parent=parent
            )
            return

        password_hash, password_salt = hash_password(password)
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT account_id
                FROM User_Account
                WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
                LIMIT 1
                """,
                (username,)
            )

            if cursor.fetchone():
                messagebox.showerror(
                    "Username Exists",
                    f"The username '{username}' is already registered.",
                    parent=parent
                )
                return

            cursor.execute(
                """
                INSERT INTO Staff
                (full_name, role, phone, email, username)
                VALUES (?, ?, ?, ?, ?)
                """,
                (full_name, role, phone, email, username)
            )

            staff_id = cursor.lastrowid

            if role == "Doctor":
                cursor.execute(
                    """
                    INSERT INTO Doctor (staff_id, specialization)
                    VALUES (?, ?)
                    """,
                    (staff_id, specialization)
                )

            cursor.execute(
                """
                INSERT INTO User_Account
                (username, password_hash, password_salt, role,
                 patient_id, staff_id, account_status)
                VALUES (?, ?, ?, 'staff', NULL, ?, 'pending')
                """,
                (
                    username,
                    password_hash,
                    password_salt,
                    staff_id
                )
            )

            conn.commit()

            messagebox.showinfo(
                "Registration Submitted",
                "Your staff registration has been submitted successfully.\n\n"
                "Your account is pending administrator approval. "
                "You will be able to log in after it is approved.",
                parent=parent
            )

            if on_back:
                on_back()

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Registration Error",
                f"Could not complete registration:\n{error}",
                parent=parent
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=parent
            )

        finally:
            if conn:
                conn.close()

    buttons = tk.Frame(card, bg=WHITE)
    buttons.pack(fill="x", pady=(18, 0))

    make_button(
        buttons,
        "Submit Registration",
        submit_registration
    ).pack(side="left", padx=(0, 10))

    if on_back:
        make_button(
            buttons,
            "Back to Login",
            on_back,
            primary=False
        ).pack(side="left")


# ============================================================
# PATIENT REGISTRATION
# ============================================================

def show_patient_registration(parent, on_back=None):
    clear_parent(parent)
    configure_styles(parent)

    main_frame = tk.Frame(parent, bg=BG)
    main_frame.pack(fill="both", expand=True, padx=22, pady=12)

    subtitle = make_header(
        main_frame,
        "Patient Registration",
        "Create your PneumoCare patient account"
    )

    card = tk.Frame(
        main_frame,
        bg=WHITE,
        padx=30,
        pady=20,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True)

    title = tk.Label(
        card,
        text="Personal Details",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 15, "bold")
    )
    title.pack(anchor="w", pady=(0, 4))

    progress = tk.Label(
        card,
        text="STEP 1 OF 2  |  PERSONAL DETAILS",
        bg=WHITE,
        fg=BLUE,
        font=("Segoe UI", 9, "bold")
    )
    progress.pack(anchor="w", pady=(0, 8))

    progress_bar = ttk.Progressbar(
        card,
        style="Registration.Horizontal.TProgressbar",
        maximum=2,
        value=1,
        mode="determinate"
    )
    progress_bar.pack(fill="x", pady=(0, 15))

    form = tk.Frame(card, bg=WHITE)
    form.pack(fill="both", expand=True, padx=2)

    footer = tk.Frame(card, bg=WHITE)
    footer.pack(side="bottom", fill="x", pady=(12, 0))

    personal_fields = {
        "Full Name": tk.StringVar(),
        "Date of Birth (YYYY-MM-DD)": tk.StringVar(),
        "Gender": tk.StringVar(value="Select"),
        "Blood Group": tk.StringVar(value=""),
        "Phone": tk.StringVar(),
        "Email": tk.StringVar(),
        "Address": tk.StringVar(),
        "Username": tk.StringVar(),
        "Password": tk.StringVar(),
        "Confirm Password": tk.StringVar()
    }

    medical_fields = {
        "Allergy": tk.StringVar(),
        "Allergy Reaction": tk.StringVar(),
        "Allergy Severity": tk.StringVar(value="Unknown"),
        "Medical Conditions": tk.StringVar(),
        "Previous Adverse Reaction": tk.StringVar(),
        "Previous Pneumococcal Vaccine": tk.StringVar(),
        "Previous Vaccination Date (YYYY-MM-DD)": tk.StringVar(),
        "Previous Dose Number": tk.StringVar()
    }

    all_fields = {**personal_fields, **medical_fields}
    entries = {}

    def clear_page():
        for widget in form.winfo_children():
            widget.destroy()

        for widget in footer.winfo_children():
            widget.destroy()

        entries.clear()

    def add_form_field(label, variable, row, column, width=30, show=None):
        field_frame = tk.Frame(form, bg=WHITE)
        field_frame.grid(
            row=row,
            column=column,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=6
        )

        make_label(field_frame, label).pack(
            anchor="w",
            pady=(0, 5)
        )

        if label == "Gender":
            widget = ttk.Combobox(
                field_frame,
                textvariable=variable,
                values=[
                    "Male",
                    "Female",
                    "Other",
                    "Prefer not to say"
                ],
                state="readonly",
                style="Registration.TCombobox",
                font=("Segoe UI", 10)
            )

        elif label == "Blood Group":
            widget = ttk.Combobox(
                field_frame,
                textvariable=variable,
                values=[
                    "A+", "A-", "B+", "B-",
                    "AB+", "AB-", "O+", "O-",
                    "Unknown"
                ],
                state="readonly",
                style="Registration.TCombobox",
                font=("Segoe UI", 10)
            )

        elif label == "Allergy Severity":
            widget = ttk.Combobox(
                field_frame,
                textvariable=variable,
                values=["Unknown", "Mild", "Moderate", "Severe"],
                state="readonly",
                style="Registration.TCombobox",
                font=("Segoe UI", 10)
            )

        else:
            widget = make_entry(field_frame, variable, show)

        widget.pack(fill="x", ipady=2)
        entries[label] = widget

    def add_footer_note(text):
        tk.Label(
            footer,
            text=text,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8),
            wraplength=950,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

    def show_personal_page():
        clear_page()

        title.config(text="Personal Details")
        subtitle.config(text="Enter your personal and account information")
        progress.config(text="STEP 1 OF 2  |  PERSONAL DETAILS")
        progress_bar.configure(value=1)

        for index, label in enumerate(personal_fields):
            row = index // 2
            column = (index % 2) * 2

            add_form_field(
                label,
                personal_fields[label],
                row,
                column,
                show="*" if label in [
                    "Password",
                    "Confirm Password"
                ] else None
            )

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=1)

        add_footer_note(
            "Your medical information will be collected on the next page."
        )

        buttons = tk.Frame(footer, bg=WHITE)
        buttons.pack(anchor="center")

        make_button(
            buttons,
            "Next: Medical Details",
            validate_personal
        ).pack(side="left", padx=6)

        if on_back:
            make_button(
                buttons,
                "Back to Login",
                on_back,
                primary=False
            ).pack(side="left", padx=6)

    def validate_personal():
        data = {
            key: value.get().strip()
            for key, value in personal_fields.items()
        }

        required = [
            "Full Name",
            "Date of Birth (YYYY-MM-DD)",
            "Gender",
            "Phone",
            "Email",
            "Username",
            "Password",
            "Confirm Password"
        ]

        if any(not data[field] for field in required):
            messagebox.showerror(
                "Missing Information",
                "Please complete all required personal and account fields.",
                parent=parent
            )
            return

        if data["Gender"] == "Select":
            messagebox.showerror(
                "Missing Information",
                "Please select your gender.",
                parent=parent
            )
            return

        try:
            dob = datetime.strptime(
                data["Date of Birth (YYYY-MM-DD)"],
                "%Y-%m-%d"
            ).date()

            if dob > date.today():
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "The date cannot be in the future.",
                parent=parent
            )
            return

        if not valid_phone(data["Phone"]):
            messagebox.showerror(
                "Invalid Phone",
                "Enter a valid phone number containing 10 to 15 digits.",
                parent=parent
            )
            return

        if not valid_email(data["Email"]):
            messagebox.showerror(
                "Invalid Email",
                "Enter a valid email address.",
                parent=parent
            )
            return

        if len(data["Password"]) < 8:
            messagebox.showerror(
                "Weak Password",
                "Password must contain at least 8 characters.",
                parent=parent
            )
            return

        if data["Password"] != data["Confirm Password"]:
            messagebox.showerror(
                "Password Error",
                "Passwords do not match.",
                parent=parent
            )
            return

        try:
            if username_exists(data["Username"]):
                messagebox.showerror(
                    "Username Exists",
                    f"The username '{data['Username']}' is already registered. "
                    "Please choose another username.",
                    parent=parent
                )
                entries["Username"].focus_set()
                return

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not check username availability:\n{error}",
                parent=parent
            )
            return

        show_medical_page()

    def show_medical_page():
        clear_page()

        title.config(text="Medical Details")
        subtitle.config(
            text="Provide your medical and previous vaccination history"
        )
        progress.config(text="STEP 2 OF 2  |  MEDICAL DETAILS")
        progress_bar.configure(value=2)

        for index, label in enumerate(medical_fields):
            row = index // 2
            column = (index % 2) * 2

            add_form_field(
                label,
                medical_fields[label],
                row,
                column
            )

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=1)

        add_footer_note(
            "Medical and vaccination history is collected for clinical review. "
            "This information does not automatically determine vaccine eligibility."
        )

        buttons = tk.Frame(footer, bg=WHITE)
        buttons.pack(anchor="center")

        make_button(
            buttons,
            "Back",
            show_personal_page,
            primary=False
        ).pack(side="left", padx=6)

        make_button(
            buttons,
            "Create Patient Account",
            submit_patient
        ).pack(side="left", padx=6)

    def submit_patient():
        data = {
            key: value.get().strip()
            for key, value in all_fields.items()
        }

        vaccine_name = data["Previous Pneumococcal Vaccine"]
        vaccine_date = data["Previous Vaccination Date (YYYY-MM-DD)"]
        dose_number = data["Previous Dose Number"]

        if data["Allergy Reaction"] and not data["Allergy"]:
            messagebox.showerror(
                "Allergy Details",
                "Enter the allergy name associated with this reaction.",
                parent=parent
            )
            return

        if data["Allergy"] and not data["Allergy Severity"]:
            messagebox.showerror(
                "Allergy Details",
                "Select the allergy severity or choose Unknown.",
                parent=parent
            )
            return

        if vaccine_name:
            try:
                parsed_vaccine_date = datetime.strptime(
                    vaccine_date,
                    "%Y-%m-%d"
                ).date()

                parsed_dose_number = int(dose_number)

                if (
                    parsed_vaccine_date > date.today()
                    or parsed_dose_number < 1
                ):
                    raise ValueError

            except (ValueError, TypeError):
                messagebox.showerror(
                    "Previous Vaccine Details",
                    "Enter a valid previous vaccination date in YYYY-MM-DD "
                    "format (not in the future) and a dose number of at least 1.",
                    parent=parent
                )
                return

        elif vaccine_date or dose_number:
            messagebox.showerror(
                "Previous Vaccine Details",
                "Enter the previous vaccine name as well.",
                parent=parent
            )
            return

        password_hash, password_salt = hash_password(data["Password"])
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Create the patient record.
            cursor.execute(
                """
                INSERT INTO Patient
                (full_name, dob, gender, phone, email, address, blood_group)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["Full Name"],
                    data["Date of Birth (YYYY-MM-DD)"],
                    data["Gender"],
                    data["Phone"],
                    data["Email"],
                    data["Address"],
                    data["Blood Group"]
                )
            )

            patient_id = cursor.lastrowid

            # Create the patient login account.
            cursor.execute(
                """
                INSERT INTO User_Account
                (username, password_hash, password_salt, role,
                 patient_id, staff_id, account_status)
                VALUES (?, ?, ?, 'patient', ?, NULL, 'active')
                """,
                (
                    data["Username"],
                    password_hash,
                    password_salt,
                    patient_id
                )
            )

            # Save allergy details, if provided.
            if data["Allergy"]:
                cursor.execute(
                    """
                    INSERT INTO Patient_Allergy
                    (patient_id, allergy_name, reaction, severity)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        patient_id,
                        data["Allergy"],
                        data["Allergy Reaction"],
                        data["Allergy Severity"]
                    )
                )

            # Save medical conditions.
            if data["Medical Conditions"]:
                cursor.execute(
                    """
                    INSERT INTO Patient_Medical_History
                    (patient_id, history_type, details, recorded_date)
                    VALUES (?, 'Medical Condition', ?, ?)
                    """,
                    (
                        patient_id,
                        data["Medical Conditions"],
                        date.today().isoformat()
                    )
                )

            # Save previous adverse reactions.
            if data["Previous Adverse Reaction"]:
                cursor.execute(
                    """
                    INSERT INTO Patient_Medical_History
                    (patient_id, history_type, details, recorded_date)
                    VALUES (?, 'Adverse Reaction', ?, ?)
                    """,
                    (
                        patient_id,
                        data["Previous Adverse Reaction"],
                        date.today().isoformat()
                    )
                )

            # Save previously administered pneumococcal vaccines.
            if vaccine_name:
                cursor.execute(
                    """
                    INSERT INTO Patient_Vaccine_History
                    (patient_id, vaccine_name, vaccination_date,
                     dose_number, administered_elsewhere, notes)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (
                        patient_id,
                        vaccine_name,
                        vaccine_date,
                        int(dose_number),
                        "Reported during patient registration"
                    )
                )

            conn.commit()

            messagebox.showinfo(
                "Registration Successful",
                "Your patient account has been created successfully.\n\n"
                f"Your Patient ID is: {patient_id}\n\n"
                "You can now log in to PneumoCare.",
                parent=parent
            )

            if on_back:
                on_back()

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Registration Error",
                f"Could not complete registration:\n{error}",
                parent=parent
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=parent
            )

        finally:
            if conn:
                conn.close()

    show_personal_page()
