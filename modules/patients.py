
import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

# PNEUMOCARE THEME
BG = "#F2F6FC"
WHITE = "#FFFFFF"
NAVY = "#172B4D"
BLUE = "#2878D0"
BLUE_DARK = "#1D5FA8"
GREEN = "#159D79"
RED = "#D9534F"
MUTED = "#718096"
BORDER = "#DFE7F1"
LIGHT = "#EAF1FA"
TEXT = "#26364A"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


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
        "Patient.TEntry",
        fieldbackground=WHITE,
        foreground=TEXT,
        padding=8,
        bordercolor=BORDER
    )

    style.configure(
        "Patient.TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=TEXT,
        padding=8,
        bordercolor=BORDER
    )

    style.map(
        "Patient.TCombobox",
        fieldbackground=[("readonly", WHITE)],
        selectbackground=[("readonly", WHITE)],
        selectforeground=[("readonly", TEXT)]
    )

    style.configure(
        "Patient.Treeview",
        background=WHITE,
        foreground=TEXT,
        fieldbackground=WHITE,
        rowheight=30,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Patient.Treeview.Heading",
        background=LIGHT,
        foreground=NAVY,
        font=("Segoe UI", 9, "bold"),
        padding=8
    )

    style.map(
        "Patient.Treeview",
        background=[("selected", "#D9E9FC")],
        foreground=[("selected", NAVY)]
    )


