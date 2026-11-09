
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime, date

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

# ---------------- INVENTORY MANAGEMENT ----------------
def show_inventory(parent, page_title, clear_content):
    clear_content()
    page_title.config(text="Vaccine Inventory")

    selected_vaccine_id = None
    selected_batch_id = None
    vaccine_map = {}
    vaccine_display_map = {}

    # ---------------- HELPERS ----------------
    def show_db_error(error):
        messagebox.showerror(
            "Database Error",
            f"Unable to complete the operation.\n\n{error}"
        )

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
            cursor="hand2",
            padx=13,
            pady=8,
            borderwidth=0
        )

    def make_label(parent_frame, text, background=BG, font_size=9):
        return tk.Label(
            parent_frame,
            text=text,
            bg=background,
            fg=NAVY,
            font=("Segoe UI", font_size, "bold")
        )

    def make_tree(parent_frame, columns, widths):
        wrapper = tk.Frame(parent_frame, bg=WHITE)
        wrapper.pack(fill="both", expand=True, pady=5)

        tree = ttk.Treeview(
            wrapper,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for column, width in zip(columns, widths):
            tree.heading(column, text=column)
            tree.column(
                column,
                width=width,
                minwidth=60,
                anchor="center",
                stretch=False
            )

        vertical = ttk.Scrollbar(
            wrapper,
            orient="vertical",
            command=tree.yview
        )
        horizontal = ttk.Scrollbar(
            wrapper,
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

        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)

        return tree

    def create_form_entry(parent_frame, label, key, row, column, fields, width=28):
        make_label(parent_frame, label, WHITE).grid(
            row=row,
            column=column,
            sticky="w",
            padx=(14, 5),
            pady=9
        )

        entry = ttk.Entry(parent_frame, width=width)
        entry.grid(
            row=row,
            column=column + 1,
            sticky="ew",
            padx=(5, 14),
            pady=9
        )

        fields[key] = entry

    # ---------------- HEADER ----------------
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Vaccine Inventory Management",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Manage vaccine details, batches, expiry dates and available stock.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 10))

    # ---------------- NOTEBOOK ----------------
    notebook = ttk.Notebook(parent)
    notebook.pack(fill="both", expand=True, pady=5)

    catalogue_tab = tk.Frame(notebook, bg=BG)
    batch_tab = tk.Frame(notebook, bg=BG)

    notebook.add(catalogue_tab, text="Vaccine Catalogue")
    notebook.add(batch_tab, text="Batch Inventory")

    # =========================================================
    # VACCINE CATALOGUE
    # =========================================================
    make_label(
        catalogue_tab,
        "Vaccine Information",
        BG,
        15
    ).pack(anchor="w", pady=(8, 5))

    vaccine_form = tk.Frame(
        catalogue_tab,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    vaccine_form.pack(fill="x", pady=5)

    vaccine_fields = {}

    create_form_entry(
        vaccine_form, "Vaccine Name", "vaccine_name",
        0, 0, vaccine_fields
    )
    create_form_entry(
        vaccine_form, "Manufacturer", "manufacturer",
        0, 2, vaccine_fields
    )
    create_form_entry(
        vaccine_form, "Vaccine Type", "vaccine_type",
        1, 0, vaccine_fields
    )
    create_form_entry(
        vaccine_form, "Description", "description",
        1, 2, vaccine_fields
    )

    for column in range(4):
        vaccine_form.columnconfigure(column, weight=1)

    # ---------------- VACCINE SEARCH ----------------
    vaccine_search_frame = tk.Frame(catalogue_tab, bg=BG)
    vaccine_search_frame.pack(fill="x", pady=8)

    make_label(vaccine_search_frame, "Search Vaccine:").pack(
        side="left",
        padx=(0, 8)
    )

    vaccine_search = ttk.Entry(vaccine_search_frame, width=32)
    vaccine_search.pack(side="left")

    # ---------------- VACCINE TABLE ----------------
    vaccine_columns = (
        "ID",
        "Vaccine Name",
        "Manufacturer",
        "Type",
        "Description"
    )

    vaccine_table = make_tree(
        catalogue_tab,
        vaccine_columns,
        [55, 180, 160, 130, 300]
    )

    # ---------------- VACCINE FORM HELPERS ----------------
    def clear_vaccine_form():
        nonlocal selected_vaccine_id
        selected_vaccine_id = None

        for entry in vaccine_fields.values():
            entry.delete(0, tk.END)

        vaccine_table.selection_remove(
            vaccine_table.selection()
        )

    def get_vaccine_values():
        values = {
            key: entry.get().strip()
            for key, entry in vaccine_fields.items()
        }

        if not values["vaccine_name"]:
            messagebox.showwarning(
                "Missing Information",
                "Vaccine name is required."
            )
            return None

        return values

    # ---------------- VACCINE OPTIONS ----------------
    def refresh_vaccine_options():
        nonlocal vaccine_map, vaccine_display_map

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT vaccine_id, vaccine_name
                FROM Vaccine
                ORDER BY vaccine_name, vaccine_id
            """)

            records = cursor.fetchall()

            vaccine_map = {}
            vaccine_display_map = {}

            display_values = []

            for vaccine_id, vaccine_name in records:
                display = f"{vaccine_name} (ID: {vaccine_id})"
                vaccine_map[display] = vaccine_id
                vaccine_display_map[vaccine_id] = display
                display_values.append(display)

            current = vaccine_combo.get()
            vaccine_combo["values"] = display_values

            if current not in vaccine_map:
                vaccine_combo.set("")

        except sqlite3.Error as error:
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- LOAD VACCINES ----------------
    def load_vaccines(keyword=""):
        for item in vaccine_table.get_children():
            vaccine_table.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            search = f"%{keyword.strip()}%"

            cursor.execute("""
                SELECT
                    vaccine_id,
                    vaccine_name,
                    manufacturer,
                    vaccine_type,
                    description
                FROM Vaccine
                WHERE vaccine_name LIKE ?
                   OR manufacturer LIKE ?
                   OR vaccine_type LIKE ?
                   OR description LIKE ?
                ORDER BY vaccine_id DESC
            """, (search, search, search, search))

            records = cursor.fetchall()

            for record in records:
                vaccine_table.insert(
                    "",
                    "end",
                    values=record
                )

        except sqlite3.Error as error:
            show_db_error(error)

        finally:
            if conn:
                conn.close()

        refresh_vaccine_options()

    # ---------------- SELECT VACCINE ----------------
    def select_vaccine(event=None):
        nonlocal selected_vaccine_id

        selected = vaccine_table.selection()

        if not selected:
            return

        record = vaccine_table.item(
            selected[0]
        )["values"]

        selected_vaccine_id = record[0]

        mapping = {
            "vaccine_name": record[1],
            "manufacturer": record[2],
            "vaccine_type": record[3],
            "description": record[4]
        }

        for key, value in mapping.items():
            vaccine_fields[key].delete(0, tk.END)
            vaccine_fields[key].insert(
                0,
                "" if value is None else str(value)
            )

    vaccine_table.bind(
        "<<TreeviewSelect>>",
        select_vaccine
    )

    # ---------------- ADD VACCINE ----------------
    def add_vaccine():
        values = get_vaccine_values()

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Vaccine (
                    vaccine_name,
                    manufacturer,
                    vaccine_type,
                    description
                )
                VALUES (?, ?, ?, ?)
            """, (
                values["vaccine_name"],
                values["manufacturer"],
                values["vaccine_type"],
                values["description"]
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Vaccine added successfully."
            )

            clear_vaccine_form()
            load_vaccines(vaccine_search.get())

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- UPDATE VACCINE ----------------
    def update_vaccine():
        if selected_vaccine_id is None:
            messagebox.showwarning(
                "Select Vaccine",
                "Select a vaccine from the table first."
            )
            return

        values = get_vaccine_values()

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Vaccine
                SET
                    vaccine_name = ?,
                    manufacturer = ?,
                    vaccine_type = ?,
                    description = ?
                WHERE vaccine_id = ?
            """, (
                values["vaccine_name"],
                values["manufacturer"],
                values["vaccine_type"],
                values["description"],
                selected_vaccine_id
            ))

            if cursor.rowcount == 0:
                raise sqlite3.Error(
                    "The selected vaccine no longer exists."
                )

            conn.commit()

            messagebox.showinfo(
                "Updated",
                "Vaccine information updated successfully."
            )

            clear_vaccine_form()
            load_vaccines(vaccine_search.get())

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- DELETE VACCINE ----------------
    def delete_vaccine():
        if selected_vaccine_id is None:
            messagebox.showwarning(
                "Select Vaccine",
                "Select a vaccine to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this vaccine?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM Vaccine
                WHERE vaccine_id = ?
            """, (selected_vaccine_id,))

            conn.commit()

            messagebox.showinfo(
                "Deleted",
                "Vaccine deleted successfully."
            )

            clear_vaccine_form()
            load_vaccines(vaccine_search.get())

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Cannot Delete",
                "This vaccine is linked to vaccine batches or "
                "vaccination records. It cannot be deleted."
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- VACCINE BUTTONS ----------------
    vaccine_button_frame = tk.Frame(catalogue_tab, bg=BG)
    vaccine_button_frame.pack(fill="x", pady=8)

    make_button(
        vaccine_button_frame, "Add Vaccine",
        add_vaccine, BLUE
    ).pack(side="left", padx=4)

    make_button(
        vaccine_button_frame, "Update",
        update_vaccine, GREEN
    ).pack(side="left", padx=4)

    make_button(
        vaccine_button_frame, "Delete",
        delete_vaccine, RED
    ).pack(side="left", padx=4)

    make_button(
        vaccine_button_frame, "Clear Form",
        clear_vaccine_form, NAVY
    ).pack(side="left", padx=4)

    make_button(
        vaccine_button_frame, "Search",
        lambda: load_vaccines(vaccine_search.get()),
        BLUE
    ).pack(side="left", padx=4)

    make_button(
        vaccine_button_frame, "Refresh",
        lambda: (
            vaccine_search.delete(0, tk.END),
            load_vaccines()
        ),
        MUTED
    ).pack(side="left", padx=4)

    vaccine_search.bind(
        "<Return>",
        lambda event: load_vaccines(vaccine_search.get())
    )

    # =========================================================
    # BATCH INVENTORY
    # =========================================================
    make_label(
        batch_tab,
        "Vaccine Batch Information",
        BG,
        15
    ).pack(anchor="w", pady=(8, 5))

    batch_form = tk.Frame(
        batch_tab,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    batch_form.pack(fill="x", pady=5)

    batch_fields = {}

    create_form_entry(
        batch_form, "Batch Number", "batch_number",
        0, 0, batch_fields, 22
    )

    create_form_entry(
        batch_form, "Manufacturing Date", "manufacturing_date",
        0, 2, batch_fields, 22
    )

    create_form_entry(
        batch_form, "Expiry Date", "expiry_date",
        1, 0, batch_fields, 22
    )

    create_form_entry(
        batch_form, "Quantity Received", "quantity_received",
        1, 2, batch_fields, 22
    )

    create_form_entry(
        batch_form, "Quantity Available", "quantity_available",
        2, 0, batch_fields, 22
    )

    for column in range(4):
        batch_form.columnconfigure(column, weight=1)

    # ---------------- VACCINE SELECTION ----------------
    make_label(
        batch_form,
        "Select Vaccine",
        WHITE
    ).grid(
        row=2,
        column=2,
        sticky="w",
        padx=(14, 5),
        pady=9
    )

    vaccine_combo = ttk.Combobox(
        batch_form,
        state="readonly",
        width=25
    )
    vaccine_combo.grid(
        row=2,
        column=3,
        sticky="ew",
        padx=(5, 14),
        pady=9
    )

    # ---------------- BATCH SEARCH ----------------
    batch_search_frame = tk.Frame(batch_tab, bg=BG)
    batch_search_frame.pack(fill="x", pady=6)

    make_label(
        batch_search_frame,
        "Search Batch:"
    ).pack(side="left", padx=(0, 8))

    batch_search = ttk.Entry(batch_search_frame, width=32)
    batch_search.pack(side="left")

    # ---------------- BATCH TABLE ----------------
    batch_columns = (
        "ID",
        "Vaccine",
        "Batch Number",
        "Manufacturing Date",
        "Expiry Date",
        "Received",
        "Available"
    )

    batch_table = make_tree(
        batch_tab,
        batch_columns,
        [55, 160, 140, 135, 135, 100, 100]
    )

    # ---------------- CLEAR BATCH FORM ----------------
    def clear_batch_form():
        nonlocal selected_batch_id
        selected_batch_id = None

        for entry in batch_fields.values():
            entry.delete(0, tk.END)

        vaccine_combo.set("")

        batch_table.selection_remove(
            batch_table.selection()
        )

    # ---------------- VALIDATE BATCH ----------------
    def get_batch_values(is_new=False):
        values = {
            key: entry.get().strip()
            for key, entry in batch_fields.items()
        }

        display = vaccine_combo.get()

        if not display or display not in vaccine_map:
            messagebox.showwarning(
                "Select Vaccine",
                "Select a vaccine from the catalogue."
            )
            return None

        if not values["batch_number"]:
            messagebox.showwarning(
                "Missing Information",
                "Batch number is required."
            )
            return None

        try:
            manufacturing = datetime.strptime(
                values["manufacturing_date"],
                "%Y-%m-%d"
            ).date()

            expiry = datetime.strptime(
                values["expiry_date"],
                "%Y-%m-%d"
            ).date()

            if manufacturing > date.today():
                raise ValueError(
                    "Manufacturing date cannot be in the future."
                )

            if expiry <= manufacturing:
                raise ValueError(
                    "Expiry date must be after the manufacturing date."
                )

            if is_new and expiry <= date.today():
                raise ValueError(
                    "A new batch must have a future expiry date."
                )

        except ValueError as error:
            messagebox.showerror(
                "Invalid Dates",
                str(error) if str(error) else
                "Enter dates in YYYY-MM-DD format."
            )
            return None

        try:
            received = int(values["quantity_received"])
            available = int(values["quantity_available"])

            if received <= 0:
                raise ValueError

            if available < 0 or available > received:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Quantity received must be a positive whole number. "
                "Quantity available must be between zero and the "
                "quantity received."
            )
            return None

        return {
            "vaccine_id": vaccine_map[display],
            "batch_number": values["batch_number"],
            "manufacturing_date": values["manufacturing_date"],
            "expiry_date": values["expiry_date"],
            "quantity_received": received,
            "quantity_available": available
        }

    # ---------------- LOAD BATCHES ----------------
    def load_batches(keyword=""):
        for item in batch_table.get_children():
            batch_table.delete(item)

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            search = f"%{keyword.strip()}%"

            cursor.execute("""
                SELECT
                    B.batch_id,
                    V.vaccine_name,
                    B.batch_number,
                    B.manufacturing_date,
                    B.expiry_date,
                    B.quantity_received,
                    B.quantity_available
                FROM Vaccine_Batch B
                JOIN Vaccine V
                    ON B.vaccine_id = V.vaccine_id
                WHERE B.batch_number LIKE ?
                   OR V.vaccine_name LIKE ?
                ORDER BY B.expiry_date ASC, B.batch_id DESC
            """, (search, search))

            records = cursor.fetchall()

            for record in records:
                batch_table.insert(
                    "",
                    "end",
                    values=record
                )

        except sqlite3.Error as error:
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- ADD BATCH ----------------
    def add_batch():
        values = get_batch_values(is_new=True)

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Vaccine_Batch (
                    vaccine_id,
                    batch_number,
                    manufacturing_date,
                    expiry_date,
                    quantity_received,
                    quantity_available,
                    received_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                values["vaccine_id"],
                values["batch_number"],
                values["manufacturing_date"],
                values["expiry_date"],
                values["quantity_received"],
                values["quantity_available"],
                date.today().isoformat()
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Vaccine batch added successfully."
            )

            clear_batch_form()
            load_batches(batch_search.get())

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Batch Could Not Be Added",
                "The batch number may already exist, or the data "
                f"violates a database constraint.\n\n{error}"
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- SELECT BATCH ----------------
    def select_batch(event=None):
        nonlocal selected_batch_id

        selected = batch_table.selection()

        if not selected:
            return

        record = batch_table.item(
            selected[0]
        )["values"]

        selected_batch_id = record[0]

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    vaccine_id,
                    batch_number,
                    manufacturing_date,
                    expiry_date,
                    quantity_received,
                    quantity_available
                FROM Vaccine_Batch
                WHERE batch_id = ?
            """, (selected_batch_id,))

            batch = cursor.fetchone()

            if not batch:
                messagebox.showwarning(
                    "Batch Not Found",
                    "The selected batch no longer exists."
                )
                clear_batch_form()
                return

            vaccine_id = batch[0]
            vaccine_combo.set(
                vaccine_display_map.get(vaccine_id, "")
            )

            mapping = {
                "batch_number": batch[1],
                "manufacturing_date": batch[2],
                "expiry_date": batch[3],
                "quantity_received": batch[4],
                "quantity_available": batch[5]
            }

            for key, value in mapping.items():
                batch_fields[key].delete(0, tk.END)
                batch_fields[key].insert(
                    0,
                    "" if value is None else str(value)
                )

        except sqlite3.Error as error:
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    batch_table.bind(
        "<<TreeviewSelect>>",
        select_batch
    )

    # ---------------- UPDATE BATCH ----------------
    def update_batch():
        if selected_batch_id is None:
            messagebox.showwarning(
                "Select Batch",
                "Select a batch from the table first."
            )
            return

        values = get_batch_values(is_new=False)

        if not values:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Preserve the number of doses already used.
            cursor.execute("""
                SELECT
                    quantity_received,
                    quantity_available
                FROM Vaccine_Batch
                WHERE batch_id = ?
            """, (selected_batch_id,))

            old_batch = cursor.fetchone()

            if not old_batch:
                raise sqlite3.Error(
                    "The selected batch no longer exists."
                )

            old_received, old_available = old_batch
            doses_used = old_received - old_available

            if values["quantity_received"] < doses_used:
                messagebox.showerror(
                    "Invalid Quantity",
                    f"This batch has already had {doses_used} doses "
                    "used. Quantity received cannot be lower than "
                    "the number of doses already used."
                )
                return

            maximum_available = (
                values["quantity_received"] - doses_used
            )

            if values["quantity_available"] > maximum_available:
                messagebox.showerror(
                    "Invalid Stock",
                    f"This batch has {doses_used} doses already used. "
                    f"Available quantity cannot exceed "
                    f"{maximum_available}."
                )
                return

            cursor.execute("""
                UPDATE Vaccine_Batch
                SET
                    vaccine_id = ?,
                    batch_number = ?,
                    manufacturing_date = ?,
                    expiry_date = ?,
                    quantity_received = ?,
                    quantity_available = ?
                WHERE batch_id = ?
            """, (
                values["vaccine_id"],
                values["batch_number"],
                values["manufacturing_date"],
                values["expiry_date"],
                values["quantity_received"],
                values["quantity_available"],
                selected_batch_id
            ))

            conn.commit()

            messagebox.showinfo(
                "Updated",
                "Batch information updated successfully."
            )

            clear_batch_form()
            load_batches(batch_search.get())

        except sqlite3.IntegrityError as error:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Update Failed",
                f"The batch number may already exist or the update "
                f"violates a database constraint.\n\n{error}"
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- DELETE BATCH ----------------
    def delete_batch():
        if selected_batch_id is None:
            messagebox.showwarning(
                "Select Batch",
                "Select a batch to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this vaccine batch?"
        ):
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM Vaccine_Batch
                WHERE batch_id = ?
            """, (selected_batch_id,))

            conn.commit()

            messagebox.showinfo(
                "Deleted",
                "Vaccine batch deleted successfully."
            )

            clear_batch_form()
            load_batches(batch_search.get())

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Cannot Delete",
                "This batch is linked to vaccination records and "
                "cannot be deleted."
            )

        except sqlite3.Error as error:
            if conn:
                conn.rollback()
            show_db_error(error)

        finally:
            if conn:
                conn.close()

    # ---------------- BATCH BUTTONS ----------------
    batch_button_frame = tk.Frame(batch_tab, bg=BG)
    batch_button_frame.pack(fill="x", pady=8)

    make_button(
        batch_button_frame, "Add Batch",
        add_batch, BLUE
    ).pack(side="left", padx=4)

    make_button(
        batch_button_frame, "Update",
        update_batch, GREEN
    ).pack(side="left", padx=4)

    make_button(
        batch_button_frame, "Delete",
        delete_batch, RED
    ).pack(side="left", padx=4)

    make_button(
        batch_button_frame, "Clear Form",
        clear_batch_form, NAVY
    ).pack(side="left", padx=4)

    make_button(
        batch_button_frame, "Search",
        lambda: load_batches(batch_search.get()),
        BLUE
    ).pack(side="left", padx=4)

    make_button(
        batch_button_frame, "Refresh",
        lambda: (
            batch_search.delete(0, tk.END),
            load_batches()
        ),
        MUTED
    ).pack(side="left", padx=4)

    batch_search.bind(
        "<Return>",
        lambda event: load_batches(batch_search.get())
    )

    # ---------------- INITIAL LOAD ----------------
    load_vaccines()
    load_batches()
