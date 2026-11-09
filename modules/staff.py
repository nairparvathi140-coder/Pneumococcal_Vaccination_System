
import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

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

STAFF_ROLES = [
    "Doctor",
    "Nurse",
    "Vaccination Staff"
]


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
        "Staff.TEntry",
        fieldbackground=WHITE,
        foreground=TEXT,
        padding=8,
        bordercolor=BORDER
    )

    style.configure(
        "Staff.TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=TEXT,
        padding=8,
        bordercolor=BORDER
    )

    style.map(
        "Staff.TCombobox",
        fieldbackground=[("readonly", WHITE)],
        selectbackground=[("readonly", WHITE)],
        selectforeground=[("readonly", TEXT)]
    )

    style.configure(
        "Staff.Treeview",
        background=WHITE,
        foreground=TEXT,
        fieldbackground=WHITE,
        rowheight=30,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Staff.Treeview.Heading",
        background=LIGHT,
        foreground=NAVY,
        font=("Segoe UI", 9, "bold"),
        padding=8
    )

    style.map(
        "Staff.Treeview",
        background=[("selected", "#D9E9FC")],
        foreground=[("selected", NAVY)]
    )


def show_staff(parent, page_title, clear_content):
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
        text="Doctors & Staff Management",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 21, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Register, search and manage hospital doctors and staff members",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 0))

    # ========================================================
    # STAFF INFORMATION FORM
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
        text="Staff Information",
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
        ("Phone Number", "phone"),
        ("Email Address", "email"),
        ("Username", "username"),
        ("Specialization (Doctors only)", "specialization")
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

        entry = ttk.Entry(
            form,
            style="Staff.TEntry",
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

    # Staff role
    tk.Label(
        form,
        text="Staff Role",
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

    role = ttk.Combobox(
        form,
        values=STAFF_ROLES,
        state="readonly",
        style="Staff.TCombobox",
        font=("Segoe UI", 9)
    )
    role.grid(
        row=4,
        column=1,
        sticky="ew",
        padx=(0, 18),
        pady=6
    )
    role.set("Nurse")

    for col in range(4):
        form.columnconfigure(col, weight=1)

    # ========================================================
    # DOCTOR SPECIALIZATION CONTROL
    # ========================================================

    def update_specialization(event=None):
        if role.get() == "Doctor":
            fields["specialization"].configure(state="normal")
        else:
            fields["specialization"].delete(0, tk.END)
            fields["specialization"].configure(state="disabled")

    role.bind(
        "<<ComboboxSelected>>",
        update_specialization
    )
    update_specialization()

    tk.Label(
        form,
        text="Note: Administrator login accounts are managed separately.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 8)
    ).grid(
        row=5,
        column=0,
        columnspan=4,
        sticky="w",
        pady=(8, 0)
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search_frame = tk.Frame(parent, bg=BG)
    search_frame.pack(fill="x", pady=(0, 10))

    tk.Label(
        search_frame,
        text="Search Staff",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=(0, 10))

    search_entry = ttk.Entry(
        search_frame,
        width=32,
        style="Staff.TEntry"
    )
    search_entry.pack(side="left", padx=(0, 8))

    # ========================================================
    # STAFF TABLE
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
        text="Registered Doctors & Staff",
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
        "Role",
        "Specialization",
        "Phone",
        "Email",
        "Username"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=7,
        style="Staff.Treeview"
    )

    widths = {
        "ID": 55,
        "Name": 165,
        "Role": 125,
        "Specialization": 155,
        "Phone": 125,
        "Email": 190,
        "Username": 120
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
    # LOAD STAFF
    # ========================================================

    def load_staff(keyword=""):
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
                    S.staff_id,
                    S.full_name,
                    S.role,
                    COALESCE(D.specialization, ''),
                    S.phone,
                    S.email,
                    S.username
                FROM Staff S
                LEFT JOIN Doctor D
                    ON S.staff_id = D.staff_id
                WHERE CAST(S.staff_id AS TEXT) LIKE ?
                   OR S.full_name LIKE ?
                   OR S.role LIKE ?
                   OR S.phone LIKE ?
                   OR S.email LIKE ?
                   OR S.username LIKE ?
                   OR D.specialization LIKE ?
                ORDER BY S.staff_id DESC
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
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
                f"Could not load staff records:\n{error}",
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
            entry.configure(state="normal")
            entry.delete(0, tk.END)

        role.set("Nurse")
        update_specialization()

        table.selection_remove(table.selection())

    # ========================================================
    # VALIDATE FORM
    # ========================================================

    def get_form_values():
        values = {
            key: entry.get().strip()
            for key, entry in fields.items()
        }

        values["role"] = role.get().strip()

        if not values["full_name"] or not values["role"]:
            messagebox.showwarning(
                "Missing Information",
                "Full name and staff role are required.",
                parent=parent
            )
            return None

        if values["role"] not in STAFF_ROLES:
            messagebox.showerror(
                "Invalid Role",
                "Select a valid staff role.",
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

        if (
            values["role"] == "Doctor"
            and not values["specialization"]
        ):
            messagebox.showwarning(
                "Missing Specialization",
                "Enter the doctor's specialization.",
                parent=parent
            )
            return None

        return values

    # ========================================================
    # CHECK USERNAME
    # ========================================================

    def username_in_use(cursor, username, current_staff_id=None):
        if not username:
            return False

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
            return True

        query = """
            SELECT staff_id
            FROM Staff
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
        """
        params = [username]

        if current_staff_id is not None:
            query += " AND staff_id != ?"
            params.append(current_staff_id)

        query += " LIMIT 1"

        cursor.execute(query, tuple(params))
        return cursor.fetchone() is not None

    # ========================================================
    # ADD STAFF
    # ========================================================

    def add_staff():
        values = get_form_values()

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if username_in_use(cursor, values["username"]):
                messagebox.showerror(
                    "Username Exists",
                    "This username is already associated with another account or staff record.",
                    parent=parent
                )
                return

            cursor.execute(
                """
                INSERT INTO Staff (
                    full_name,
                    role,
                    phone,
                    email,
                    username
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    values["full_name"],
                    values["role"],
                    values["phone"],
                    values["email"],
                    values["username"] or None
                )
            )

            staff_id = cursor.lastrowid

            if values["role"] == "Doctor":
                cursor.execute(
                    """
                    INSERT INTO Doctor (
                        staff_id,
                        specialization
                    )
                    VALUES (?, ?)
                    """,
                    (
                        staff_id,
                        values["specialization"]
                    )
                )

            conn.commit()

            messagebox.showinfo(
                "Staff Registered",
                f"Staff member registered successfully.\nStaff ID: {staff_id}",
                parent=parent
            )

            clear_form()
            load_staff(search_entry.get())

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Registration Error",
                f"Could not register this staff member:\n{error}",
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
    # SELECT STAFF
    # ========================================================

    def select_staff(event=None):
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
                    S.full_name,
                    S.phone,
                    S.email,
                    S.username,
                    S.role,
                    COALESCE(D.specialization, '')
                FROM Staff S
                LEFT JOIN Doctor D
                    ON S.staff_id = D.staff_id
                WHERE S.staff_id = ?
                """,
                (selected_id,)
            )

            data = cursor.fetchone()

            if data:
                mapping = {
                    "full_name": data[0],
                    "phone": data[1],
                    "email": data[2],
                    "username": data[3],
                    "specialization": data[5]
                }

                for key, value in mapping.items():
                    fields[key].configure(state="normal")
                    fields[key].delete(0, tk.END)
                    fields[key].insert(0, value or "")

                role.set(data[4])
                update_specialization()

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not retrieve staff information:\n{error}",
                parent=parent
            )

        finally:
            if conn:
                conn.close()

    table.bind(
        "<<TreeviewSelect>>",
        select_staff
    )

    # ========================================================
    # UPDATE STAFF
    # ========================================================

    def update_staff():
        if selected_id is None:
            messagebox.showwarning(
                "Select Staff",
                "Select a staff member from the table before updating.",
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

            if username_in_use(
                cursor,
                values["username"],
                selected_id
            ):
                messagebox.showerror(
                    "Username Exists",
                    "This username is already used by another account or staff record.",
                    parent=parent
                )
                return

            # Check whether this staff member has a linked login account.
            cursor.execute(
                """
                SELECT account_id, username
                FROM User_Account
                WHERE staff_id = ?
                """,
                (selected_id,)
            )

            linked_account = cursor.fetchone()

            if linked_account and not values["username"]:
                messagebox.showerror(
                    "Username Required",
                    "This staff member has a linked login account. "
                    "A username is required to keep the staff record "
                    "and login account synchronized.",
                    parent=parent
                )
                return

            cursor.execute(
                """
                UPDATE Staff
                SET
                    full_name = ?,
                    role = ?,
                    phone = ?,
                    email = ?,
                    username = ?
                WHERE staff_id = ?
                """,
                (
                    values["full_name"],
                    values["role"],
                    values["phone"],
                    values["email"],
                    values["username"] or None,
                    selected_id
                )
            )

            # Keep the linked login account username synchronized.
            if linked_account:
                cursor.execute(
                    """
                    UPDATE User_Account
                    SET username = ?
                    WHERE staff_id = ?
                    """,
                    (
                        values["username"],
                        selected_id
                    )
                )

            # Create or update the Doctor record.
            if values["role"] == "Doctor":
                cursor.execute(
                    """
                    INSERT INTO Doctor (
                        staff_id,
                        specialization
                    )
                    VALUES (?, ?)
                    ON CONFLICT(staff_id)
                    DO UPDATE SET
                        specialization = excluded.specialization
                    """,
                    (
                        selected_id,
                        values["specialization"]
                    )
                )
            else:
                # This may fail if the doctor has linked appointments
                # or eligibility assessments. The transaction protects
                # the existing records if that happens.
                cursor.execute(
                    """
                    DELETE FROM Doctor
                    WHERE staff_id = ?
                    """,
                    (selected_id,)
                )

            conn.commit()

            messagebox.showinfo(
                "Staff Updated",
                "Staff information updated successfully.",
                parent=parent
            )

            clear_form()
            load_staff(search_entry.get())

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Cannot Update Staff",
                "The change conflicts with an existing account or linked "
                "medical record.\n\n"
                "A doctor with linked appointments or eligibility "
                "assessments cannot be changed to another role.\n\n"
                f"Database details: {error}",
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
    # DELETE STAFF
    # ========================================================

    def delete_staff():
        if selected_id is None:
            messagebox.showwarning(
                "Select Staff",
                "Select a staff member from the table before deleting.",
                parent=parent
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this staff member?\n\n"
            "Staff members with linked login accounts, appointments, "
            "or medical records may not be deletable.",
            parent=parent
        )

        if not confirm:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Remove the Doctor record first if one exists.
            cursor.execute(
                """
                DELETE FROM Doctor
                WHERE staff_id = ?
                """,
                (selected_id,)
            )

            cursor.execute(
                """
                DELETE FROM Staff
                WHERE staff_id = ?
                """,
                (selected_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Staff Deleted",
                "Staff record deleted successfully.",
                parent=parent
            )

            clear_form()
            load_staff(search_entry.get())

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Cannot Delete Staff",
                "This staff member has linked records, such as a login "
                "account, vaccination records, appointments, or eligibility "
                "assessments.\n\n"
                "Preserve the staff record and manage the linked account "
                "through the appropriate administrator controls.",
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
        "Add Staff",
        add_staff,
        BLUE,
        BLUE_DARK
    ).pack(side="left", padx=(0, 7))

    create_button(
        "Update",
        update_staff,
        GREEN
    ).pack(side="left", padx=7)

    create_button(
        "Delete",
        delete_staff,
        RED
    ).pack(side="left", padx=7)

    create_button(
        "Clear Form",
        clear_form,
        NAVY
    ).pack(side="left", padx=7)

    create_button(
        "Search",
        lambda: load_staff(search_entry.get()),
        BLUE
    ).pack(side="left", padx=7)

    def refresh_staff():
        search_entry.delete(0, tk.END)
        clear_form()
        load_staff()

    create_button(
        "Refresh",
        refresh_staff,
        MUTED
    ).pack(side="left", padx=7)

    search_entry.bind(
        "<Return>",
        lambda event: load_staff(search_entry.get())
    )

    # INITIAL LOAD
    load_staff()