def show_patients(parent, page_title, clear_content):
    clear_content()
    configure_styles(parent)

    selected_id = None

    # ========================================================
    # HEADER
    # ========================================================

    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(0, 12))

    tk.Label(
        header,
        text="Patient Management",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 21, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Register, search and manage hospital patient records",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 0))

    # ========================================================
    # PATIENT INFORMATION FORM
    # ========================================================

    form = tk.Frame(
        parent,
        bg=WHITE,
        padx=20,
        pady=15,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 12))

    tk.Label(
        form,
        text="Patient Information",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 14, "bold")
    ).grid(
        row=0,
        column=0,
        columnspan=4,
        sticky="w",
        pady=(0, 12)
    )

    fields = {}

    field_labels = [
        ("Full Name", "full_name"),
        ("Date of Birth (YYYY-MM-DD)", "dob"),
        ("Phone Number", "phone"),
        ("Email Address", "email"),
        ("Address", "address"),
        ("Blood Group", "blood_group")
    ]

    for index, (label, key) in enumerate(field_labels):
        row = (index // 2) + 1
        col = (index % 2) * 2

        tk.Label(
            form,
            text=label,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=row,
            column=col,
            sticky="w",
            padx=(0, 12),
            pady=7
        )

        if key == "blood_group":
            entry = ttk.Combobox(
                form,
                values=[
                    "A+", "A-", "B+", "B-",
                    "AB+", "AB-", "O+", "O-",
                    "Unknown"
                ],
                state="readonly",
                style="Patient.TCombobox",
                font=("Segoe UI", 9)
            )
        else:
            entry = ttk.Entry(
                form,
                style="Patient.TEntry",
                font=("Segoe UI", 9)
            )

        entry.grid(
            row=row,
            column=col + 1,
            sticky="ew",
            padx=(0, 18),
            pady=6
        )

        fields[key] = entry

    # Gender field
    tk.Label(
        form,
        text="Gender",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=4,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=7
    )

    gender = ttk.Combobox(
        form,
        values=[
            "Male",
            "Female",
            "Other",
            "Prefer not to say"
        ],
        state="readonly",
        style="Patient.TCombobox",
        font=("Segoe UI", 9)
    )

    gender.grid(
        row=4,
        column=1,
        sticky="ew",
        padx=(0, 18),
        pady=6
    )

    for col in range(4):
        form.columnconfigure(col, weight=1)

    # ========================================================
    # SEARCH
    # ========================================================

    search_frame = tk.Frame(parent, bg=BG)
    search_frame.pack(fill="x", pady=(0, 10))

    tk.Label(
        search_frame,
        text="Search Patients",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=(0, 10))

    search_entry = ttk.Entry(
        search_frame,
        width=32,
        style="Patient.TEntry"
    )
    search_entry.pack(side="left", padx=(0, 8))

    # ========================================================
    # PATIENT TABLE
    # ========================================================

    table_card = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    table_card.pack(
        fill="both",
        expand=True,
        pady=(0, 10)
    )

    table_header = tk.Frame(table_card, bg=WHITE)
    table_header.pack(fill="x", padx=15, pady=(12, 8))

    tk.Label(
        table_header,
        text="Registered Patients",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(side="left")

    record_count = tk.Label(
        table_header,
        text="0 records",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9)
    )
    record_count.pack(side="right")

    table_frame = tk.Frame(table_card, bg=WHITE)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 12)
    )

    columns = (
        "ID",
        "Name",
        "DOB",
        "Gender",
        "Phone",
        "Email",
        "Blood Group"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=7,
        style="Patient.Treeview"
    )

    widths = {
        "ID": 55,
        "Name": 170,
        "DOB": 105,
        "Gender": 110,
        "Phone": 125,
        "Email": 190,
        "Blood Group": 95
    }

    for col in columns:
        table.heading(col, text=col)
        table.column(
            col,
            width=widths[col],
            minwidth=65,
            anchor="center",
            stretch=True
        )

    vertical_scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=table.xview
    )

    table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    table.grid(row=0, column=0, sticky="nsew")
    vertical_scroll.grid(row=0, column=1, sticky="ns")
    horizontal_scroll.grid(row=1, column=0, sticky="ew")

    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    # ========================================================
    # LOAD PATIENTS
    # ========================================================

    def load_patients(keyword=""):
        for item in table.get_children():
            table.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            search_pattern = f"%{keyword.strip()}%"

            cursor.execute(
                """
                SELECT
                    patient_id,
                    full_name,
                    dob,
                    gender,
                    phone,
                    email,
                    blood_group
                FROM Patient
                WHERE CAST(patient_id AS TEXT) LIKE ?
                   OR full_name LIKE ?
                   OR phone LIKE ?
                   OR email LIKE ?
                ORDER BY patient_id DESC
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern
                )
            )

            records = cursor.fetchall()

            for record in records:
                table.insert(
                    "",
                    "end",
                    values=record
                )

            record_count.config(
                text=f"{len(records)} records"
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load patient records:\n{error}",
                parent=parent
            )

        finally:
            if conn:
                conn.close()

    # ========================================================
    # CLEAR FORM
    # ========================================================

    def clear_form():
        nonlocal selected_id

        selected_id = None

        for entry in fields.values():
            entry.delete(0, tk.END)

        gender.set("")
        table.selection_remove(table.selection())

    # ========================================================
    # VALIDATE FORM
    # ========================================================

    def get_form_values():
        values = {
            key: entry.get().strip()
            for key, entry in fields.items()
        }

        values["gender"] = gender.get().strip()

        if not values["full_name"] or not values["dob"]:
            messagebox.showwarning(
                "Missing Information",
                "Patient name and date of birth are required.",
                parent=parent
            )
            return None

        try:
            dob = datetime.strptime(
                values["dob"],
                "%Y-%m-%d"
            ).date()

            if dob > date.today():
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "It cannot be in the future.",
                parent=parent
            )
            return None

        if values["phone"] and not valid_phone(values["phone"]):
            messagebox.showerror(
                "Invalid Phone",
                "Enter a valid phone number containing 10 to 15 digits.",
                parent=parent
            )
            return None

        if values["email"] and not valid_email(values["email"]):
            messagebox.showerror(
                "Invalid Email",
                "Enter a valid email address.",
                parent=parent
            )
            return None

        return values

    # ========================================================
    # ADD PATIENT
    # ========================================================

    def add_patient():
        values = get_form_values()

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO Patient (
                    full_name,
                    dob,
                    gender,
                    phone,
                    email,
                    address,
                    blood_group
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["full_name"],
                    values["dob"],
                    values["gender"],
                    values["phone"],
                    values["email"],
                    values["address"],
                    values["blood_group"]
                )
            )

            patient_id = cursor.lastrowid
            conn.commit()

            messagebox.showinfo(
                "Patient Registered",
                f"Patient registered successfully.\nPatient ID: {patient_id}",
                parent=parent
            )

            clear_form()
            load_patients(search_entry.get())

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

    # ========================================================
    # SELECT PATIENT
    # ========================================================

    def select_patient(event=None):
        nonlocal selected_id

        selected = table.selection()

        if not selected:
            return

        record = table.item(selected[0])["values"]

        if not record:
            return

        selected_id = record[0]
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    full_name,
                    dob,
                    gender,
                    phone,
                    email,
                    address,
                    blood_group
                FROM Patient
                WHERE patient_id = ?
                """,
                (selected_id,)
            )

            patient = cursor.fetchone()

            if patient:
                mapping = {
                    "full_name": patient[0],
                    "dob": patient[1],
                    "phone": patient[3],
                    "email": patient[4],
                    "address": patient[5],
                    "blood_group": patient[6]
                }

                for key, value in mapping.items():
                    fields[key].delete(0, tk.END)
                    fields[key].insert(0, value or "")

                gender.set(patient[2] or "")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not retrieve patient information:\n{error}",
                parent=parent
            )

        finally:
            if conn:
                conn.close()

    table.bind(
        "<<TreeviewSelect>>",
        select_patient
    )

    # ========================================================
    # UPDATE PATIENT
    # ========================================================

    def update_patient():
        if selected_id is None:
            messagebox.showwarning(
                "Select Patient",
                "Select a patient from the table before updating.",
                parent=parent
            )
            return

        values = get_form_values()

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE Patient
                SET
                    full_name = ?,
                    dob = ?,
                    gender = ?,
                    phone = ?,
                    email = ?,
                    address = ?,
                    blood_group = ?
                WHERE patient_id = ?
                """,
                (
                    values["full_name"],
                    values["dob"],
                    values["gender"],
                    values["phone"],
                    values["email"],
                    values["address"],
                    values["blood_group"],
                    selected_id
                )
            )

            if cursor.rowcount == 0:
                messagebox.showwarning(
                    "Patient Not Found",
                    "This patient record no longer exists.",
                    parent=parent
                )
                conn.rollback()
                clear_form()
                load_patients()
                return

            conn.commit()

            messagebox.showinfo(
                "Updated",
                "Patient information updated successfully.",
                parent=parent
            )

            clear_form()
            load_patients(search_entry.get())

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

    # ========================================================
    # DELETE PATIENT
    # ========================================================

    def delete_patient():
        if selected_id is None:
            messagebox.showwarning(
                "Select Patient",
                "Select a patient from the table before deleting.",
                parent=parent
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this patient record?\n\n"
            "Records linked to appointments, assessments, accounts, "
            "or vaccinations may prevent deletion.",
            parent=parent
        )

        if not confirm:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM Patient
                WHERE patient_id = ?
                """,
                (selected_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Deleted",
                "Patient record deleted successfully.",
                parent=parent
            )

            clear_form()
            load_patients(search_entry.get())

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Cannot Delete Patient",
                "This patient has linked records such as appointments, "
                "eligibility assessments, vaccination history, or a login "
                "account.\n\n"
                "The database has protected these records. Preserve the "
                "patient's medical history instead of deleting the record.",
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

    # ========================================================
    # BUTTONS
    # ========================================================

    button_frame = tk.Frame(parent, bg=BG)
    button_frame.pack(fill="x", pady=(0, 5))

    def create_button(text, command, color, active_color=None):
        return tk.Button(
            button_frame,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=active_color or color,
            activeforeground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=9
        )

    create_button(
        "Add Patient",
        add_patient,
        BLUE,
        BLUE_DARK
    ).pack(side="left", padx=(0, 7))

    create_button(
        "Update",
        update_patient,
        GREEN
    ).pack(side="left", padx=7)

    create_button(
        "Delete",
        delete_patient,
        RED
    ).pack(side="left", padx=7)

    create_button(
        "Clear Form",
        clear_form,
        NAVY
    ).pack(side="left", padx=7)

    create_button(
        "Search",
        lambda: load_patients(search_entry.get()),
        BLUE
    ).pack(side="left", padx=7)

    create_button(
        "Refresh",
        lambda: refresh_patients(),
        MUTED
    ).pack(side="left", padx=7)

    def refresh_patients():
        search_entry.delete(0, tk.END)
        clear_form()
        load_patients()

    search_entry.bind(
        "<Return>",
        lambda event: load_patients(search_entry.get())
    )

    # INITIAL LOAD
    load_patients()
