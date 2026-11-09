
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

# ---------------- DATABASE ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ---------------- COLORS ----------------
NAVY = "#172B4D"
BLUE = "#2878D0"
BG = "#F3F6FB"
WHITE = "#FFFFFF"
TEXT = "#243247"
MUTED = "#718096"
GREEN = "#159D79"
RED = "#D9534F"
BORDER = "#E3EAF3"

# ---------------- ELIGIBILITY MANAGEMENT ----------------
def show_eligibility(parent, page_title, clear_content, account):
    # ---------------- ACCESS CONTROL ----------------
    if not account or account.get("role") not in ("admin", "staff"):
        messagebox.showerror(
            "Access Denied",
            "Only administrators and registered doctors can access eligibility management."
        )
        return

    role = account.get("role")
    staff_id = account.get("staff_id")

    current_doctor_id = None
    doctors = []
    patients = []

    # ---------------- LOAD INITIAL DATA ----------------
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                patient_id,
                full_name,
                dob,
                gender,
                phone
            FROM Patient
            ORDER BY full_name
        """)
        patients = cursor.fetchall()

        cursor.execute("""
            SELECT
                D.doctor_id,
                S.full_name,
                D.specialization
            FROM Doctor D
            JOIN Staff S ON D.staff_id = S.staff_id
            ORDER BY S.full_name
        """)
        doctors = cursor.fetchall()

        if role == "staff":
            if not staff_id:
                messagebox.showerror(
                    "Access Denied",
                    "Your staff account is not linked to a doctor."
                )
                return

            cursor.execute("""
                SELECT doctor_id
                FROM Doctor
                WHERE staff_id = ?
            """, (staff_id,))

            result = cursor.fetchone()

            if result:
                current_doctor_id = result[0]

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to load eligibility information.\n\n{error}"
        )
        return

    finally:
        if conn:
            conn.close()

    if role == "staff" and current_doctor_id is None:
        clear_content()

        tk.Label(
            parent,
            text="Eligibility assessments can only be recorded by a registered doctor.",
            bg=BG,
            fg=RED,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=20)

        tk.Label(
            parent,
            text="Your staff account is not linked to a Doctor record. Please ask the administrator to review your account.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        return

    clear_content()
    page_title.config(text="Eligibility Management")

    # ---------------- EMPTY PATIENT LIST ----------------
    if not patients:
        tk.Label(
            parent,
            text="No registered patients are available.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=20)
        return

    if role == "admin" and not doctors:
        tk.Label(
            parent,
            text="No registered doctors are available.",
            bg=BG,
            fg=RED,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=20)

        tk.Label(
            parent,
            text="A registered doctor must be available before an assessment can be recorded.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

    # ---------------- HEADER ----------------
    heading = tk.Frame(parent, bg=BG)
    heading.pack(fill="x", pady=(0, 12))

    tk.Label(
        heading,
        text="Patient Eligibility Assessment",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 19, "bold")
    ).pack(anchor="w")

    tk.Label(
        heading,
        text="Review patient history and record a doctor's clinical assessment.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 0))

    # ---------------- MAIN BODY ----------------
    body = tk.Frame(parent, bg=BG)
    body.pack(fill="both", expand=True)

    # =========================================================
    # LEFT: PATIENT LIST
    # =========================================================
    left = tk.Frame(
        body,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
        width=290
    )
    left.pack(side="left", fill="y", padx=(0, 12))
    left.pack_propagate(False)

    tk.Label(
        left,
        text="Registered Patients",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", padx=15, pady=(13, 10))

    search_var = tk.StringVar()

    search_entry = ttk.Entry(
        left,
        textvariable=search_var
    )
    search_entry.pack(
        fill="x",
        padx=12,
        pady=(0, 10)
    )

    search_entry.insert(0, "Search by name or ID...")

    patient_table_frame = tk.Frame(left, bg=WHITE)
    patient_table_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 12)
    )

    patient_table = ttk.Treeview(
        patient_table_frame,
        columns=("ID", "Name"),
        show="headings",
        height=18,
        selectmode="browse"
    )

    patient_table.heading("ID", text="ID")
    patient_table.heading("Name", text="Patient Name")

    patient_table.column(
        "ID",
        width=48,
        minwidth=45,
        anchor="center",
        stretch=False
    )
    patient_table.column(
        "Name",
        width=205,
        minwidth=120,
        anchor="w"
    )

    patient_scroll = ttk.Scrollbar(
        patient_table_frame,
        orient="vertical",
        command=patient_table.yview
    )

    patient_table.configure(
        yscrollcommand=patient_scroll.set
    )

    patient_table.pack(side="left", fill="both", expand=True)
    patient_scroll.pack(side="right", fill="y")

    # =========================================================
    # RIGHT: PATIENT HISTORY AND ASSESSMENT
    # =========================================================
    right = tk.Frame(body, bg=BG)
    right.pack(side="left", fill="both", expand=True)

    # ---------------- PATIENT HISTORY ----------------
    history_frame = tk.Frame(
        right,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    history_frame.pack(
        fill="both",
        expand=True,
        pady=(0, 10)
    )

    tk.Label(
        history_frame,
        text="Patient Medical History",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    history_container = tk.Frame(history_frame, bg=WHITE)
    history_container.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 12)
    )

    history_text = tk.Text(
        history_container,
        height=10,
        wrap="word",
        font=("Segoe UI", 9),
        bg="#FAFBFD",
        fg=TEXT,
        relief="flat",
        padx=10,
        pady=8,
        state="disabled"
    )

    history_scroll = ttk.Scrollbar(
        history_container,
        orient="vertical",
        command=history_text.yview
    )

    history_text.configure(
        yscrollcommand=history_scroll.set
    )

    history_text.pack(side="left", fill="both", expand=True)
    history_scroll.pack(side="right", fill="y")

    # ---------------- ASSESSMENT FORM ----------------
    assessment_frame = tk.Frame(
        right,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    assessment_frame.pack(fill="x")

    tk.Label(
        assessment_frame,
        text="Record Eligibility Assessment",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="w",
        padx=15,
        pady=(12, 8)
    )

    selected_patient_var = tk.StringVar(
        value="No patient selected"
    )

    tk.Label(
        assessment_frame,
        textvariable=selected_patient_var,
        bg=WHITE,
        fg=BLUE,
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="w",
        padx=15,
        pady=5
    )

    doctor_var = tk.StringVar()
    risk_var = tk.StringVar(value="Select Risk Category")
    status_var = tk.StringVar(value="Select Eligibility Status")
    reason_var = tk.StringVar()

    row = 2

    # ---------------- ASSESSING DOCTOR ----------------
    if role == "admin":
        doctor_options = {
            f"{doctor[1]} - {doctor[2]} (ID: {doctor[0]})": doctor[0]
            for doctor in doctors
        }

        tk.Label(
            assessment_frame,
            text="Assessing Doctor:",
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=15,
            pady=6
        )

        doctor_combo = ttk.Combobox(
            assessment_frame,
            textvariable=doctor_var,
            values=list(doctor_options.keys()),
            state="readonly",
            width=35
        )

        doctor_combo.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=15,
            pady=6
        )

    else:
        doctor_options = {}

        doctor_name = next(
            (
                doctor[1]
                for doctor in doctors
                if doctor[0] == current_doctor_id
            ),
            "Doctor"
        )

        doctor_var.set(str(current_doctor_id))

        tk.Label(
            assessment_frame,
            text="Assessing Doctor:",
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=15,
            pady=6
        )

        tk.Label(
            assessment_frame,
            text=doctor_name,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 9)
        ).grid(
            row=row,
            column=1,
            sticky="w",
            padx=15,
            pady=6
        )

    row += 1

    # ---------------- RISK CATEGORY ----------------
    tk.Label(
        assessment_frame,
        text="Risk Category:",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=row,
        column=0,
        sticky="w",
        padx=15,
        pady=6
    )

    risk_combo = ttk.Combobox(
        assessment_frame,
        textvariable=risk_var,
        values=["Low", "Moderate", "High", "Very High"],
        state="readonly",
        width=35
    )

    risk_combo.grid(
        row=row,
        column=1,
        sticky="ew",
        padx=15,
        pady=6
    )

    row += 1

    # ---------------- ELIGIBILITY STATUS ----------------
    tk.Label(
        assessment_frame,
        text="Eligibility Status:",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=row,
        column=0,
        sticky="w",
        padx=15,
        pady=6
    )

    status_combo = ttk.Combobox(
        assessment_frame,
        textvariable=status_var,
        values=["Eligible", "Not Eligible", "Pending Review"],
        state="readonly",
        width=35
    )

    status_combo.grid(
        row=row,
        column=1,
        sticky="ew",
        padx=15,
        pady=6
    )

    row += 1

    # ---------------- REASON ----------------
    tk.Label(
        assessment_frame,
        text="Reason:",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=row,
        column=0,
        sticky="w",
        padx=15,
        pady=6
    )

    reason_entry = ttk.Entry(
        assessment_frame,
        textvariable=reason_var,
        width=40
    )

    reason_entry.grid(
        row=row,
        column=1,
        sticky="ew",
        padx=15,
        pady=6
    )

    row += 1

    # ---------------- CLINICAL NOTES ----------------
    tk.Label(
        assessment_frame,
        text="Clinical Notes:",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=row,
        column=0,
        sticky="nw",
        padx=15,
        pady=6
    )

    notes_entry = tk.Text(
        assessment_frame,
        height=3,
        width=40,
        font=("Segoe UI", 9),
        wrap="word",
        relief="solid",
        borderwidth=1
    )

    notes_entry.grid(
        row=row,
        column=1,
        sticky="ew",
        padx=15,
        pady=6
    )

    row += 1
    assessment_frame.columnconfigure(1, weight=1)

    selected_patient_id = {"value": None}

    # =========================================================
    # HISTORY DISPLAY
    # =========================================================
    def set_history(content):
        history_text.config(state="normal")
        history_text.delete("1.0", tk.END)
        history_text.insert("1.0", content)
        history_text.config(state="disabled")

    def load_patient_history(patient_id):
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
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
            """, (patient_id,))

            patient = cursor.fetchone()

            if not patient:
                set_history("Patient record could not be found.")
                return

            cursor.execute("""
                SELECT allergy_name, reaction, severity
                FROM Patient_Allergy
                WHERE patient_id = ?
                ORDER BY recorded_at DESC
            """, (patient_id,))
            allergies = cursor.fetchall()

            cursor.execute("""
                SELECT history_type, details, recorded_date
                FROM Patient_Medical_History
                WHERE patient_id = ?
                ORDER BY recorded_date DESC
            """, (patient_id,))
            medical_history = cursor.fetchall()

            cursor.execute("""
                SELECT
                    vaccine_name,
                    vaccination_date,
                    dose_number,
                    administered_elsewhere,
                    notes
                FROM Patient_Vaccine_History
                WHERE patient_id = ?
                ORDER BY vaccination_date DESC
            """, (patient_id,))
            previous_vaccines = cursor.fetchall()

            cursor.execute("""
                SELECT
                    V.vaccine_name,
                    VR.dose_number,
                    VR.date_administered,
                    VR.next_due_date
                FROM Vaccination VR
                JOIN Vaccine V
                    ON VR.vaccine_id = V.vaccine_id
                WHERE VR.patient_id = ?
                ORDER BY VR.date_administered DESC
            """, (patient_id,))
            recorded_vaccines = cursor.fetchall()

            cursor.execute("""
                SELECT
                    E.assessment_date,
                    E.risk_category,
                    E.eligibility_status,
                    E.reason,
                    S.full_name
                FROM Eligibility_Assessment E
                JOIN Doctor D
                    ON E.assessed_by = D.doctor_id
                JOIN Staff S
                    ON D.staff_id = S.staff_id
                WHERE E.patient_id = ?
                ORDER BY E.assessment_date DESC, E.assessment_id DESC
            """, (patient_id,))
            previous_assessments = cursor.fetchall()

        except sqlite3.Error as error:
            set_history(
                f"Unable to load patient history.\n\n{error}"
            )
            return

        finally:
            if conn:
                conn.close()

        lines = [
            f"PATIENT: {patient[0]}",
            f"Date of Birth: {patient[1]}",
            f"Gender: {patient[2]}",
            f"Phone: {patient[3]}",
            f"Email: {patient[4] or 'Not provided'}",
            f"Address: {patient[5] or 'Not provided'}",
            f"Blood Group: {patient[6] or 'Not provided'}",
            "",
            "ALLERGIES"
        ]

        if allergies:
            for allergy in allergies:
                lines.append(
                    f"- {allergy[0]} | Reaction: {allergy[1] or 'Not provided'} "
                    f"| Severity: {allergy[2] or 'Unknown'}"
                )
        else:
            lines.append("No allergies recorded.")

        lines.extend(["", "MEDICAL HISTORY"])

        if medical_history:
            for item in medical_history:
                lines.append(
                    f"- {item[0]} ({item[2]}): {item[1]}"
                )
        else:
            lines.append("No medical history recorded.")

        lines.extend([
            "",
            "PREVIOUS VACCINATIONS REPORTED AT REGISTRATION"
        ])

        if previous_vaccines:
            for item in previous_vaccines:
                lines.append(
                    f"- {item[0]} | Date: {item[1]} | Dose: {item[2]} "
                    f"| Administered elsewhere: {item[3]} "
                    f"| Notes: {item[4] or 'None'}"
                )
        else:
            lines.append("No previous vaccination history reported.")

        lines.extend([
            "",
            "VACCINATIONS RECORDED IN PNEUMOCARE"
        ])

        if recorded_vaccines:
            for item in recorded_vaccines:
                lines.append(
                    f"- {item[0]} | Dose: {item[1]} | Date: {item[2]} "
                    f"| Next due: {item[3] or 'Not recorded'}"
                )
        else:
            lines.append("No PneumoCare vaccination records.")

        lines.extend([
            "",
            "PREVIOUS ELIGIBILITY ASSESSMENTS"
        ])

        if previous_assessments:
            for item in previous_assessments:
                lines.append(
                    f"- {item[0]} | {item[1]} risk | {item[2]} "
                    f"| Doctor: {item[4]} | Reason: {item[3] or 'Not recorded'}"
                )
        else:
            lines.append("No previous assessments.")

        set_history("\n".join(lines))

    # =========================================================
    # PATIENT SELECTION AND SEARCH
    # =========================================================
    def select_patient(event=None):
        selection = patient_table.selection()

        if not selection:
            return

        values = patient_table.item(
            selection[0],
            "values"
        )

        patient_id = int(values[0])

        selected_patient_id["value"] = patient_id

        selected_patient_var.set(
            f"Selected Patient: {values[1]} (ID: {patient_id})"
        )

        load_patient_history(patient_id)

    def refresh_patient_list(*args):
        query = search_var.get().strip().lower()

        if query == "search by name or id...":
            query = ""

        for item in patient_table.get_children():
            patient_table.delete(item)

        for patient in patients:
            name = str(patient[1]).lower()
            patient_id = str(patient[0])

            if not query or query in name or query in patient_id:
                patient_table.insert(
                    "",
                    "end",
                    values=(patient[0], patient[1])
                )

    patient_table.bind(
        "<<TreeviewSelect>>",
        select_patient
    )

    search_var.trace_add(
        "write",
        refresh_patient_list
    )

    refresh_patient_list()

    # =========================================================
    # SAVE ASSESSMENT
    # =========================================================
    def save_assessment():
        patient_id = selected_patient_id["value"]

        if not patient_id:
            messagebox.showwarning(
                "Select Patient",
                "Please select a patient first."
            )
            return

        if role == "admin":
            doctor_id = doctor_options.get(doctor_var.get())
        else:
            doctor_id = current_doctor_id

        if not doctor_id:
            messagebox.showwarning(
                "Select Doctor",
                "Please select a registered doctor."
            )
            return

        risk = risk_var.get()
        status = status_var.get()
        reason = reason_var.get().strip()
        notes = notes_entry.get("1.0", "end").strip()

        if risk not in ("Low", "Moderate", "High", "Very High"):
            messagebox.showwarning(
                "Missing Information",
                "Please select a risk category."
            )
            return

        if status not in ("Eligible", "Not Eligible", "Pending Review"):
            messagebox.showwarning(
                "Missing Information",
                "Please select an eligibility status."
            )
            return

        if not reason:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the reason for this assessment."
            )
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("BEGIN IMMEDIATE")

            # Confirm that the selected patient still exists.
            cursor.execute("""
                SELECT patient_id
                FROM Patient
                WHERE patient_id = ?
            """, (patient_id,))

            if not cursor.fetchone():
                raise sqlite3.Error(
                    "The selected patient record no longer exists."
                )

            # Confirm that the assessing doctor still exists.
            cursor.execute("""
                SELECT doctor_id
                FROM Doctor
                WHERE doctor_id = ?
            """, (doctor_id,))

            if not cursor.fetchone():
                raise sqlite3.Error(
                    "The selected doctor record no longer exists."
                )

            # Staff accounts may only record assessments
            # under their own linked Doctor record.
            if role == "staff":
                cursor.execute("""
                    SELECT doctor_id
                    FROM Doctor
                    WHERE doctor_id = ?
                      AND staff_id = ?
                """, (doctor_id, staff_id))

                if not cursor.fetchone():
                    raise sqlite3.Error(
                        "Your account is not authorized to use this doctor record."
                    )

            cursor.execute("""
                INSERT INTO Eligibility_Assessment (
                    patient_id,
                    assessed_by,
                    assessment_date,
                    risk_category,
                    eligibility_status,
                    reason,
                    clinical_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                doctor_id,
                date.today().isoformat(),
                risk,
                status,
                reason,
                notes
            ))

            conn.commit()

            messagebox.showinfo(
                "Assessment Saved",
                "The eligibility assessment has been recorded successfully."
            )

            clear_assessment_form()
            load_patient_history(patient_id)

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Save Error",
                f"Could not save the assessment.\n\n{error}"
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:
            if conn:
                conn.close()

    # =========================================================
    # CLEAR ASSESSMENT FORM
    # =========================================================
    def clear_assessment_form():
        risk_var.set("Select Risk Category")
        status_var.set("Select Eligibility Status")
        reason_var.set("")
        notes_entry.delete("1.0", tk.END)

        if role == "admin":
            doctor_var.set("")

    # ---------------- BUTTONS ----------------
    buttons = tk.Frame(assessment_frame, bg=WHITE)
    buttons.grid(
        row=row,
        column=0,
        columnspan=2,
        pady=12
    )

    tk.Button(
        buttons,
        text="Save Assessment",
        command=save_assessment,
        bg=BLUE,
        fg=WHITE,
        activebackground=NAVY,
        activeforeground=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        padx=20,
        pady=9
    ).pack(side="left", padx=6)

    tk.Button(
        buttons,
        text="Clear Assessment",
        command=clear_assessment_form,
        bg="#EAF0F8",
        fg=BLUE,
        activebackground="#DCE7F5",
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        padx=15,
        pady=9
    ).pack(side="left", padx=6)

    # ---------------- INITIAL HISTORY MESSAGE ----------------
    set_history(
        "Select a patient from the list to view their medical history, "
        "allergies, vaccination records and previous eligibility assessments."
    )
