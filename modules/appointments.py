
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ---------------- DATABASE ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ---------------- COLORS ----------------
BG = "#F3F6FB"
WHITE = "#FFFFFF"
NAVY = "#172B4D"
BLUE = "#2878D0"
GREEN = "#159D79"
RED = "#D9534F"
TEXT = "#243247"
MUTED = "#718096"
BORDER = "#E3EAF3"

# ---------------- SHARED HELPERS ----------------
def make_button(parent, text, command, bg, fg=WHITE):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
        padx=13,
        pady=8
    )

def make_table(parent, columns, widths):
    frame = tk.Frame(parent, bg=WHITE)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for column in columns:
        tree.heading(column, text=column)
        tree.column(
            column,
            width=widths[column],
            minwidth=65,
            anchor="center",
            stretch=False
        )

    vertical = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )
    horizontal = ttk.Scrollbar(
        frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=vertical.set,
        xscrollcommand=horizontal.set
    )

    tree.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    return tree

def valid_appointment_datetime(date_value, time_value):
    try:
        value = datetime.strptime(
            f"{date_value.strip()} {time_value.strip()}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return None, "Enter the date as YYYY-MM-DD and time as HH:MM."

    if value <= datetime.now():
        return None, "Choose a future appointment time."

    if value.weekday() == 6:
        return None, "The clinic is closed on Sundays."

    if not (9 <= value.hour < 17):
        return None, "Appointments are available between 9:00 AM and 4:30 PM."

    if value.minute not in (0, 30):
        return None, "Appointments must use 30-minute time slots."

    return value, None

# ============================================================
# ADMIN AND DOCTOR APPOINTMENT MANAGEMENT
# ============================================================
def show_appointments(parent, page_title, clear_content, account):

    if not account or account.get("role") not in ("admin", "staff"):
        messagebox.showerror(
            "Access Denied",
            "You are not allowed to manage appointments."
        )
        return

    is_admin = account["role"] == "admin"
    doctor_id = None

    # ---------------- DOCTOR ACCESS CHECK ----------------
    if not is_admin:
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT doctor_id
                FROM Doctor
                WHERE staff_id = ?
            """, (account.get("staff_id"),))

            result = cursor.fetchone()

            if not result:
                messagebox.showerror(
                    "Access Denied",
                    "Only registered doctors can manage appointments."
                )
                return

            doctor_id = result[0]

        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            if conn:
                conn.close()

    clear_content()
    page_title.config(text="Appointment Management")

    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    heading = "All Appointments" if is_admin else "My Patient Appointments"

    tk.Label(
        main,
        text=heading,
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 19, "bold")
    ).pack(anchor="w")

    tk.Label(
        main,
        text="View, reschedule and manage scheduled appointments.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 10))

    # ---------------- FORM ----------------
    form = tk.Frame(
        main,
        bg=WHITE,
        padx=18,
        pady=14,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 12))

    patient_var = tk.StringVar()
    doctor_var = tk.StringVar()
    date_var = tk.StringVar()
    time_var = tk.StringVar()

    patients = {}
    doctors = {}

    patient_combo = ttk.Combobox(
        form,
        textvariable=patient_var,
        state="disabled",
        width=29
    )

    doctor_combo = ttk.Combobox(
        form,
        textvariable=doctor_var,
        state="readonly" if is_admin else "disabled",
        width=29
    )

    date_entry = ttk.Entry(form, textvariable=date_var, width=22)
    time_entry = ttk.Entry(form, textvariable=time_var, width=22)

    fields = [
        ("Patient", patient_combo, 1, 0),
        ("Doctor", doctor_combo, 1, 2),
        ("New Date (YYYY-MM-DD)", date_entry, 2, 0),
        ("New Time (HH:MM)", time_entry, 2, 2)
    ]

    for label, widget, row, column in fields:
        tk.Label(
            form,
            text=label,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(
            row=row,
            column=column,
            sticky="w",
            padx=(0, 8),
            pady=7
        )

        widget.grid(
            row=row,
            column=column + 1,
            sticky="ew",
            padx=(0, 18),
            pady=7
        )

    tk.Label(
        form,
        text="Appointment Notes",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 9, "bold")
    ).grid(
        row=3,
        column=0,
        sticky="nw",
        pady=6
    )

    notes_text = tk.Text(
        form,
        height=2,
        width=55,
        font=("Segoe UI", 9),
        wrap="word",
        state="disabled"
    )
    notes_text.grid(
        row=3,
        column=1,
        columnspan=3,
        sticky="ew",
        pady=6
    )

    for column in range(4):
        form.grid_columnconfigure(
            column,
            weight=1 if column in (1, 3) else 0
        )

    # ---------------- APPOINTMENT TABLE ----------------
    table_card = tk.Frame(
        main,
        bg=WHITE,
        padx=12,
        pady=12,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    table_card.pack(fill="both", expand=True)

    tk.Label(
        table_card,
        text="Appointment Records",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", pady=(0, 10))

    columns = (
        "ID",
        "Patient",
        "Doctor",
        "Date & Time",
        "Status",
        "Notes"
    )

    tree = make_table(
        table_card,
        columns,
        {
            "ID": 60,
            "Patient": 165,
            "Doctor": 165,
            "Date & Time": 155,
            "Status": 110,
            "Notes": 250
        }
    )

    # ---------------- LOAD DROPDOWNS ----------------
    def load_dropdowns():
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT patient_id, full_name
                FROM Patient
                ORDER BY full_name
            """)

            patients.clear()
            patients.update({
                f"{row[0]} - {row[1]}": row[0]
                for row in cursor.fetchall()
            })

            cursor.execute("""
                SELECT D.doctor_id, S.full_name
                FROM Doctor D
                JOIN Staff S ON D.staff_id = S.staff_id
                ORDER BY S.full_name
            """)

            doctors.clear()
            doctors.update({
                f"{row[0]} - {row[1]}": row[0]
                for row in cursor.fetchall()
            })

            patient_combo["values"] = list(patients.keys())
            doctor_combo["values"] = list(doctors.keys())

            if not is_admin:
                doctor_var.set(
                    next(
                        (
                            name for name, value in doctors.items()
                            if value == doctor_id
                        ),
                        ""
                    )
                )

        finally:
            if conn:
                conn.close()

    # ---------------- LOAD APPOINTMENTS ----------------
    def load_appointments():
        for item in tree.get_children():
            tree.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT
                    A.appointment_id,
                    P.full_name,
                    S.full_name,
                    A.appointment_datetime,
                    A.status,
                    COALESCE(A.notes, '')
                FROM Appointment A
                JOIN Patient P ON A.patient_id = P.patient_id
                JOIN Doctor D ON A.doctor_id = D.doctor_id
                JOIN Staff S ON D.staff_id = S.staff_id
            """

            params = ()

            if not is_admin:
                query += " WHERE A.doctor_id = ?"
                params = (doctor_id,)

            query += " ORDER BY A.appointment_datetime DESC"

            cursor.execute(query, params)

            for record in cursor.fetchall():
                tree.insert("", "end", values=record)

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:
            if conn:
                conn.close()

    # ---------------- CLEAR FORM ----------------
    def clear_form():
        patient_var.set("")

        if is_admin:
            doctor_var.set("")
        else:
            doctor_var.set(
                next(
                    (
                        name for name, value in doctors.items()
                        if value == doctor_id
                    ),
                    ""
                )
            )

        date_var.set("")
        time_var.set("")

        notes_text.config(state="normal")
        notes_text.delete("1.0", tk.END)
        notes_text.config(state="disabled")

        for item in tree.selection():
            tree.selection_remove(item)

    # ---------------- SELECT APPOINTMENT ----------------
    def select_appointment(event=None):
        selected = tree.selection()

        if not selected:
            return

        appointment_id = tree.item(
            selected[0],
            "values"
        )[0]

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    patient_id,
                    doctor_id,
                    appointment_datetime,
                    status,
                    notes
                FROM Appointment
                WHERE appointment_id = ?
            """, (appointment_id,))

            record = cursor.fetchone()

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )
            return

        finally:
            if conn:
                conn.close()

        if not record:
            return

        patient_var.set(
            next(
                (
                    name for name, value in patients.items()
                    if value == record[0]
                ),
                ""
            )
        )

        doctor_var.set(
            next(
                (
                    name for name, value in doctors.items()
                    if value == record[1]
                ),
                ""
            )
        )

        appointment_datetime = record[2] or ""

        try:
            appointment_date, appointment_time = appointment_datetime.split(" ", 1)
        except ValueError:
            appointment_date = appointment_datetime
            appointment_time = ""

        date_var.set(appointment_date)
        time_var.set(appointment_time[:5])

        notes_text.config(state="normal")
        notes_text.delete("1.0", tk.END)
        notes_text.insert("1.0", record[4] or "")
        notes_text.config(state="disabled")

        if record[3] != "Scheduled":
            messagebox.showinfo(
                "Appointment Status",
                f"This appointment is {record[3]}. "
                "Only scheduled appointments can be rescheduled."
            )

    tree.bind(
        "<<TreeviewSelect>>",
        select_appointment
    )

    # ---------------- RESCHEDULE APPOINTMENT ----------------
    def reschedule_appointment():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select an appointment first."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        appointment_id = values[0]

        if values[4] != "Scheduled":
            messagebox.showwarning(
                "Cannot Reschedule",
                "Only scheduled appointments can be rescheduled."
            )
            return

        new_doctor_id = (
            doctors.get(doctor_var.get())
            if is_admin else doctor_id
        )

        if not new_doctor_id:
            messagebox.showwarning(
                "Missing Doctor",
                "Select a registered doctor."
            )
            return

        new_datetime, error_message = valid_appointment_datetime(
            date_var.get(),
            time_var.get()
        )

        if error_message:
            messagebox.showwarning(
                "Invalid Appointment Time",
                error_message
            )
            return

        appointment_datetime = new_datetime.strftime(
            "%Y-%m-%d %H:%M"
        )

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("BEGIN IMMEDIATE")

            cursor.execute("""
                SELECT COUNT(*)
                FROM Appointment
                WHERE doctor_id = ?
                  AND datetime(appointment_datetime) = datetime(?)
                  AND status = 'Scheduled'
                  AND appointment_id <> ?
            """, (
                new_doctor_id,
                appointment_datetime,
                appointment_id
            ))

            if cursor.fetchone()[0] > 0:
                conn.rollback()

                messagebox.showwarning(
                    "Slot Unavailable",
                    "This doctor already has an appointment at that time."
                )
                return

            # Recheck ownership and status during the update.
            if is_admin:
                cursor.execute("""
                    UPDATE Appointment
                    SET doctor_id = ?, appointment_datetime = ?
                    WHERE appointment_id = ?
                      AND status = 'Scheduled'
                """, (
                    new_doctor_id,
                    appointment_datetime,
                    appointment_id
                ))
            else:
                cursor.execute("""
                    UPDATE Appointment
                    SET appointment_datetime = ?
                    WHERE appointment_id = ?
                      AND doctor_id = ?
                      AND status = 'Scheduled'
                """, (
                    appointment_datetime,
                    appointment_id,
                    doctor_id
                ))

            if cursor.rowcount != 1:
                conn.rollback()

                messagebox.showwarning(
                    "Update Failed",
                    "The appointment could not be rescheduled."
                )
                return

            conn.commit()

            messagebox.showinfo(
                "Rescheduled",
                "Appointment rescheduled successfully."
            )

            load_appointments()
            clear_form()

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

    # ---------------- CANCEL APPOINTMENT ----------------
    def cancel_appointment():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select an appointment first."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        if values[4] != "Scheduled":
            messagebox.showwarning(
                "Cannot Cancel",
                "Only scheduled appointments can be cancelled."
            )
            return

        if not messagebox.askyesno(
            "Confirm Cancellation",
            f"Cancel the appointment for {values[1]}?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if is_admin:
                cursor.execute("""
                    UPDATE Appointment
                    SET status = 'Cancelled'
                    WHERE appointment_id = ?
                      AND status = 'Scheduled'
                """, (values[0],))
            else:
                cursor.execute("""
                    UPDATE Appointment
                    SET status = 'Cancelled'
                    WHERE appointment_id = ?
                      AND doctor_id = ?
                      AND status = 'Scheduled'
                """, (values[0], doctor_id))

            if cursor.rowcount != 1:
                conn.rollback()

                messagebox.showwarning(
                    "Update Failed",
                    "The appointment could not be cancelled."
                )
                return

            conn.commit()

            messagebox.showinfo(
                "Cancelled",
                "Appointment cancelled successfully."
            )

            load_appointments()
            clear_form()

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

    # ---------------- MARK COMPLETED ----------------
    def mark_completed():
        if is_admin:
            return

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select an appointment first."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        if values[4] != "Scheduled":
            messagebox.showwarning(
                "Cannot Complete",
                "Only scheduled appointments can be marked completed."
            )
            return

        if not messagebox.askyesno(
            "Confirm Completion",
            f"Mark the appointment for {values[1]} as completed?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Appointment
                SET status = 'Completed'
                WHERE appointment_id = ?
                  AND doctor_id = ?
                  AND status = 'Scheduled'
            """, (
                values[0],
                doctor_id
            ))

            if cursor.rowcount != 1:
                conn.rollback()

                messagebox.showwarning(
                    "Update Failed",
                    "The appointment could not be completed."
                )
                return

            conn.commit()

            messagebox.showinfo(
                "Completed",
                "Appointment marked as completed."
            )

            load_appointments()
            clear_form()

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

    # ---------------- ACTION BUTTONS ----------------
    buttons = tk.Frame(form, bg=WHITE)
    buttons.grid(
        row=4,
        column=0,
        columnspan=4,
        sticky="w",
        pady=(12, 0)
    )

    make_button(
        buttons,
        "Reschedule Appointment",
        reschedule_appointment,
        BLUE
    ).pack(side="left", padx=(0, 7))

    make_button(
        buttons,
        "Cancel Appointment",
        cancel_appointment,
        "#FCE8E8",
        "#A93232"
    ).pack(side="left", padx=7)

    if not is_admin:
        make_button(
            buttons,
            "Mark Completed",
            mark_completed,
            "#E3F5ED",
            GREEN
        ).pack(side="left", padx=7)

    make_button(
        buttons,
        "Clear Selection",
        clear_form,
        "#EAF0F8",
        NAVY
    ).pack(side="left", padx=7)

    make_button(
        buttons,
        "Refresh",
        load_appointments,
        "#EAF0F8",
        NAVY
    ).pack(side="left", padx=7)

    # ---------------- INITIAL LOAD ----------------
    try:
        load_dropdowns()
        load_appointments()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# PATIENT APPOINTMENT BOOKING
# ============================================================
def show_patient_booking(parent, page_title, clear_content, account):

    if (
        not account
        or account.get("role") != "patient"
        or not account.get("patient_id")
    ):
        messagebox.showerror(
            "Access Denied",
            "Only logged-in patients can book appointments."
        )
        return

    clear_content()
    page_title.config(text="Book an Appointment")

    patient_id = account["patient_id"]

    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True)

    # ---------------- BOOKING FORM ----------------
    form = tk.Frame(
        main,
        bg=WHITE,
        padx=22,
        pady=18,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    form.pack(fill="x", pady=(8, 12))

    tk.Label(
        form,
        text="Book Your Appointment",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 17, "bold")
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        form,
        text="Choose a doctor, date and available time slot.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(0, 15))

    # ---------------- LOAD DOCTORS ----------------
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                D.doctor_id,
                S.full_name,
                COALESCE(D.specialization, 'General')
            FROM Doctor D
            JOIN Staff S ON D.staff_id = S.staff_id
            ORDER BY S.full_name
        """)

        doctor_rows = cursor.fetchall()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )
        return

    finally:
        if conn:
            conn.close()

    doctor_map = {
        f"{row[1]} - {row[2]} (ID: {row[0]})": row[0]
        for row in doctor_rows
    }

    doctor_var = tk.StringVar()
    date_var = tk.StringVar(
        value=datetime.now().strftime("%Y-%m-%d")
    )
    slot_var = tk.StringVar()

    tk.Label(
        form,
        text="Select Doctor",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(5, 4))

    doctor_combo = ttk.Combobox(
        form,
        textvariable=doctor_var,
        values=list(doctor_map.keys()),
        state="readonly",
        width=43
    )
    doctor_combo.pack(anchor="w", pady=(0, 10))

    tk.Label(
        form,
        text="Appointment Date (YYYY-MM-DD)",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(5, 4))

    date_entry = ttk.Entry(
        form,
        textvariable=date_var,
        width=25
    )
    date_entry.pack(anchor="w", pady=(0, 10))

    tk.Label(
        form,
        text="Available Time Slots",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(5, 4))

    slot_combo = ttk.Combobox(
        form,
        textvariable=slot_var,
        state="readonly",
        width=25
    )
    slot_combo.pack(anchor="w", pady=(0, 8))

    availability_label = tk.Label(
        form,
        text="Select a doctor and date, then check availability.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9)
    )
    availability_label.pack(anchor="w", pady=(0, 10))

    # ---------------- GET AVAILABLE SLOTS ----------------
    def get_available_slots(doctor_id, selected_date):
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT strftime('%H:%M', appointment_datetime)
                FROM Appointment
                WHERE doctor_id = ?
                  AND status = 'Scheduled'
                  AND date(appointment_datetime) = ?
            """, (
                doctor_id,
                selected_date.isoformat()
            ))

            booked = {
                row[0]
                for row in cursor.fetchall()
                if row[0]
            }

            available = []

            for hour in range(9, 17):
                for minute in (0, 30):
                    slot_time = f"{hour:02d}:{minute:02d}"

                    slot_datetime = datetime.strptime(
                        f"{selected_date.isoformat()} {slot_time}",
                        "%Y-%m-%d %H:%M"
                    )

                    if (
                        slot_time not in booked
                        and slot_datetime > datetime.now()
                    ):
                        available.append(slot_time)

            return available

        finally:
            if conn:
                conn.close()

    # ---------------- CHECK AVAILABILITY ----------------
    def check_availability():
        slot_var.set("")
        slot_combo["values"] = []

        selected_doctor_id = doctor_map.get(
            doctor_var.get()
        )

        if not selected_doctor_id:
            messagebox.showwarning(
                "Select Doctor",
                "Please select a doctor."
            )
            return

        try:
            selected_date = datetime.strptime(
                date_var.get().strip(),
                "%Y-%m-%d"
            ).date()

        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Enter the date in YYYY-MM-DD format."
            )
            return

        today = datetime.now().date()

        if selected_date < today:
            messagebox.showwarning(
                "Invalid Date",
                "You cannot book an appointment in the past."
            )
            return

        if selected_date.weekday() == 6:
            availability_label.config(
                text="The clinic is closed on Sundays.",
                fg=RED
            )
            return

        try:
            available = get_available_slots(
                selected_doctor_id,
                selected_date
            )

            slot_combo["values"] = available

            if available:
                availability_label.config(
                    text=f"{len(available)} available slots. Select one to continue.",
                    fg=GREEN
                )
            else:
                availability_label.config(
                    text="No available slots for this doctor on this date.",
                    fg=RED
                )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

    # ---------------- SILENT AVAILABILITY REFRESH ----------------
    def check_availability_silently():
        selected_doctor_id = doctor_map.get(
            doctor_var.get()
        )

        if not selected_doctor_id:
            return

        try:
            selected_date = datetime.strptime(
                date_var.get().strip(),
                "%Y-%m-%d"
            ).date()

            if (
                selected_date < datetime.now().date()
                or selected_date.weekday() == 6
            ):
                return

            available = get_available_slots(
                selected_doctor_id,
                selected_date
            )

            slot_combo["values"] = available

            if slot_var.get() not in available:
                slot_var.set("")

            availability_label.config(
                text=(
                    f"{len(available)} available slots."
                    if available
                    else "No available slots for this doctor on this date."
                ),
                fg=GREEN if available else RED
            )

        except (ValueError, sqlite3.Error) as error:
            if isinstance(error, sqlite3.Error):
                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

    # ---------------- BOOK APPOINTMENT ----------------
    def book_appointment():
        selected_doctor_id = doctor_map.get(
            doctor_var.get()
        )

        selected_slot = slot_var.get()

        if not selected_doctor_id or not selected_slot:
            messagebox.showwarning(
                "Missing Information",
                "Select a doctor, date and available time slot."
            )
            return

        try:
            selected_date = datetime.strptime(
                date_var.get().strip(),
                "%Y-%m-%d"
            ).date()

        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Enter the date in YYYY-MM-DD format."
            )
            return

        appointment_datetime, error_message = valid_appointment_datetime(
            selected_date.isoformat(),
            selected_slot
        )

        if error_message:
            messagebox.showwarning(
                "Invalid Appointment",
                error_message
            )
            return

        # Verify the chosen slot belongs to the current availability list.
        if selected_slot not in slot_combo["values"]:
            messagebox.showwarning(
                "Check Availability",
                "This slot is no longer available. Check availability again."
            )
            check_availability()
            return

        formatted_datetime = appointment_datetime.strftime(
            "%Y-%m-%d %H:%M"
        )

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("BEGIN IMMEDIATE")

            # Confirm that the patient still exists.
            cursor.execute("""
                SELECT patient_id
                FROM Patient
                WHERE patient_id = ?
            """, (patient_id,))

            if not cursor.fetchone():
                raise sqlite3.Error(
                    "Your patient record could not be found."
                )

            # Confirm that the selected doctor still exists.
            cursor.execute("""
                SELECT doctor_id
                FROM Doctor
                WHERE doctor_id = ?
            """, (selected_doctor_id,))

            if not cursor.fetchone():
                raise sqlite3.Error(
                    "The selected doctor is no longer available."
                )

            cursor.execute("""
                SELECT COUNT(*)
                FROM Appointment
                WHERE doctor_id = ?
                  AND datetime(appointment_datetime) = datetime(?)
                  AND status = 'Scheduled'
            """, (
                selected_doctor_id,
                formatted_datetime
            ))

            if cursor.fetchone()[0] > 0:
                conn.rollback()

                messagebox.showwarning(
                    "Slot Unavailable",
                    "This slot has already been booked. Please select another time."
                )

                check_availability()
                return

            cursor.execute("""
                INSERT INTO Appointment (
                    patient_id,
                    doctor_id,
                    appointment_datetime,
                    status,
                    notes
                )
                VALUES (?, ?, ?, 'Scheduled', ?)
            """, (
                patient_id,
                selected_doctor_id,
                formatted_datetime,
                "Booked by patient"
            ))

            conn.commit()

            messagebox.showinfo(
                "Appointment Booked",
                "Your appointment has been booked successfully."
            )

            check_availability()
            load_my_appointments()

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

    # ---------------- BOOKING BUTTONS ----------------
    booking_buttons = tk.Frame(form, bg=WHITE)
    booking_buttons.pack(anchor="w", pady=(8, 0))

    make_button(
        booking_buttons,
        "Check Availability",
        check_availability,
        "#EAF0F8",
        NAVY
    ).pack(side="left", padx=(0, 8))

    make_button(
        booking_buttons,
        "Book Appointment",
        book_appointment,
        BLUE
    ).pack(side="left")

    # =========================================================
    # PATIENT APPOINTMENT HISTORY
    # =========================================================
    appointments_frame = tk.Frame(
        main,
        bg=WHITE,
        padx=15,
        pady=13,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    appointments_frame.pack(
        fill="both",
        expand=True,
        pady=(0, 10)
    )

    tk.Label(
        appointments_frame,
        text="My Appointments",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", pady=(0, 9))

    my_columns = (
        "ID",
        "Doctor",
        "Date & Time",
        "Status",
        "Notes"
    )

    my_tree = make_table(
        appointments_frame,
        my_columns,
        {
            "ID": 55,
            "Doctor": 190,
            "Date & Time": 160,
            "Status": 110,
            "Notes": 220
        }
    )

    # ---------------- LOAD PATIENT APPOINTMENTS ----------------
    def load_my_appointments():
        for item in my_tree.get_children():
            my_tree.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    A.appointment_id,
                    S.full_name,
                    A.appointment_datetime,
                    A.status,
                    COALESCE(A.notes, '')
                FROM Appointment A
                JOIN Doctor D ON A.doctor_id = D.doctor_id
                JOIN Staff S ON D.staff_id = S.staff_id
                WHERE A.patient_id = ?
                ORDER BY A.appointment_datetime DESC
            """, (patient_id,))

            for record in cursor.fetchall():
                my_tree.insert(
                    "",
                    "end",
                    values=record
                )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:
            if conn:
                conn.close()

    # ---------------- CANCEL PATIENT APPOINTMENT ----------------
    def cancel_my_appointment():
        selected = my_tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select one of your appointments first."
            )
            return

        values = my_tree.item(
            selected[0],
            "values"
        )

        appointment_id = values[0]

        if values[3] != "Scheduled":
            messagebox.showwarning(
                "Cannot Cancel",
                "Only scheduled appointments can be cancelled."
            )
            return

        if not messagebox.askyesno(
            "Confirm Cancellation",
            f"Cancel your appointment with {values[1]} on {values[2]}?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Appointment
                SET status = 'Cancelled'
                WHERE appointment_id = ?
                  AND patient_id = ?
                  AND status = 'Scheduled'
            """, (
                appointment_id,
                patient_id
            ))

            if cursor.rowcount != 1:
                conn.rollback()

                messagebox.showwarning(
                    "Cancellation Failed",
                    "This appointment could not be cancelled. Refresh the list and try again."
                )

                load_my_appointments()
                return

            conn.commit()

            messagebox.showinfo(
                "Appointment Cancelled",
                "Your appointment has been cancelled successfully. "
                "The time slot is now available again."
            )

            load_my_appointments()
            check_availability_silently()

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

    # ---------------- PATIENT ACTION BUTTONS ----------------
    action_row = tk.Frame(appointments_frame, bg=WHITE)
    action_row.pack(fill="x", pady=(9, 0))

    make_button(
        action_row,
        "Cancel My Appointment",
        cancel_my_appointment,
        "#FCE8E8",
        "#A93232"
    ).pack(side="left", padx=(0, 8))

    make_button(
        action_row,
        "Refresh Appointments",
        load_my_appointments,
        "#EAF0F8",
        NAVY
    ).pack(side="left")

    # ---------------- INITIAL LOAD ----------------
    if not doctor_rows:
        availability_label.config(
            text="No doctors are currently registered.",
            fg=RED
        )

    load_my_appointments()
