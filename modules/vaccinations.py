
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

BG = "#F3F6FB"
WHITE = "#FFFFFF"
NAVY = "#172B4D"
BLUE = "#2878D0"
GREEN = "#159D79"
RED = "#D9534F"
MUTED = "#718096"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def show_vaccinations(parent, page_title, clear_content, account):
    clear_content()
    page_title.config(text="Vaccination Records")

    role = (account.get("role") or "").lower()
    logged_staff_id = account.get("staff_id")

    if role not in ("admin", "staff"):
        messagebox.showerror("Access Denied", "Only administrators and authorised staff can manage vaccination records.")
        return

    if role == "staff" and not logged_staff_id:
        messagebox.showerror("Account Error", "This staff account is not linked to a Staff record.")
        return

    patient_map = {}
    vaccine_map = {}
    batch_map = {}
    staff_map = {}

    # ---------------- PAGE HEADER ----------------
    tk.Label(
        parent,
        text="Vaccination Records Management",
        bg=BG, fg=NAVY,
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w")

    tk.Label(
        parent,
        text="Record administered vaccines, monitor stock and maintain patient vaccination history.",
        bg=BG, fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 10))

    notebook = ttk.Notebook(parent)
    notebook.pack(fill="both", expand=True, pady=5)

    record_tab = tk.Frame(notebook, bg=BG)
    history_tab = tk.Frame(notebook, bg=BG)
    stock_tab = tk.Frame(notebook, bg=BG)

    notebook.add(record_tab, text="Record Vaccination")
    notebook.add(history_tab, text="Vaccination History")
    notebook.add(stock_tab, text="Available Stock")

    # ---------------- RECORD FORM ----------------
    form = tk.LabelFrame(
        record_tab,
        text="Vaccination Details",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 11, "bold"),
        padx=10, pady=8
    )
    form.pack(fill="x", padx=5, pady=6)

    fields = {}

    labels = [
        ("Patient", "patient"),
        ("Vaccine", "vaccine"),
        ("Batch", "batch"),
        ("Dose Number", "dose"),
        ("Administration Date (YYYY-MM-DD)", "admin_date"),
        ("Next Due Date (YYYY-MM-DD)", "next_due"),
        ("Administered By", "staff")
    ]

    for i, (label, key) in enumerate(labels):
        row = i // 2
        col = (i % 2) * 2

        tk.Label(
            form, text=label,
            bg=WHITE, fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).grid(row=row, column=col, sticky="w", padx=8, pady=6)

        if key in ("patient", "vaccine", "batch", "staff"):
            widget = ttk.Combobox(form, state="readonly", width=30)
        else:
            widget = ttk.Entry(form, width=32)

        widget.grid(row=row, column=col + 1, sticky="ew", padx=8, pady=6)
        fields[key] = widget

    for col in range(4):
        form.columnconfigure(col, weight=1)

    tk.Label(
        form, text="Adverse Reaction Notes",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 9, "bold")
    ).grid(row=4, column=0, sticky="nw", padx=8, pady=6)

    reaction_entry = tk.Text(
        form, height=2,
        font=("Segoe UI", 9),
        wrap="word"
    )
    reaction_entry.grid(
        row=4, column=1,
        columnspan=3, sticky="ew",
        padx=8, pady=6
    )

    # ---------------- SEARCH AND BUTTONS ----------------
    search_frame = tk.Frame(record_tab, bg=BG)
    search_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(
        search_frame,
        text="Search patient:",
        bg=BG, fg=NAVY,
        font=("Segoe UI", 9, "bold")
    ).pack(side="left", padx=(0, 8))

    search_entry = ttk.Entry(search_frame, width=28)
    search_entry.pack(side="left")

    button_frame = tk.Frame(record_tab, bg=BG)
    button_frame.pack(fill="x", padx=5, pady=5)

    def make_button(text, command, color):
        return tk.Button(
            button_frame,
            text=text,
            command=command,
            bg=color, fg=WHITE,
            activebackground=color,
            activeforeground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12, pady=7
        )

    # ---------------- RECORD TABLE ----------------
    record_frame = tk.Frame(record_tab, bg=WHITE)
    record_frame.pack(fill="both", expand=True, padx=5, pady=5)

    record_columns = (
        "ID", "Patient", "Vaccine", "Batch",
        "Dose", "Date", "Next Due", "Staff"
    )

    record_table = ttk.Treeview(
        record_frame,
        columns=record_columns,
        show="headings",
        height=8
    )

    record_widths = [55, 160, 150, 110, 60, 110, 110, 150]

    for col, width in zip(record_columns, record_widths):
        record_table.heading(col, text=col)
        record_table.column(col, width=width, minwidth=55, anchor="center")

    record_y_scroll = ttk.Scrollbar(
        record_frame, orient="vertical",
        command=record_table.yview
    )
    record_x_scroll = ttk.Scrollbar(
        record_frame, orient="horizontal",
        command=record_table.xview
    )

    record_table.configure(
        yscrollcommand=record_y_scroll.set,
        xscrollcommand=record_x_scroll.set
    )

    record_table.grid(row=0, column=0, sticky="nsew")
    record_y_scroll.grid(row=0, column=1, sticky="ns")
    record_x_scroll.grid(row=1, column=0, sticky="ew")

    record_frame.rowconfigure(0, weight=1)
    record_frame.columnconfigure(0, weight=1)

    # ---------------- HISTORY TABLE ----------------
    history_frame = tk.Frame(history_tab, bg=WHITE)
    history_frame.pack(fill="both", expand=True, padx=5, pady=8)

    history_columns = (
        "Patient", "Vaccine", "Dose", "Date",
        "Next Due", "Adverse Reaction", "Administered By"
    )

    history_table = ttk.Treeview(
        history_frame,
        columns=history_columns,
        show="headings",
        height=15
    )

    history_widths = [160, 150, 60, 110, 110, 260, 160]

    for col, width in zip(history_columns, history_widths):
        history_table.heading(col, text=col)
        history_table.column(col, width=width, minwidth=60, anchor="center")

    history_y_scroll = ttk.Scrollbar(
        history_frame, orient="vertical",
        command=history_table.yview
    )
    history_x_scroll = ttk.Scrollbar(
        history_frame, orient="horizontal",
        command=history_table.xview
    )

    history_table.configure(
        yscrollcommand=history_y_scroll.set,
        xscrollcommand=history_x_scroll.set
    )

    history_table.grid(row=0, column=0, sticky="nsew")
    history_y_scroll.grid(row=0, column=1, sticky="ns")
    history_x_scroll.grid(row=1, column=0, sticky="ew")

    history_frame.rowconfigure(0, weight=1)
    history_frame.columnconfigure(0, weight=1)

    # ---------------- STOCK TABLE ----------------
    stock_frame = tk.Frame(stock_tab, bg=WHITE)
    stock_frame.pack(fill="both", expand=True, padx=5, pady=8)

    stock_columns = (
        "Vaccine", "Batch Number", "Manufacturing Date",
        "Expiry Date", "Doses Received", "Doses Available"
    )

    stock_table = ttk.Treeview(
        stock_frame,
        columns=stock_columns,
        show="headings",
        height=15
    )

    stock_widths = [180, 140, 150, 140, 130, 140]

    for col, width in zip(stock_columns, stock_widths):
        stock_table.heading(col, text=col)
        stock_table.column(col, width=width, minwidth=80, anchor="center")

    stock_y_scroll = ttk.Scrollbar(
        stock_frame, orient="vertical",
        command=stock_table.yview
    )
    stock_x_scroll = ttk.Scrollbar(
        stock_frame, orient="horizontal",
        command=stock_table.xview
    )

    stock_table.configure(
        yscrollcommand=stock_y_scroll.set,
        xscrollcommand=stock_x_scroll.set
    )

    stock_table.grid(row=0, column=0, sticky="nsew")
    stock_y_scroll.grid(row=0, column=1, sticky="ns")
    stock_x_scroll.grid(row=1, column=0, sticky="ew")

    stock_frame.rowconfigure(0, weight=1)
    stock_frame.columnconfigure(0, weight=1)

    # ---------------- LOAD FORM OPTIONS ----------------
    def load_options():
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT patient_id, full_name FROM Patient ORDER BY full_name"
            )
            patients = cur.fetchall()

            cur.execute(
                "SELECT vaccine_id, vaccine_name FROM Vaccine ORDER BY vaccine_name"
            )
            vaccines = cur.fetchall()

            cur.execute(
                "SELECT staff_id, full_name, role FROM Staff ORDER BY full_name"
            )
            staff = cur.fetchall()

            patient_map.clear()
            patient_map.update({
                f"{name} (ID: {pid})": pid
                for pid, name in patients
            })

            vaccine_map.clear()
            vaccine_map.update({
                name: vid
                for vid, name in vaccines
            })

            staff_map.clear()
            staff_map.update({
                f"{name} ({staff_role})": sid
                for sid, name, staff_role in staff
            })

            fields["patient"]["values"] = list(patient_map.keys())
            fields["vaccine"]["values"] = list(vaccine_map.keys())

            if role == "admin":
                fields["staff"]["values"] = list(staff_map.keys())
                fields["staff"].configure(state="readonly")
            else:
                fields["staff"].configure(state="disabled")
                staff_name = next(
                    (
                        name for name, sid in staff_map.items()
                        if sid == logged_staff_id
                    ),
                    ""
                )
                fields["staff"].set(staff_name)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load form options:\n{e}")
        finally:
            if conn:
                conn.close()

    # ---------------- LOAD AVAILABLE BATCHES ----------------
    def refresh_batches(event=None):
        vaccine_id = vaccine_map.get(fields["vaccine"].get())

        fields["batch"].set("")
        batch_map.clear()

        if vaccine_id is None:
            fields["batch"]["values"] = []
            return

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT batch_id, batch_number, expiry_date, quantity_available
                FROM Vaccine_Batch
                WHERE vaccine_id = ?
                  AND quantity_available > 0
                ORDER BY expiry_date ASC
            """, (vaccine_id,))

            rows = cur.fetchall()
            options = []

            for batch_id, number, expiry, quantity in rows:
                try:
                    expiry_day = datetime.strptime(
                        expiry, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    continue

                if expiry_day <= date.today():
                    continue

                label = f"{number} | {quantity} doses | Exp: {expiry}"
                batch_map[label] = batch_id
                options.append(label)

            fields["batch"]["values"] = options

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load vaccine batches:\n{e}")
        finally:
            if conn:
                conn.close()

    fields["vaccine"].bind(
        "<<ComboboxSelected>>",
        refresh_batches
    )

    # ---------------- LOAD VACCINATION RECORDS ----------------
    def load_records(keyword=""):
        for item in record_table.get_children():
            record_table.delete(item)

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT
                    V.vaccination_id,
                    P.full_name,
                    VC.vaccine_name,
                    B.batch_number,
                    V.dose_number,
                    V.date_administered,
                    V.next_due_date,
                    S.full_name
                FROM Vaccination V
                JOIN Patient P ON P.patient_id = V.patient_id
                JOIN Vaccine VC ON VC.vaccine_id = V.vaccine_id
                JOIN Vaccine_Batch B ON B.batch_id = V.batch_id
                JOIN Staff S ON S.staff_id = V.administered_by
                WHERE P.full_name LIKE ?
            """

            params = [f"%{keyword}%"]

            if role == "staff":
                query += " AND V.administered_by = ?"
                params.append(logged_staff_id)

            query += """
                ORDER BY V.date_administered DESC,
                         V.vaccination_id DESC
            """

            cur.execute(query, params)

            for row in cur.fetchall():
                record_table.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load vaccination records:\n{e}")
        finally:
            if conn:
                conn.close()

    # ---------------- LOAD VACCINATION HISTORY ----------------
    def load_history():
        for item in history_table.get_children():
            history_table.delete(item)

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT
                    P.full_name,
                    VC.vaccine_name,
                    V.dose_number,
                    V.date_administered,
                    V.next_due_date,
                    V.adverse_reaction_notes,
                    S.full_name
                FROM Vaccination V
                JOIN Patient P ON P.patient_id = V.patient_id
                JOIN Vaccine VC ON VC.vaccine_id = V.vaccine_id
                JOIN Staff S ON S.staff_id = V.administered_by
            """

            params = []

            if role == "staff":
                query += " WHERE V.administered_by = ?"
                params.append(logged_staff_id)

            query += """
                ORDER BY V.date_administered DESC,
                         V.vaccination_id DESC
            """

            cur.execute(query, params)

            for row in cur.fetchall():
                history_table.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load vaccination history:\n{e}")
        finally:
            if conn:
                conn.close()

    # ---------------- LOAD INVENTORY STOCK ----------------
    def load_stock():
        for item in stock_table.get_children():
            stock_table.delete(item)

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    V.vaccine_name,
                    B.batch_number,
                    B.manufacturing_date,
                    B.expiry_date,
                    B.quantity_received,
                    B.quantity_available
                FROM Vaccine_Batch B
                JOIN Vaccine V ON V.vaccine_id = B.vaccine_id
                ORDER BY B.expiry_date ASC
            """)

            for row in cur.fetchall():
                stock_table.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load vaccine stock:\n{e}")
        finally:
            if conn:
                conn.close()

    # ---------------- CLEAR FORM ----------------
    def clear_form():
        fields["patient"].set("")
        fields["vaccine"].set("")
        fields["batch"].set("")
        fields["dose"].delete(0, tk.END)
        fields["admin_date"].delete(0, tk.END)
        fields["next_due"].delete(0, tk.END)
        fields["batch"]["values"] = []
        batch_map.clear()
        reaction_entry.delete("1.0", tk.END)

        if role == "admin":
            fields["staff"].set("")
        else:
            staff_name = next(
                (
                    name for name, sid in staff_map.items()
                    if sid == logged_staff_id
                ),
                ""
            )
            fields["staff"].set(staff_name)

    # ---------------- DATE VALIDATION ----------------
    def parse_date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    # ---------------- SAVE VACCINATION ----------------
    def save_vaccination():
        patient_id = patient_map.get(fields["patient"].get())
        vaccine_id = vaccine_map.get(fields["vaccine"].get())
        batch_id = batch_map.get(fields["batch"].get())

        if role == "admin":
            staff_id = staff_map.get(fields["staff"].get())
        else:
            staff_id = logged_staff_id

        dose_text = fields["dose"].get().strip()
        admin_date_text = fields["admin_date"].get().strip()
        next_due_text = fields["next_due"].get().strip()
        reaction = reaction_entry.get("1.0", tk.END).strip()

        if not all([patient_id, vaccine_id, batch_id, staff_id]):
            messagebox.showwarning(
                "Missing Information",
                "Select a patient, vaccine, available batch and administering staff member."
            )
            return

        try:
            dose = int(dose_text)
            if dose <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid Dose",
                "Dose number must be a positive whole number."
            )
            return

        admin_day = parse_date(admin_date_text)
        next_due_day = parse_date(next_due_text) if next_due_text else None

        if not admin_day:
            messagebox.showerror(
                "Invalid Date",
                "Enter the administration date in YYYY-MM-DD format."
            )
            return

        if next_due_text and not next_due_day:
            messagebox.showerror(
                "Invalid Date",
                "Enter the next due date in YYYY-MM-DD format."
            )
            return

        if admin_day > date.today():
            messagebox.showerror(
                "Invalid Date",
                "Administration date cannot be in the future."
            )
            return

        if next_due_day and next_due_day <= admin_day:
            messagebox.showerror(
                "Invalid Due Date",
                "Next due date must be after the administration date."
            )
            return

        conn = None

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE")

            # Confirm the staff member exists.
            cur.execute(
                "SELECT staff_id FROM Staff WHERE staff_id = ?",
                (staff_id,)
            )

            if not cur.fetchone():
                raise ValueError("The selected staff member does not exist.")

            # Staff accounts can only record vaccinations under their own ID.
            if role == "staff" and staff_id != logged_staff_id:
                raise ValueError("You can only record vaccinations under your own staff account.")

            # Recheck the batch inside the transaction.
            cur.execute("""
                SELECT vaccine_id, expiry_date, quantity_available
                FROM Vaccine_Batch
                WHERE batch_id = ?
            """, (batch_id,))

            batch = cur.fetchone()

            if not batch:
                raise ValueError("The selected vaccine batch no longer exists.")

            if batch[0] != vaccine_id:
                raise ValueError("The selected batch does not belong to this vaccine.")

            expiry_day = parse_date(batch[1])

            if not expiry_day:
                raise ValueError("The selected batch has an invalid expiry date.")

            if expiry_day <= admin_day:
                raise ValueError("The selected batch is expired on the administration date.")

            if batch[2] <= 0:
                raise ValueError("This batch is out of stock.")

            # Prevent duplicate dose numbers for the same patient and vaccine.
            cur.execute("""
                SELECT vaccination_id
                FROM Vaccination
                WHERE patient_id = ?
                  AND vaccine_id = ?
                  AND dose_number = ?
            """, (patient_id, vaccine_id, dose))

            if cur.fetchone():
                raise ValueError(
                    "This patient already has this dose number recorded for this vaccine."
                )

            # Save vaccination.
            cur.execute("""
                INSERT INTO Vaccination (
                    patient_id,
                    vaccine_id,
                    batch_id,
                    appointment_id,
                    administered_by,
                    dose_number,
                    date_administered,
                    next_due_date,
                    adverse_reaction_notes
                )
                VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                vaccine_id,
                batch_id,
                staff_id,
                dose,
                admin_date_text,
                next_due_text or None,
                reaction or None
            ))

            # Deduct one dose from stock.
            cur.execute("""
                UPDATE Vaccine_Batch
                SET quantity_available = quantity_available - 1
                WHERE batch_id = ?
                  AND quantity_available > 0
            """, (batch_id,))

            if cur.rowcount != 1:
                raise ValueError(
                    "Stock could not be updated. Refresh the page and try again."
                )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Vaccination record saved successfully.\nOne dose has been deducted from stock."
            )

            clear_form()
            load_options()
            load_records(search_entry.get().strip())
            load_history()
            load_stock()
            refresh_batches()

        except ValueError as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Cannot Save Vaccination", str(e))

        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            messagebox.showerror(
                "Record Conflict",
                f"The vaccination could not be saved because of a database constraint:\n{e}"
            )

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            messagebox.showerror(
                "Database Error",
                f"Could not save the vaccination:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ---------------- BUTTON ACTIONS ----------------
    make_button(
        "Save Vaccination",
        save_vaccination,
        GREEN
    ).pack(side="left", padx=4)

    make_button(
        "Clear Form",
        clear_form,
        NAVY
    ).pack(side="left", padx=4)

    make_button(
        "Search",
        lambda: load_records(search_entry.get().strip()),
        BLUE
    ).pack(side="left", padx=4)

    make_button(
        "Refresh",
        lambda: (
            load_options(),
            load_records(search_entry.get().strip()),
            load_history(),
            load_stock(),
            refresh_batches()
        ),
        MUTED
    ).pack(side="left", padx=4)

    search_entry.bind(
        "<Return>",
        lambda event: load_records(search_entry.get().strip())
    )

    # ---------------- INITIAL LOAD ----------------
    load_options()
    load_records()
    load_history()
    load_stock()
