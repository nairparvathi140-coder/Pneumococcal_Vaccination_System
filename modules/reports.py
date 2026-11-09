
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import csv
from datetime import date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")

BG = "#F3F6FB"
WHITE = "#FFFFFF"
NAVY = "#172B4D"
BLUE = "#2878D0"
GREEN = "#159D79"
MUTED = "#718096"
LOW_STOCK_LIMIT = 10


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def show_reports(parent, page_title, clear_content, account):
    clear_content()
    page_title.config(text="Reports & Analytics")

    # ---------------- PAGE HEADER ----------------
    tk.Label(
        parent,
        text="Reports & Analytics",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w")

    tk.Label(
        parent,
        text="Visual insights into vaccination, inventory, appointments and eligibility.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 8))

    main_tabs = ttk.Notebook(parent)
    main_tabs.pack(fill="both", expand=True, pady=5)

    overview_tab = tk.Frame(main_tabs, bg=BG)
    vaccination_tab = tk.Frame(main_tabs, bg=BG)
    inventory_tab = tk.Frame(main_tabs, bg=BG)
    appointment_tab = tk.Frame(main_tabs, bg=BG)

    main_tabs.add(overview_tab, text="Overview")
    main_tabs.add(vaccination_tab, text="Vaccination Reports")
    main_tabs.add(inventory_tab, text="Inventory Reports")
    main_tabs.add(appointment_tab, text="Appointments & Eligibility")

    report_tables = {}
    chart_canvases = {}

    # ---------------- CHART PAGE ----------------
    def make_chart_page(notebook, title, key):
        page = tk.Frame(notebook, bg=WHITE)
        notebook.add(page, text=title)

        chart_frame = tk.Frame(page, bg=WHITE)
        chart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        chart_canvases[key] = {
            "frame": chart_frame,
            "canvas": None
        }

        return page

    # ---------------- DATA TABLE PAGE ----------------
    def make_data_page(notebook, title, name, columns, widths):
        page = tk.Frame(notebook, bg=WHITE)
        notebook.add(page, text=title)

        tk.Label(
            page,
            text=title,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=12, pady=10)

        table_frame = tk.Frame(page, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        for col, width in zip(columns, widths):
            table.heading(col, text=col)
            table.column(
                col,
                width=width,
                minwidth=65,
                anchor="center"
            )

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=table.yview
        )

        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=table.xview
        )

        table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        report_tables[name] = table

        tk.Button(
            page,
            text="Export CSV",
            command=lambda: export_table(name),
            bg=BLUE,
            fg=WHITE,
            activebackground=NAVY,
            activeforeground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(anchor="e", padx=10, pady=8)

        return table

    # ---------------- TABLE UTILITIES ----------------
    def fill_table(table, records):
        for item in table.get_children():
            table.delete(item)

        for record in records:
            table.insert("", "end", values=record)

    def export_table(name):
        table = report_tables.get(name)

        if table is None:
            return

        rows = [
            table.item(item)["values"]
            for item in table.get_children()
        ]

        if not rows:
            messagebox.showinfo(
                "No Data",
                "There are no records to export."
            )
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{name}_report.csv"
        )

        if not filepath:
            return

        try:
            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(table["columns"])
                writer.writerows(rows)

            messagebox.showinfo(
                "Export Successful",
                f"Report saved successfully:\n{filepath}"
            )

        except (OSError, csv.Error) as e:
            messagebox.showerror("Export Error", str(e))

    # ---------------- CHART UTILITIES ----------------
    def draw_chart(key, chart_type, title, labels, values, x_label="", y_label=""):
        chart_info = chart_canvases[key]
        frame = chart_info["frame"]
        old_canvas = chart_info["canvas"]

        if old_canvas is not None:
            old_canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(8, 4.2), dpi=90)
        ax = fig.add_subplot(111)

        fig.subplots_adjust(
            left=0.12,
            right=0.95,
            top=0.88,
            bottom=0.22
        )

        valid_data = bool(labels and values and sum(values) > 0)

        if not valid_data:
            ax.text(
                0.5,
                0.5,
                "No data available yet",
                ha="center",
                va="center",
                fontsize=13,
                color=MUTED,
                transform=ax.transAxes
            )
            ax.set_title(
                title,
                fontsize=13,
                fontweight="bold",
                color=NAVY
            )
            ax.set_axis_off()

        elif chart_type == "pie":
            ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90
            )
            ax.set_title(
                title,
                fontsize=13,
                fontweight="bold",
                color=NAVY
            )

        else:
            bars = ax.bar(labels, values)

            ax.set_title(
                title,
                fontsize=13,
                fontweight="bold",
                color=NAVY
            )

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.tick_params(axis="x", labelrotation=25)

            for label in ax.get_xticklabels():
                label.set_ha("right")

            ax.grid(axis="y", linestyle="--", alpha=0.3)
            ax.set_axisbelow(True)
            ax.bar_label(bars, padding=3)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        chart_info["canvas"] = canvas

    # ---------------- OVERVIEW CARDS ----------------
    cards_frame = tk.Frame(overview_tab, bg=BG)
    cards_frame.pack(fill="x", padx=5, pady=5)

    overview_values = {}

    card_definitions = [
        ("Total Patients", "patients", BLUE),
        ("Vaccinations", "vaccinations", GREEN),
        ("Appointments", "appointments", "#8B5CF6"),
        ("Available Doses", "stock", "#D97706"),
        ("Pending Assessments", "pending", "#D9534F")
    ]

    for i, (label, key, color) in enumerate(card_definitions):
        row = i // 3
        col = i % 3

        card = tk.Frame(
            cards_frame,
            bg=WHITE,
            highlightbackground="#E3EAF3",
            highlightthickness=1
        )

        card.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=4,
            pady=4,
            ipadx=4,
            ipady=8
        )

        tk.Label(
            card,
            text=label,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
            wraplength=150
        ).pack(padx=5, pady=(6, 3))

        value_label = tk.Label(
            card,
            text="0",
            bg=WHITE,
            fg=color,
            font=("Segoe UI", 20, "bold")
        )

        value_label.pack(padx=5, pady=(0, 6))
        overview_values[key] = value_label

    for col in range(3):
        cards_frame.columnconfigure(col, weight=1)

    # ---------------- OVERVIEW TABS ----------------
    overview_notebook = ttk.Notebook(overview_tab)
    overview_notebook.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    make_chart_page(
        overview_notebook,
        "Vaccination Trend",
        "overview_trend"
    )

    make_data_page(
        overview_notebook,
        "System Summary",
        "system_summary",
        ("Metric", "Value"),
        [300, 180]
    )

    # ---------------- VACCINATION REPORTS ----------------
    vaccine_notebook = ttk.Notebook(vaccination_tab)
    vaccine_notebook.pack(fill="both", expand=True, padx=5, pady=5)

    make_chart_page(
        vaccine_notebook,
        "Monthly Trend",
        "vaccine_monthly_chart"
    )

    make_data_page(
        vaccine_notebook,
        "Monthly Data",
        "monthly_vaccinations",
        ("Month", "Total Doses"),
        [250, 180]
    )

    make_chart_page(
        vaccine_notebook,
        "Vaccine Distribution",
        "vaccine_distribution_chart"
    )

    make_data_page(
        vaccine_notebook,
        "Vaccine Data",
        "vaccination_by_vaccine",
        ("Vaccine", "Total Doses", "Unique Patients"),
        [250, 150, 160]
    )

    # ---------------- INVENTORY REPORTS ----------------
    inventory_notebook = ttk.Notebook(inventory_tab)
    inventory_notebook.pack(fill="both", expand=True, padx=5, pady=5)

    make_chart_page(
        inventory_notebook,
        "Stock by Vaccine",
        "stock_by_vaccine_chart"
    )

    make_data_page(
        inventory_notebook,
        "Batch Details",
        "inventory",
        (
            "Vaccine",
            "Batch Number",
            "Expiry Date",
            "Received",
            "Available",
            "Stock Status"
        ),
        [170, 120, 120, 90, 90, 150]
    )

    make_chart_page(
        inventory_notebook,
        "Batch Status",
        "batch_status_chart"
    )

    make_data_page(
        inventory_notebook,
        "Batch Status Data",
        "batch_status",
        ("Stock Status", "Number of Batches"),
        [250, 180]
    )

    # ---------------- APPOINTMENT AND ELIGIBILITY REPORTS ----------------
    appointment_notebook = ttk.Notebook(appointment_tab)
    appointment_notebook.pack(fill="both", expand=True, padx=5, pady=5)

    make_chart_page(
        appointment_notebook,
        "Appointment Status",
        "appointment_chart"
    )

    make_data_page(
        appointment_notebook,
        "Appointment Data",
        "appointments",
        ("Appointment Status", "Total Appointments"),
        [250, 180]
    )

    make_chart_page(
        appointment_notebook,
        "Eligibility Distribution",
        "eligibility_chart"
    )

    make_data_page(
        appointment_notebook,
        "Eligibility Data",
        "eligibility",
        ("Eligibility Status", "Total Assessments"),
        [250, 180]
    )

    make_chart_page(
        appointment_notebook,
        "Risk Categories",
        "risk_chart"
    )

    make_data_page(
        appointment_notebook,
        "Risk Data",
        "risk_categories",
        ("Risk Category", "Total Assessments"),
        [250, 180]
    )

    # ---------------- REFRESH REPORTS ----------------
    def refresh_reports():
        conn = None

        try:
            conn = get_connection()
            cur = conn.cursor()
            today = date.today().isoformat()

            # OVERVIEW COUNTS
            cur.execute("SELECT COUNT(*) FROM Patient")
            patients = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM Vaccination")
            vaccinations = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM Appointment")
            appointments = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(quantity_available), 0)
                FROM Vaccine_Batch
                WHERE date(expiry_date) > date(?)
                  AND quantity_available > 0
            """, (today,))

            stock = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM Eligibility_Assessment
                WHERE eligibility_status = 'Pending Review'
            """)

            pending = cur.fetchone()[0]

            overview_values["patients"].config(text=str(patients))
            overview_values["vaccinations"].config(text=str(vaccinations))
            overview_values["appointments"].config(text=str(appointments))
            overview_values["stock"].config(text=str(stock))
            overview_values["pending"].config(text=str(pending))

            summary = [
                ("Registered Patients", patients),
                ("Vaccination Records", vaccinations),
                ("Total Appointments", appointments),
                ("Available Vaccine Doses", stock),
                ("Pending Eligibility Assessments", pending),
                ("Report Generated On", date.today().strftime("%d %B %Y"))
            ]

            fill_table(
                report_tables["system_summary"],
                summary
            )

            # MONTHLY VACCINATION COUNTS
            cur.execute("""
                SELECT
                    substr(date_administered, 1, 7),
                    COUNT(*)
                FROM Vaccination
                WHERE date_administered IS NOT NULL
                  AND date_administered != ''
                GROUP BY substr(date_administered, 1, 7)
                ORDER BY substr(date_administered, 1, 7)
            """)

            monthly_rows = cur.fetchall()

            fill_table(
                report_tables["monthly_vaccinations"],
                monthly_rows
            )

            monthly_labels = [row[0] for row in monthly_rows]
            monthly_values = [row[1] for row in monthly_rows]

            draw_chart(
                "overview_trend",
                "bar",
                "Monthly Vaccination Activity",
                monthly_labels,
                monthly_values,
                "Month",
                "Doses"
            )

            draw_chart(
                "vaccine_monthly_chart",
                "bar",
                "Monthly Vaccination Activity",
                monthly_labels,
                monthly_values,
                "Month",
                "Doses"
            )

            # VACCINE-WISE DISTRIBUTION
            cur.execute("""
                SELECT
                    VC.vaccine_name,
                    COUNT(V.vaccination_id),
                    COUNT(DISTINCT V.patient_id)
                FROM Vaccine VC
                LEFT JOIN Vaccination V
                    ON VC.vaccine_id = V.vaccine_id
                GROUP BY VC.vaccine_id, VC.vaccine_name
                ORDER BY VC.vaccine_name
            """)

            vaccine_rows = cur.fetchall()

            fill_table(
                report_tables["vaccination_by_vaccine"],
                vaccine_rows
            )

            distribution_rows = [
                row for row in vaccine_rows if row[1] > 0
            ]

            draw_chart(
                "vaccine_distribution_chart",
                "pie",
                "Vaccinations by Vaccine",
                [row[0] for row in distribution_rows],
                [row[1] for row in distribution_rows]
            )

            # INVENTORY BATCH DETAILS
            cur.execute("""
                SELECT
                    VC.vaccine_name,
                    B.batch_number,
                    B.expiry_date,
                    B.quantity_received,
                    B.quantity_available,
                    CASE
                        WHEN date(B.expiry_date) IS NULL
                            THEN 'Invalid Expiry Date'
                        WHEN date(B.expiry_date) <= date(?)
                            THEN 'Expired'
                        WHEN B.quantity_available <= 0
                            THEN 'Out of Stock'
                        WHEN B.quantity_available <= ?
                            THEN 'Low Stock'
                        ELSE 'Available'
                    END
                FROM Vaccine_Batch B
                JOIN Vaccine VC
                    ON VC.vaccine_id = B.vaccine_id
                ORDER BY date(B.expiry_date)
            """, (today, LOW_STOCK_LIMIT))

            inventory_rows = cur.fetchall()

            fill_table(
                report_tables["inventory"],
                inventory_rows
            )

            # AVAILABLE STOCK BY VACCINE
            cur.execute("""
                SELECT
                    VC.vaccine_name,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN date(B.expiry_date) > date(?)
                                THEN B.quantity_available
                                ELSE 0
                            END
                        ),
                        0
                    )
                FROM Vaccine VC
                LEFT JOIN Vaccine_Batch B
                    ON B.vaccine_id = VC.vaccine_id
                GROUP BY VC.vaccine_id, VC.vaccine_name
                ORDER BY VC.vaccine_name
            """, (today,))

            stock_rows = cur.fetchall()

            stock_chart_rows = [
                row for row in stock_rows if row[1] > 0
            ]

            draw_chart(
                "stock_by_vaccine_chart",
                "bar",
                "Available Doses by Vaccine",
                [row[0] for row in stock_chart_rows],
                [row[1] for row in stock_chart_rows],
                "Vaccine",
                "Doses"
            )

            # BATCH STOCK STATUS
            cur.execute("""
                SELECT
                    CASE
                        WHEN date(expiry_date) IS NULL
                            THEN 'Invalid Expiry Date'
                        WHEN date(expiry_date) <= date(?)
                            THEN 'Expired'
                        WHEN quantity_available <= 0
                            THEN 'Out of Stock'
                        WHEN quantity_available <= ?
                            THEN 'Low Stock'
                        ELSE 'Available'
                    END AS stock_status,
                    COUNT(*)
                FROM Vaccine_Batch
                GROUP BY stock_status
                ORDER BY stock_status
            """, (today, LOW_STOCK_LIMIT))

            batch_rows = cur.fetchall()

            fill_table(
                report_tables["batch_status"],
                batch_rows
            )

            draw_chart(
                "batch_status_chart",
                "pie",
                "Batch Stock Status",
                [row[0] for row in batch_rows],
                [row[1] for row in batch_rows]
            )

            # APPOINTMENT STATUS
            cur.execute("""
                SELECT status, COUNT(*)
                FROM Appointment
                GROUP BY status
                ORDER BY status
            """)

            appointment_rows = cur.fetchall()

            fill_table(
                report_tables["appointments"],
                appointment_rows
            )

            draw_chart(
                "appointment_chart",
                "pie",
                "Appointment Status Distribution",
                [row[0] for row in appointment_rows],
                [row[1] for row in appointment_rows]
            )

            # ELIGIBILITY STATUS
            cur.execute("""
                SELECT eligibility_status, COUNT(*)
                FROM Eligibility_Assessment
                GROUP BY eligibility_status
                ORDER BY eligibility_status
            """)

            eligibility_rows = cur.fetchall()

            fill_table(
                report_tables["eligibility"],
                eligibility_rows
            )

            draw_chart(
                "eligibility_chart",
                "pie",
                "Patient Eligibility Distribution",
                [row[0] for row in eligibility_rows],
                [row[1] for row in eligibility_rows]
            )

            # RISK CATEGORIES
            cur.execute("""
                SELECT risk_category, COUNT(*)
                FROM Eligibility_Assessment
                WHERE risk_category IS NOT NULL
                  AND risk_category != ''
                GROUP BY risk_category
                ORDER BY risk_category
            """)

            risk_rows = cur.fetchall()

            fill_table(
                report_tables["risk_categories"],
                risk_rows
            )

            draw_chart(
                "risk_chart",
                "bar",
                "Patient Risk Category Distribution",
                [row[0] for row in risk_rows],
                [row[1] for row in risk_rows],
                "Risk Category",
                "Assessments"
            )

        except sqlite3.Error as e:
            messagebox.showerror(
                "Report Database Error",
                f"Could not refresh reports:\n{e}"
            )

        except Exception as e:
            messagebox.showerror(
                "Report Error",
                f"An unexpected error occurred:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ---------------- REFRESH BUTTON ----------------
    refresh_frame = tk.Frame(parent, bg=BG)
    refresh_frame.pack(fill="x", pady=3)

    tk.Button(
        refresh_frame,
        text="Refresh All Reports",
        command=refresh_reports,
        bg=GREEN,
        fg=WHITE,
        activebackground=NAVY,
        activeforeground=WHITE,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=14,
        pady=8
    ).pack(anchor="e", padx=5)

    # Initial report loading
    refresh_reports()
