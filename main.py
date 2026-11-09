
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modules.appointments import show_appointments, show_patient_booking
from modules.eligibility import show_eligibility
from modules.registration import show_staff_registration, show_patient_registration
from modules.staff_requests import show_staff_requests
from modules.auth import authenticate_user
from modules.patients import show_patients
from modules.staff import show_staff
from modules.inventory import show_inventory
from modules.password_recovery import show_forgot_password
from modules.vaccinations import show_vaccinations
from modules.reports import show_reports

# DATABASE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pneumococcal.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def pending_staff_count():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM User_Account WHERE role='staff' AND account_status='pending'"
        )
        return cursor.fetchone()[0]
    except sqlite3.Error:
        return 0
    finally:
        if conn:
            conn.close()


# GLOBAL THEME PALETTES
THEMES = {
    "dark": {
        "bg": "#000000",
        "panel": "#000000",
        "text": "#00E5FF",
        "muted": "#00CFE8",
        "icon": "#00E5FF",
        "border": "#00E5FF",
        "button": "#000000",
        "button_hover": "#10313A",
        "sidebar": "#000000",
        "sidebar_hover": "#10313A",
        "accent": "#00E5FF",
        "soft": "#000000",
        "input": "#000000",
        "selected": "#10313A",
        "table_heading": "#000000",
        "danger": "#000000"
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#FFFFFF",
        "text": "#17345B",
        "muted": "#52657D",
        "icon": "#17345B",
        "border": "#17345B",
        "button": "#FFFFFF",
        "button_hover": "#EAF2FA",
        "sidebar": "#FFFFFF",
        "sidebar_hover": "#EAF2FA",
        "accent": "#17345B",
        "soft": "#FFFFFF",
        "input": "#FFFFFF",
        "selected": "#DCEBFA",
        "table_heading": "#FFFFFF",
        "danger": "#FFFFFF"
    }
}

CURRENT_THEME = "dark"

# Legacy constants retained for compatibility with existing modules.
NAVY = "#172B4D"
NAVY_LIGHT = "#243B60"
BLUE = "#2878D0"
BG = "#F3F6FB"
WHITE = "#FFFFFF"
TEXT = "#243247"
MUTED = "#718096"
GREEN = "#159D79"
RED = "#D9534F"


def get_app_theme_colors(theme_name=None):
    return dict(THEMES[theme_name or CURRENT_THEME])


style = None


def configure_app_styles(theme_name=None):
    global style
    if style is None:
        style = ttk.Style(root)

    t = get_app_theme_colors(theme_name)
    style.theme_use("clam")

    style.configure(
        ".",
        background=t["bg"],
        foreground=t["text"],
        fieldbackground=t["input"],
        font=("Segoe UI", 10)
    )

    style.configure("TFrame", background=t["bg"])
    style.configure("TLabel", background=t["bg"], foreground=t["text"])

    style.configure(
        "TLabelframe",
        background=t["bg"],
        bordercolor=t["border"],
        relief="solid"
    )
    style.configure(
        "TLabelframe.Label",
        background=t["bg"],
        foreground=t["text"]
    )

    style.configure(
        "TEntry",
        fieldbackground=t["input"],
        foreground=t["text"],
        insertcolor=t["text"],
        bordercolor=t["border"],
        lightcolor=t["border"],
        darkcolor=t["border"],
        relief="solid"
    )

    style.configure(
        "TCombobox",
        fieldbackground=t["input"],
        background=t["input"],
        foreground=t["text"],
        arrowcolor=t["text"],
        bordercolor=t["border"],
        lightcolor=t["border"],
        darkcolor=t["border"],
        relief="solid"
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", t["input"])],
        foreground=[("readonly", t["text"])],
        selectbackground=[("readonly", t["selected"])],
        selectforeground=[("readonly", t["text"])]
    )

    style.configure(
        "TButton",
        background=t["button"],
        foreground=t["text"],
        bordercolor=t["border"],
        lightcolor=t["border"],
        darkcolor=t["border"],
        relief="solid",
        borderwidth=1,
        padding=(10, 6)
    )
    style.map(
        "TButton",
        background=[
            ("active", t["button_hover"]),
            ("pressed", t["selected"])
        ],
        foreground=[("active", t["text"])]
    )

    style.configure(
        "TNotebook",
        background=t["bg"],
        bordercolor=t["border"]
    )
    style.configure(
        "TNotebook.Tab",
        background=t["panel"],
        foreground=t["text"],
        bordercolor=t["border"],
        padding=(13, 8),
        font=("Segoe UI", 9, "bold")
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", t["panel"]),
            ("active", t["button_hover"])
        ],
        foreground=[
            ("selected", t["text"]),
            ("active", t["text"])
        ]
    )

    style.configure(
        "Treeview",
        background=t["panel"],
        foreground=t["text"],
        fieldbackground=t["panel"],
        rowheight=34,
        bordercolor=t["border"],
        relief="solid",
        font=("Segoe UI", 10)
    )
    style.configure(
        "Treeview.Heading",
        background=t["table_heading"],
        foreground=t["text"],
        bordercolor=t["border"],
        font=("Segoe UI", 10, "bold"),
        relief="solid"
    )
    style.map(
        "Treeview",
        background=[("selected", t["selected"])],
        foreground=[("selected", t["text"])]
    )

    style.configure(
        "TScrollbar",
        background=t["panel"],
        troughcolor=t["bg"],
        bordercolor=t["border"],
        arrowcolor=t["text"]
    )

    style.configure(
        "TCheckbutton",
        background=t["bg"],
        foreground=t["text"]
    )
    style.map(
        "TCheckbutton",
        background=[("active", t["bg"])],
        foreground=[("disabled", t["muted"])]
    )

    style.configure(
        "TRadiobutton",
        background=t["bg"],
        foreground=t["text"]
    )
    style.map(
        "TRadiobutton",
        background=[("active", t["bg"])],
        foreground=[("disabled", t["muted"])]
    )

    return style


