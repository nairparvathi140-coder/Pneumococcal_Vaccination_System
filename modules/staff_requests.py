
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

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
MUTED = "#718096"
BORDER = "#E3EAF3"

# ---------------- STAFF REQUEST MANAGEMENT ----------------
def show_staff_requests(parent, page_title, clear_content, account):
    """
    Admin-only page for approving or rejecting staff registrations.
    """

    # ---------------- ACCESS CONTROL ----------------
    if not account or account.get("role") != "admin":
        messagebox.showerror(
            "Access Denied",
            "Only administrators can manage staff requests."
        )
        return

    clear_content()
    page_title.config(text="Staff Registration Requests")

    # ---------------- MAIN FRAME ----------------
    main_frame = tk.Frame(parent, bg=BG, padx=12, pady=10)
    main_frame.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    header_frame = tk.Frame(main_frame, bg=BG)
    header_frame.pack(fill="x", pady=(0, 12))

    tk.Label(
        header_frame,
        text="Staff Registration Requests",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w")

    tk.Label(
        header_frame,
        text="Review staff registrations and manage account access.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 0))

    # ---------------- SUMMARY CARD ----------------
    summary_frame = tk.Frame(
        main_frame,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
        padx=15,
        pady=10
    )
    summary_frame.pack(fill="x", pady=(0, 12))

    summary_left = tk.Frame(summary_frame, bg=WHITE)
    summary_left.pack(side="left", fill="x", expand=True)

    tk.Label(
        summary_left,
        text="PENDING APPROVALS",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9, "bold")
    ).pack(anchor="w")

    count_label = tk.Label(
        summary_left,
        text="0",
        bg=WHITE,
        fg=BLUE,
        font=("Segoe UI", 24, "bold")
    )
    count_label.pack(anchor="w")

    tk.Label(
        summary_frame,
        text="Staff accounts remain inactive until approved.",
        bg=WHITE,
        fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(side="right", padx=10)

    # ---------------- SEARCH ----------------
    search_frame = tk.Frame(main_frame, bg=BG)
    search_frame.pack(fill="x", pady=(0, 8))

    tk.Label(
        search_frame,
        text="Search Requests",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 9, "bold")
    ).pack(side="left", padx=(0, 8))

    search_entry = ttk.Entry(search_frame, width=32)
    search_entry.pack(side="left")

    # ---------------- TABLE ----------------
    columns = (
        "account_id",
        "staff_id",
        "full_name",
        "role",
        "specialization",
        "phone",
        "email",
        "username"
    )

    headings = {
        "account_id": "Account ID",
        "staff_id": "Staff ID",
        "full_name": "Full Name",
        "role": "Staff Role",
        "specialization": "Specialization",
        "phone": "Phone",
        "email": "Email",
        "username": "Username"
    }

    widths = {
        "account_id": 85,
        "staff_id": 75,
        "full_name": 170,
        "role": 135,
        "specialization": 160,
        "phone": 120,
        "email": 190,
        "username": 125
    }

    table_card = tk.Frame(
        main_frame,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    table_card.pack(fill="both", expand=True)

    table_frame = tk.Frame(table_card, bg=WHITE)
    table_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for column in columns:
        tree.heading(column, text=headings[column])
        tree.column(
            column,
            width=widths[column],
            minwidth=65,
            anchor="center",
            stretch=False
        )

    vertical_scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    tree.grid(row=0, column=0, sticky="nsew")
    vertical_scroll.grid(row=0, column=1, sticky="ns")
    horizontal_scroll.grid(row=1, column=0, sticky="ew")

    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    # ---------------- BUTTON HELPER ----------------
    def make_button(parent_frame, text, command, color):
        return tk.Button(
            parent_frame,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=color,
            activeforeground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=9
        )

    # ---------------- LOAD REQUESTS ----------------
    def load_requests(keyword=""):
        for item in tree.get_children():
            tree.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    UA.account_id,
                    S.staff_id,
                    S.full_name,
                    S.role,
                    COALESCE(D.specialization, 'N/A'),
                    S.phone,
                    S.email,
                    UA.username
                FROM User_Account UA
                JOIN Staff S
                    ON UA.staff_id = S.staff_id
                LEFT JOIN Doctor D
                    ON S.staff_id = D.staff_id
                WHERE UA.role = 'staff'
                  AND UA.account_status = 'pending'
                ORDER BY UA.created_at ASC, UA.account_id ASC
            """)

            rows = cursor.fetchall()

            keyword = keyword.strip().lower()

            filtered_rows = []

            for row in rows:
                searchable_values = [
                    str(value).lower()
                    for value in row
                    if value is not None
                ]

                if not keyword or any(
                    keyword in value
                    for value in searchable_values
                ):
                    filtered_rows.append(row)

            for row in filtered_rows:
                tree.insert(
                    "",
                    "end",
                    values=row
                )

            count_label.config(text=str(len(rows)))

            if keyword:
                result_text = (
                    f"Showing {len(filtered_rows)} of {len(rows)} "
                    "pending requests"
                )
            else:
                result_text = f"{len(rows)} pending requests"

            status_label.config(text=result_text)

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to load staff requests.\n\n{error}"
            )

        finally:
            if conn:
                conn.close()

    # ---------------- APPROVE / REJECT REQUEST ----------------
    def update_request(new_status):
        if new_status not in ("active", "disabled"):
            messagebox.showerror(
                "Invalid Action",
                "The requested account status is invalid."
            )
            return

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select a staff request from the table first."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        account_id = values[0]
        staff_name = values[2]

        if new_status == "active":
            action = "approve"
            title = "Approve Staff Request"
            success_title = "Request Approved"
            success_message = (
                f"{staff_name}'s staff account has been approved "
                "and activated."
            )
        else:
            action = "reject"
            title = "Reject Staff Request"
            success_title = "Request Rejected"
            success_message = (
                f"{staff_name}'s registration has been rejected."
            )

        if not messagebox.askyesno(
            title,
            f"Are you sure you want to {action} "
            f"the registration request for {staff_name}?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("BEGIN IMMEDIATE")

            cursor.execute("""
                UPDATE User_Account
                SET account_status = ?
                WHERE account_id = ?
                  AND role = 'staff'
                  AND account_status = 'pending'
            """, (
                new_status,
                account_id
            ))

            if cursor.rowcount == 0:
                conn.rollback()

                messagebox.showwarning(
                    "Request Already Processed",
                    "This request is no longer pending. "
                    "The table will now be refreshed."
                )

                load_requests(search_entry.get())
                return

            conn.commit()

            messagebox.showinfo(
                success_title,
                success_message
            )

            load_requests(search_entry.get())

        except sqlite3.Error as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                f"Unable to update the staff request.\n\n{error}"
            )

        finally:
            if conn:
                conn.close()

    # ---------------- ACTION BUTTONS ----------------
    button_frame = tk.Frame(main_frame, bg=BG)
    button_frame.pack(fill="x", pady=(12, 5))

    make_button(
        button_frame,
        "Approve Request",
        lambda: update_request("active"),
        GREEN
    ).pack(side="left", padx=(0, 7))

    make_button(
        button_frame,
        "Reject Request",
        lambda: update_request("disabled"),
        RED
    ).pack(side="left", padx=7)

    make_button(
        button_frame,
        "Search",
        lambda: load_requests(search_entry.get()),
        BLUE
    ).pack(side="left", padx=7)

    make_button(
        button_frame,
        "Refresh",
        lambda: (
            search_entry.delete(0, tk.END),
            load_requests()
        ),
        NAVY
    ).pack(side="left", padx=7)

    # ---------------- STATUS LABEL ----------------
    status_label = tk.Label(
        main_frame,
        text="Loading requests...",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9)
    )
    status_label.pack(anchor="w", pady=(4, 0))

    search_entry.bind(
        "<Return>",
        lambda event: load_requests(search_entry.get())
    )

    # ---------------- INITIAL LOAD ----------------
    load_requests()