def apply_complete_theme(widget, theme_name=None):
    """Apply the selected theme to existing widgets without rebuilding pages."""
    t = get_app_theme_colors(theme_name)
    configure_app_styles(theme_name)

    def recolour(current):
        try:
            if isinstance(current, (tk.Tk, tk.Toplevel)):
                current.configure(bg=t["bg"])

            elif isinstance(current, (tk.Frame, tk.LabelFrame)):
                current.configure(
                    bg=t["bg"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"]
                )

            elif isinstance(current, tk.Canvas):
                current.configure(
                    bg=t["bg"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"]
                )

            elif isinstance(current, (tk.Label, tk.Message)):
                current.configure(bg=t["bg"], fg=t["text"])

            elif isinstance(current, tk.Button):
                current.configure(
                    bg=t["button"],
                    fg=t["text"],
                    activebackground=t["button_hover"],
                    activeforeground=t["text"],
                    disabledforeground=t["muted"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"],
                    highlightthickness=1,
                    bd=1,
                    relief="solid"
                )

            elif isinstance(current, (tk.Entry, tk.Spinbox, tk.Text, tk.Listbox)):
                current.configure(
                    bg=t["input"],
                    fg=t["text"],
                    insertbackground=t["text"],
                    selectbackground=t["selected"],
                    selectforeground=t["text"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"],
                    highlightthickness=1,
                    bd=1,
                    relief="solid"
                )

            elif isinstance(current, (tk.Checkbutton, tk.Radiobutton)):
                current.configure(
                    bg=t["bg"],
                    fg=t["text"],
                    activebackground=t["bg"],
                    activeforeground=t["text"],
                    selectcolor=t["panel"]
                )

            elif isinstance(current, tk.Menubutton):
                current.configure(
                    bg=t["button"],
                    fg=t["text"],
                    activebackground=t["button_hover"],
                    activeforeground=t["text"]
                )

        except (tk.TclError, TypeError):
            pass

        try:
            for child in current.winfo_children():
                recolour(child)
        except tk.TclError:
            pass

    recolour(widget)


# WINDOW
root = tk.Tk()
root.title("PneumoCare | Hospital Vaccination Management")
root.geometry("1250x760")
root.minsize(950, 620)
root.configure(bg=THEMES[CURRENT_THEME]["bg"])

configure_app_styles(CURRENT_THEME)


def launch_themed(callback):
    callback()
    apply_complete_theme(root, CURRENT_THEME)


# LOGIN AND LANDING PAGE
def show_login():
    for widget in root.winfo_children():
        widget.destroy()

    t = THEMES[CURRENT_THEME]
    root.configure(bg=t["bg"])

    def draw_lungs(canvas, color, bg):
        canvas.delete("all")
        width = 3
        canvas.create_line(50, 5, 50, 27, fill=color, width=width)
        canvas.create_line(43, 8, 57, 8, fill=color, width=width)
        canvas.create_line(43, 15, 57, 15, fill=color, width=width)
        canvas.create_line(50, 25, 37, 36, fill=color, width=width)
        canvas.create_line(50, 25, 63, 36, fill=color, width=width)
        left = [38,31,29,29,20,37,17,49,20,62,28,69,37,64,43,51,44,38]
        right = [62,31,71,29,80,37,83,49,80,62,72,69,63,64,57,51,56,38]
        canvas.create_polygon(left, smooth=True, outline=color, fill=bg, width=width)
        canvas.create_polygon(right, smooth=True, outline=color, fill=bg, width=width)
        canvas.create_line(38,35,32,47,28,56, fill=color, width=2)
        canvas.create_line(62,35,68,47,72,56, fill=color, width=2)
        canvas.create_line(38,35,43,43, fill=color, width=2)
        canvas.create_line(62,35,57,43, fill=color, width=2)

    def draw_portal_icon(canvas, icon_type, color, bg):
        canvas.delete("all")
        width = 2.7

        if icon_type == "patient":
            canvas.create_oval(42,5,58,21, outline=color, width=width)
            canvas.create_arc(28,20,72,65, start=0, extent=180, style="arc", outline=color, width=width)
            canvas.create_line(28,42,28,59, fill=color, width=width)
            canvas.create_line(72,42,72,59, fill=color, width=width)

        elif icon_type == "admin":
            points = [50,3,68,12,65,39,50,54,35,39,32,12]
            canvas.create_polygon(points, outline=color, fill=bg, width=width)
            canvas.create_line(42,28,48,34,59,21, fill=color, width=width)

        elif icon_type == "staff":
            canvas.create_oval(25,7,39,21, outline=color, width=width)
            canvas.create_oval(61,7,75,21, outline=color, width=width)
            canvas.create_arc(15,23,49,61, start=0, extent=180, style="arc", outline=color, width=width)
            canvas.create_arc(51,23,85,61, start=0, extent=180, style="arc", outline=color, width=width)
            canvas.create_line(49,36,55,30, fill=color, width=width)

    def show_portal_login(selected_role):
        for widget in root.winfo_children():
            widget.destroy()

        current = THEMES[CURRENT_THEME]
        root.configure(bg=current["bg"])

        page = tk.Frame(root, bg=current["bg"])
        page.pack(fill="both", expand=True)

        def toggle_login_theme():
            global CURRENT_THEME
            CURRENT_THEME = "light" if CURRENT_THEME == "dark" else "dark"
            configure_app_styles(CURRENT_THEME)
            show_portal_login(selected_role)

        tk.Button(
            page,
            text="☀  Light mode" if CURRENT_THEME == "dark" else "☾  Dark mode",
            command=toggle_login_theme,
            bg=current["button"],
            fg=current["text"],
            activebackground=current["button_hover"],
            activeforeground=current["text"],
            relief="solid",
            highlightbackground=current["border"],
            highlightthickness=1,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=13,
            pady=7
        ).place(relx=0.98, rely=0.025, anchor="ne")

        panel = tk.Frame(
            page,
            bg=current["panel"],
            highlightbackground=current["border"],
            highlightthickness=1,
            padx=48,
            pady=28
        )
        panel.place(relx=0.5, rely=0.5, anchor="center")

        role_details = {
            "patient": ("Patient Portal", "Access your personal vaccination records."),
            "admin": ("Administrator Login", "Manage the PneumoCare system."),
            "staff": ("Staff & Doctor Portal", "Access clinical and hospital services.")
        }

        title, subtitle = role_details[selected_role]

        logo = tk.Canvas(panel, width=100, height=82, bg=current["panel"], highlightthickness=0)
        logo.pack()
        draw_lungs(logo, current["icon"], current["panel"])

        tk.Label(panel, text="PneumoCare", bg=current["panel"], fg=current["text"], font=("Segoe UI",27,"bold")).pack()
        tk.Label(panel, text="HOSPITAL VACCINATION MANAGEMENT SYSTEM", bg=current["panel"], fg=current["muted"], font=("Segoe UI",9)).pack(pady=(3,20))
        tk.Label(panel, text=title, bg=current["panel"], fg=current["text"], font=("Segoe UI",17,"bold")).pack(anchor="w")
        tk.Label(panel, text=subtitle, bg=current["panel"], fg=current["muted"], font=("Segoe UI",10)).pack(anchor="w", pady=(4,18))

        tk.Label(panel, text="Username", bg=current["panel"], fg=current["text"], font=("Segoe UI",10,"bold")).pack(anchor="w", pady=(0,5))
        username_entry = ttk.Entry(panel, width=38, font=("Segoe UI",11))
        username_entry.pack(fill="x", pady=(0,13))

        tk.Label(panel, text="Password", bg=current["panel"], fg=current["text"], font=("Segoe UI",10,"bold")).pack(anchor="w", pady=(0,5))
        password_entry = ttk.Entry(panel, width=38, show="*", font=("Segoe UI",11))
        password_entry.pack(fill="x", pady=(0,7))

        show_password = tk.BooleanVar(value=False)

        def toggle_password():
            password_entry.config(show="" if show_password.get() else "*")

        tk.Checkbutton(
            panel,
            text="Show password",
            variable=show_password,
            command=toggle_password,
            bg=current["panel"],
            fg=current["muted"],
            selectcolor=current["bg"],
            activebackground=current["panel"],
            activeforeground=current["text"],
            font=("Segoe UI",9),
            relief="flat"
        ).pack(anchor="w", pady=(0,13))

        def login():
            username = username_entry.get().strip()
            password = password_entry.get()

            if not username or not password:
                messagebox.showwarning("Missing Information", "Enter your username and password.", parent=root)
                return

            result = authenticate_user(username, password, selected_role)

            if not result["success"]:
                messagebox.showerror("Login Failed", result["message"], parent=root)
                return

            open_dashboard(result)

        tk.Button(
            panel,
            text="LOGIN",
            command=login,
            bg=current["accent"],
            fg=current["bg"],
            activebackground=current["button_hover"],
            activeforeground=current["text"],
            font=("Segoe UI",11,"bold"),
            relief="solid",
            highlightbackground=current["border"],
            highlightthickness=1,
            cursor="hand2",
            pady=11
        ).pack(fill="x", pady=(4,10))

        tk.Button(
            panel,
            text="Forgot Password?",
            command=lambda: launch_themed(lambda: show_forgot_password(root)),
            bg=current["panel"],
            fg=current["icon"],
            activebackground=current["button_hover"],
            activeforeground=current["text"],
            relief="flat",
            font=("Segoe UI",9,"bold"),
            cursor="hand2"
        ).pack(anchor="e", pady=(0,10))

        tk.Button(
            panel,
            text="← Back to Portals",
            command=show_login,
            bg=current["panel"],
            fg=current["muted"],
            activebackground=current["button_hover"],
            activeforeground=current["text"],
            relief="flat",
            font=("Segoe UI",9),
            cursor="hand2"
        ).pack()

        username_entry.bind("<Return>", lambda event: password_entry.focus())
        password_entry.bind("<Return>", lambda event: login())
        username_entry.focus()

    # LANDING PAGE
    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True, padx=24, pady=18)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(3, weight=1)

    topbar = tk.Frame(outer, bg=t["bg"])
    topbar.grid(row=0, column=0, sticky="ew")
    topbar.grid_columnconfigure(0, weight=1)

    tk.Label(
        topbar,
        text="PNEUMOCARE  |  HEALTHCARE PORTAL",
        bg=t["bg"],
        fg=t["muted"],
        font=("Segoe UI",9,"bold")
    ).grid(row=0,column=0,sticky="w")

    def toggle_theme():
        global CURRENT_THEME
        CURRENT_THEME = "light" if CURRENT_THEME == "dark" else "dark"
        configure_app_styles(CURRENT_THEME)
        show_login()

    tk.Button(
        topbar,
        text="☀  Light mode" if CURRENT_THEME == "dark" else "☾  Dark mode",
        command=toggle_theme,
        bg=t["button"],
        fg=t["text"],
        activebackground=t["button_hover"],
        activeforeground=t["text"],
        relief="solid",
        highlightbackground=t["border"],
        highlightthickness=1,
        font=("Segoe UI",9,"bold"),
        cursor="hand2",
        padx=13,
        pady=7
    ).grid(row=0,column=1,sticky="e")

    header = tk.Frame(outer, bg=t["bg"])
    header.grid(row=1, column=0, sticky="ew", pady=(8,0))

    logo = tk.Canvas(header, width=110, height=88, bg=t["bg"], highlightthickness=0)
    logo.pack()
    draw_lungs(logo, t["icon"], t["bg"])

    tk.Label(header, text="PneumoCare", bg=t["bg"], fg=t["text"], font=("Segoe UI",38,"bold")).pack()
    tk.Label(header, text="HOSPITAL VACCINATION MANAGEMENT SYSTEM", bg=t["bg"], fg=t["muted"], font=("Segoe UI",10,"bold")).pack(pady=(5,0))

    welcome = tk.Frame(outer, bg=t["bg"])
    welcome.grid(row=2, column=0, sticky="ew", pady=(17,5))

    tk.Label(welcome, text="Care begins with a breath.", bg=t["bg"], fg=t["text"], font=("Segoe UI",19,"bold")).pack()
    tk.Label(welcome, text="A smarter way to manage pneumococcal vaccination and patient care.", bg=t["bg"], fg=t["muted"], font=("Segoe UI",10)).pack(pady=(5,0))

    portal_area = tk.Frame(outer, bg=t["bg"])
    portal_area.grid(row=3, column=0, sticky="nsew", padx=35, pady=(12,10))
    for col in range(3):
        portal_area.grid_columnconfigure(col, weight=1)
    portal_area.grid_rowconfigure(1, weight=1)

    tk.Label(portal_area, text="SELECT YOUR ACCESS PORTAL", bg=t["bg"], fg=t["muted"], font=("Segoe UI",9,"bold")).grid(row=0,column=0,columnspan=3,pady=(0,12))

    cards = tk.Frame(portal_area, bg=t["bg"])
    cards.grid(row=1,column=0,columnspan=3,sticky="nsew")

    for col in range(3):
        cards.grid_columnconfigure(col, weight=1, uniform="cards")
    cards.grid_rowconfigure(0, weight=1)

    portals = [
        ("Patients", "Your health records, appointments and vaccination history.", "patient"),
        ("Admin", "Manage users, hospital operations and reports.", "admin"),
        ("Staff", "Access patient care and clinical services.", "staff")
    ]

    for col, (name, description, role_name) in enumerate(portals):
        card = tk.Frame(
            cards,
            bg=t["button"],
            highlightbackground=t["border"],
            highlightthickness=1,
            padx=18,
            pady=17,
            cursor="hand2"
        )
        card.grid(row=0,column=col,sticky="nsew",padx=9,pady=4)

        icon_holder = tk.Canvas(card,width=100,height=68,bg=t["button"],highlightthickness=0,cursor="hand2")
        icon_holder.pack(pady=(2,8))
        draw_portal_icon(icon_holder,role_name,t["icon"],t["button"])

        tk.Label(card,text=name,bg=t["button"],fg=t["text"],font=("Segoe UI",17,"bold"),cursor="hand2").pack(pady=(0,7))
        tk.Label(card,text=description,bg=t["button"],fg=t["muted"],font=("Segoe UI",9),wraplength=230,justify="center",cursor="hand2").pack(pady=(0,13))
        tk.Label(card,text="ENTER PORTAL   →",bg=t["button"],fg=t["icon"],font=("Segoe UI",9,"bold"),cursor="hand2").pack()

        def open_selected(event=None, selected=role_name):
            show_portal_login(selected)

        def card_enter(event, selected_card=card):
            selected_card.configure(bg=t["button_hover"],highlightbackground=t["icon"])
            for child in selected_card.winfo_children():
                try:
                    child.configure(bg=t["button_hover"])
                except tk.TclError:
                    pass

        def card_leave(event, selected_card=card):
            selected_card.configure(bg=t["button"],highlightbackground=t["border"])
            for child in selected_card.winfo_children():
                try:
                    child.configure(bg=t["button"])
                except tk.TclError:
                    pass

        for child in card.winfo_children():
            child.bind("<Button-1>",open_selected)
            child.bind("<Enter>",card_enter)
            child.bind("<Leave>",card_leave)

        card.bind("<Button-1>",open_selected)
        card.bind("<Enter>",card_enter)
        card.bind("<Leave>",card_leave)

    signup = tk.Frame(
        outer,
        bg=t["panel"],
        highlightbackground=t["border"],
        highlightthickness=1,
        padx=20,
        pady=10
    )
    signup.grid(row=4,column=0,sticky="ew",pady=(5,0))
    signup.grid_columnconfigure(0,weight=1)
    signup.grid_columnconfigure(1,weight=1)

    tk.Label(signup,text="NEW TO PNEUMOCARE?",bg=t["panel"],fg=t["text"],font=("Segoe UI",10,"bold")).grid(row=0,column=0,columnspan=2,pady=(2,8))

    tk.Button(
        signup,
        text="Patient Registration",
        command=lambda:launch_themed(lambda:show_patient_registration(root,show_login)),
        bg=t["button"],
        fg=t["text"],
        activebackground=t["button_hover"],
        activeforeground=t["text"],
        relief="solid",
        highlightbackground=t["border"],
        highlightthickness=1,
        font=("Segoe UI",9,"bold"),
        cursor="hand2",
        padx=16,
        pady=8
    ).grid(row=1,column=0,padx=12,sticky="ew")

    tk.Button(
        signup,
        text="Staff Registration",
        command=lambda:launch_themed(lambda:show_staff_registration(root,show_login)),
        bg=t["button"],
        fg=t["text"],
        activebackground=t["button_hover"],
        activeforeground=t["text"],
        relief="solid",
        highlightbackground=t["border"],
        highlightthickness=1,
        font=("Segoe UI",9,"bold"),
        cursor="hand2",
        padx=16,
        pady=8
    ).grid(row=1,column=1,padx=12,sticky="ew")

    tk.Label(
        signup,
        text="Staff accounts require administrator approval before login.",
        bg=t["panel"],
        fg=t["muted"],
        font=("Segoe UI",8)
    ).grid(row=2,column=0,columnspan=2,pady=(7,1))


# DASHBOARD DATA
def get_stats():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Patient")
        patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Doctor")
        doctors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Vaccination")
        vaccinations = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Appointment WHERE status='Scheduled'")
        appointments = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Vaccine_Batch WHERE expiry_date >= date('now')")
        batches = cursor.fetchone()[0]
        return patients, doctors, vaccinations, appointments, batches
    finally:
        conn.close()


def get_recent_appointments():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.appointment_id, P.full_name, S.full_name,
                   A.appointment_datetime, A.status
            FROM Appointment A
            JOIN Patient P ON A.patient_id=P.patient_id
            JOIN Doctor D ON A.doctor_id=D.doctor_id
            JOIN Staff S ON D.staff_id=S.staff_id
            ORDER BY A.appointment_datetime DESC
            LIMIT 5
        """)
        return cursor.fetchall()
    finally:
        conn.close()


# OPEN DASHBOARD
def open_dashboard(account):
    for widget in root.winfo_children():
        widget.destroy()

    role = account["role"]
    username = account["username"]
    patient_id = account["patient_id"]
    staff_id = account["staff_id"]

    theme = get_app_theme_colors(CURRENT_THEME)
    root.configure(bg=theme["bg"])

    sidebar = tk.Frame(root,bg=theme["sidebar"],width=230)
    sidebar.pack(side="left",fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar,text="✚  PneumoCare",bg=theme["sidebar"],fg=theme["text"],font=("Segoe UI",19,"bold")).pack(pady=(30,5))
    tk.Label(sidebar,text=role.upper()+" PORTAL",bg=theme["sidebar"],fg=theme["muted"],font=("Segoe UI",9,"bold")).pack(pady=(0,15))
    tk.Label(sidebar,text="Welcome, "+username,bg=theme["sidebar"],fg=theme["text"],font=("Segoe UI",10)).pack(pady=(0,25))

    main_area = tk.Frame(root,bg=theme["bg"])
    main_area.pack(side="left",fill="both",expand=True)

    header = tk.Frame(main_area,bg=theme["panel"],height=75)
    header.pack(fill="x")
    header.pack_propagate(False)

    page_title = tk.Label(header,text="Dashboard",bg=theme["panel"],fg=theme["text"],font=("Segoe UI",21,"bold"))
    page_title.pack(side="left",padx=30,pady=18)

    tk.Label(header,text=date.today().strftime("%d %B %Y"),bg=theme["panel"],fg=theme["muted"],font=("Segoe UI",10)).pack(side="right",padx=20)

    content = tk.Frame(main_area,bg=theme["bg"])
    content.pack(fill="both",expand=True,padx=30,pady=25)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    active_page = {"command": None}

    def refresh_global_theme():
        current = get_app_theme_colors(CURRENT_THEME)
        configure_app_styles(CURRENT_THEME)
        root.configure(bg=current["bg"])
        apply_complete_theme(root, CURRENT_THEME)

        theme_button.config(
            text="☀  Light mode" if CURRENT_THEME == "dark" else "☾  Dark mode",
            bg=current["button"],
            fg=current["text"],
            activebackground=current["button_hover"],
            activeforeground=current["text"],
            highlightbackground=current["border"],
            highlightcolor=current["border"],
            highlightthickness=1,
            bd=1,
            relief="solid"
        )

    def toggle_dashboard_theme():
        global CURRENT_THEME
        CURRENT_THEME = "light" if CURRENT_THEME == "dark" else "dark"
        refresh_global_theme()

    theme_button = tk.Button(
        header,
        text="☀  Light mode" if CURRENT_THEME == "dark" else "☾  Dark mode",
        command=toggle_dashboard_theme,
        bg=theme["button"],
        fg=theme["text"],
        activebackground=theme["button_hover"],
        activeforeground=theme["text"],
        relief="solid",
        highlightbackground=theme["border"],
        highlightthickness=1,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
        padx=13,
        pady=7
    )
    theme_button.pack(side="right", padx=(0, 22))

    # DASHBOARD
    def show_dashboard():
        clear_content()
        page_title.config(text="Dashboard")
        t = get_app_theme_colors(CURRENT_THEME)

        tk.Label(content,text="Welcome to PneumoCare",bg=t["bg"],fg=t["text"],font=("Segoe UI",18,"bold")).pack(anchor="w")
        tk.Label(content,text="Hospital Pneumococcal Vaccination Management System",bg=t["bg"],fg=t["muted"],font=("Segoe UI",10)).pack(anchor="w",pady=(3,20))

        stats = get_stats()
        cards_data = [
            ("Total Patients",stats[0]),
            ("Doctors",stats[1]),
            ("Vaccinations",stats[2]),
            ("Scheduled Appointments",stats[3])
        ]

        card_frame = tk.Frame(content,bg=t["bg"])
        card_frame.pack(fill="x",pady=5)

        for i,(title,value) in enumerate(cards_data):
            card = tk.Frame(
                card_frame,
                bg=t["panel"],
                highlightbackground=t["border"],
                highlightthickness=1
            )
            card.grid(row=0,column=i,sticky="nsew",padx=7,ipadx=8,ipady=15)
            card_frame.columnconfigure(i,weight=1)

            tk.Label(card,text=title,bg=t["panel"],fg=t["muted"],font=("Segoe UI",10)).pack(anchor="w",padx=15,pady=(12,5))
            tk.Label(card,text=str(value),bg=t["panel"],fg=t["text"],font=("Segoe UI",25,"bold")).pack(anchor="w",padx=15,pady=(0,12))

        lower = tk.Frame(content,bg=t["bg"])
        lower.pack(fill="both",expand=True,pady=25)

        appointment_frame = tk.Frame(
            lower,
            bg=t["panel"],
            highlightbackground=t["border"],
            highlightthickness=1
        )
        appointment_frame.pack(fill="both",expand=True)

        tk.Label(appointment_frame,text="Recent Appointments",bg=t["panel"],fg=t["text"],font=("Segoe UI",14,"bold")).pack(anchor="w",padx=20,pady=15)

        columns = ("ID","Patient","Doctor","Date","Status")
        table = ttk.Treeview(appointment_frame,columns=columns,show="headings",height=6)

        for col in columns:
            table.heading(col,text=col)
            table.column(col,anchor="center",width=130)

        table.pack(fill="both",expand=True,padx=15,pady=(0,15))

        for record in get_recent_appointments():
            table.insert("","end",values=record)

        inventory_frame = tk.Frame(
            content,
            bg=t["panel"],
            highlightbackground=t["border"],
            highlightthickness=1
        )
        inventory_frame.pack(fill="x")

        tk.Label(inventory_frame,text="Inventory Overview",bg=t["panel"],fg=t["text"],font=("Segoe UI",12,"bold")).pack(anchor="w",padx=20,pady=(12,5))
        tk.Label(inventory_frame,text=f"Non-expired vaccine batches: {stats[4]}",bg=t["panel"],fg=t["text"],font=("Segoe UI",11)).pack(anchor="w",padx=20,pady=(0,12))

        if role == "admin":
            pending = pending_staff_count()
            tk.Label(
                inventory_frame,
                text=f"Pending staff registration requests: {pending}",
                bg=t["panel"],
                fg=t["text"],
                font=("Segoe UI",10,"bold")
            ).pack(anchor="w",padx=20,pady=(0,12))

    # PATIENT BOOKING
    def open_patient_booking():
        page_title.config(text="Book an Appointment")
        show_patient_booking(content, page_title, clear_content, account)
        apply_complete_theme(root, CURRENT_THEME)

    # PATIENT PORTAL
    def show_patient_portal():
        clear_content()
        page_title.config(text="My Patient Portal")
        t = get_app_theme_colors(CURRENT_THEME)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT patient_id,full_name,dob,gender,phone,email,address,blood_group
                FROM Patient WHERE patient_id=?
            """,(patient_id,))
            patient = cursor.fetchone()

            if not patient:
                tk.Label(content,text="Patient profile not found.",bg=t["bg"],fg=t["text"],font=("Segoe UI",14,"bold")).pack(anchor="w")
                return

            today = date.today()
            try:
                dob = date.fromisoformat(patient[2])
                age = today.year-dob.year-((today.month,today.day)<(dob.month,dob.day))
            except (ValueError,TypeError):
                age = "Not available"

            cursor.execute("""
                SELECT V.vaccine_name,VR.dose_number,VR.date_administered,VR.next_due_date
                FROM Vaccination VR JOIN Vaccine V ON VR.vaccine_id=V.vaccine_id
                WHERE VR.patient_id=? ORDER BY VR.date_administered DESC
            """,(patient_id,))
            vaccination_records = cursor.fetchall()

            cursor.execute("""
                SELECT V.vaccine_name,VR.next_due_date
                FROM Vaccination VR JOIN Vaccine V ON VR.vaccine_id=V.vaccine_id
                WHERE VR.patient_id=? AND VR.next_due_date IS NOT NULL
                AND date(VR.next_due_date)>=date('now')
                ORDER BY date(VR.next_due_date) ASC LIMIT 1
            """,(patient_id,))
            next_due = cursor.fetchone()

            cursor.execute("""
                SELECT A.appointment_id,S.full_name,A.appointment_datetime,A.status,COALESCE(A.notes,'')
                FROM Appointment A
                JOIN Doctor D ON A.doctor_id=D.doctor_id
                JOIN Staff S ON D.staff_id=S.staff_id
                WHERE A.patient_id=? ORDER BY A.appointment_datetime DESC
            """,(patient_id,))
            appointment_records = cursor.fetchall()
        finally:
            conn.close()

        tk.Label(content,text="Welcome, "+patient[1],bg=t["bg"],fg=t["text"],font=("Segoe UI",20,"bold")).pack(anchor="w")
        tk.Label(content,text="Your personal vaccination information",bg=t["bg"],fg=t["muted"],font=("Segoe UI",10)).pack(anchor="w",pady=(3,15))

        booking_bar = tk.Frame(content,bg=t["bg"])
        booking_bar.pack(fill="x",pady=(0,10))

        tk.Button(
            booking_bar,
            text="＋  Book an Appointment",
            command=open_patient_booking,
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_hover"],
            activeforeground=t["text"],
            relief="solid",
            highlightbackground=t["border"],
            highlightthickness=1,
            cursor="hand2",
            font=("Segoe UI",10,"bold"),
            padx=18,
            pady=10
        ).pack(side="left")

        details_frame = tk.Frame(
            content,
            bg=t["panel"],
            highlightbackground=t["border"],
            highlightthickness=1
        )
        details_frame.pack(fill="x",pady=5)

        tk.Label(details_frame,text="My Personal Details",bg=t["panel"],fg=t["text"],font=("Segoe UI",14,"bold")).pack(anchor="w",padx=20,pady=12)

        details = [
            ("Patient ID",patient[0]),("Full Name",patient[1]),("Date of Birth",patient[2]),
            ("Age",age),("Gender",patient[3]),("Phone",patient[4]),
            ("Email",patient[5]),("Address",patient[6]),("Blood Group",patient[7])
        ]

        detail_grid = tk.Frame(details_frame,bg=t["panel"])
        detail_grid.pack(fill="x",padx=20,pady=(0,15))

        for i,(label,value) in enumerate(details):
            row = i//3
            col = i%3
            tk.Label(detail_grid,text=label,bg=t["panel"],fg=t["muted"],font=("Segoe UI",9)).grid(row=row*2,column=col,sticky="w",padx=10,pady=(8,2))
            tk.Label(detail_grid,text=str(value or "Not provided"),bg=t["panel"],fg=t["text"],font=("Segoe UI",10,"bold")).grid(row=row*2+1,column=col,sticky="w",padx=10)

        for col in range(3):
            detail_grid.columnconfigure(col,weight=1)

        due_frame = tk.Frame(
            content,
            bg=t["panel"],
            highlightbackground=t["border"],
            highlightthickness=1
        )
        due_frame.pack(fill="x",pady=12)

        tk.Label(due_frame,text="Next Vaccination",bg=t["panel"],fg=t["text"],font=("Segoe UI",13,"bold")).pack(anchor="w",padx=20,pady=(12,5))

        if next_due:
            due_text = f"{next_due[0]}  |  Due date: {next_due[1]}"
        else:
            due_text = "No upcoming vaccination due date recorded."

        tk.Label(due_frame,text=due_text,bg=t["panel"],fg=t["text"],font=("Segoe UI",11,"bold")).pack(anchor="w",padx=20,pady=(0,12))

        tk.Label(content,text="My Appointments",bg=t["bg"],fg=t["text"],font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(12,5))

        appointment_columns = ("Appointment ID","Doctor","Date & Time","Status","Notes")
        appointment_table = ttk.Treeview(content,columns=appointment_columns,show="headings",height=4)

        for col in appointment_columns:
            appointment_table.heading(col,text=col)
            appointment_table.column(col,anchor="center",width=150)

        appointment_table.pack(fill="x",pady=5)

        for record in appointment_records:
            appointment_table.insert("","end",values=record)

        if not appointment_records:
            tk.Label(content,text="No appointments have been scheduled for you yet.",bg=t["bg"],fg=t["muted"],font=("Segoe UI",10)).pack(anchor="w",pady=5)

        tk.Label(content,text="My Vaccination History",bg=t["bg"],fg=t["text"],font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(10,5))

        columns = ("Vaccine","Dose Number","Date Administered","Next Due Date")
        table = ttk.Treeview(content,columns=columns,show="headings",height=6)

        for col in columns:
            table.heading(col,text=col)
            table.column(col,anchor="center",width=180)

        table.pack(fill="both",expand=True,pady=5)

        for record in vaccination_records:
            table.insert("","end",values=record)

        if not vaccination_records:
            tk.Label(content,text="No vaccination records are available yet.",bg=t["bg"],fg=t["muted"],font=("Segoe UI",10)).pack(anchor="w",pady=5)

    # NAVIGATION
    def create_nav_button(name,command):
        current = get_app_theme_colors(CURRENT_THEME)

        def open_page():
            command()
            apply_complete_theme(root, CURRENT_THEME)

        btn = tk.Button(
            sidebar,
            text="   " + name,
            command=open_page,
            bg=current["sidebar"],
            fg=current["text"],
            activebackground=current["sidebar_hover"],
            activeforeground=current["text"],
            relief="solid",
            highlightbackground=current["border"],
            highlightthickness=1,
            bd=1,
            anchor="w",
            font=("Segoe UI",11),
            cursor="hand2",
            padx=15,
            pady=13
        )
        btn.pack(fill="x",padx=10,pady=2)

    # ADMIN MENU
    if role == "admin":
        pending_requests = pending_staff_count()
        staff_request_label = f"Staff Requests ({pending_requests})" if pending_requests > 0 else "Staff Requests"

        menu_items = [
            ("Dashboard",show_dashboard),
            ("Patients",lambda:show_patients(content,page_title,clear_content)),
            ("Doctors & Staff",lambda:show_staff(content,page_title,clear_content)),
            ("Vaccine Inventory",lambda:show_inventory(content,page_title,clear_content)),
            (staff_request_label,lambda:show_staff_requests(content,page_title,clear_content,account)),
            ("Eligibility",lambda:show_eligibility(content,page_title,clear_content,account)),
            ("Appointments",lambda:show_appointments(content,page_title,clear_content,account)),
            ("Vaccinations",lambda:show_vaccinations(content,page_title,clear_content,account)),
            ("Reports",lambda:show_reports(content,page_title,clear_content,account))
        ]

    # STAFF MENU
    elif role == "staff":
        menu_items = [
            ("Dashboard",show_dashboard),
            ("Patients",lambda:show_patients(content,page_title,clear_content)),
            ("Vaccine Inventory",lambda:show_inventory(content,page_title,clear_content)),
            ("Eligibility",lambda:show_eligibility(content,page_title,clear_content,account)),
            ("Appointments",lambda:show_appointments(content,page_title,clear_content,account)),
            ("Vaccinations",lambda:show_vaccinations(content,page_title,clear_content,account))
        ]

    # PATIENT MENU
    else:
        menu_items = [
            ("My Dashboard",show_patient_portal),
            ("Book Appointment",open_patient_booking)
        ]

    for name,command in menu_items:
        create_nav_button(name,command)

    def logout():
        confirm = messagebox.askyesno("Logout","Are you sure you want to logout?")
        if confirm:
            show_login()

    current = get_app_theme_colors(CURRENT_THEME)

    tk.Button(
        sidebar,
        text="   Logout",
        command=logout,
        bg=current["sidebar"],
        fg=current["text"],
        activebackground=current["sidebar_hover"],
        activeforeground=current["text"],
        relief="solid",
        highlightbackground=current["border"],
        highlightthickness=1,
        bd=1,
        anchor="w",
        font=("Segoe UI",11,"bold"),
        cursor="hand2",
        padx=15,
        pady=12
    ).pack(side="bottom",fill="x",padx=10,pady=15)

    tk.Label(
        sidebar,
        text="PneumoCare v1.0\nDBMS 2026 Project",
        bg=current["sidebar"],
        fg=current["muted"],
        font=("Segoe UI",9),
        justify="center"
    ).pack(side="bottom",pady=10)

    if role == "patient":
        show_patient_portal()
    else:
        show_dashboard()

    apply_complete_theme(root, CURRENT_THEME)


# START APPLICATION
show_login()
root.mainloop()
