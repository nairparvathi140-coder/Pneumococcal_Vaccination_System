
import tkinter as tk
from tkinter import ttk, messagebox
from modules.auth import (
    reset_password_by_contact,
    reset_admin_password,
    set_admin_recovery_key,
    ensure_recovery_table
)

def show_forgot_password(parent):
    if not ensure_recovery_table():
        messagebox.showerror(
            "Database Error",
            "The password recovery system could not be initialized.",
            parent=parent
        )
        return

    window = tk.Toplevel(parent)
    window.title("PneumoCare | Password Recovery")
    window.geometry("650x780")
    window.minsize(580, 680)
    window.configure(bg="#F2F6FC")
    window.transient(parent)
    window.grab_set()

    NAVY = "#172B4D"
    BLUE = "#2878D0"
    BLUE_DARK = "#1D5FA8"
    WHITE = "#FFFFFF"
    MUTED = "#718096"
    LIGHT = "#EAF1FA"
    BORDER = "#DFE7F1"
    BG = "#F2F6FC"

    selected_role = tk.StringVar(value="Patient")
    username_var = tk.StringVar()
    email_var = tk.StringVar()
    phone_var = tk.StringVar()
    recovery_key_var = tk.StringVar()
    new_password_var = tk.StringVar()
    confirm_password_var = tk.StringVar()
    current_password_var = tk.StringVar()
    new_recovery_key_var = tk.StringVar()
    confirm_recovery_key_var = tk.StringVar()
    setup_mode = tk.BooleanVar(value=False)

    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Recovery.TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=NAVY,
        padding=9,
        bordercolor=BORDER
    )
    style.map(
        "Recovery.TCombobox",
        fieldbackground=[("readonly", WHITE)],
        selectbackground=[("readonly", WHITE)],
        selectforeground=[("readonly", NAVY)]
    )
    style.configure(
        "Recovery.TEntry",
        fieldbackground=WHITE,
        foreground=NAVY,
        padding=10,
        bordercolor=BORDER
    )

    outer = tk.Frame(window, bg=BG)
    outer.pack(fill="both", expand=True, padx=22, pady=22)

    header = tk.Frame(outer, bg=BG)
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
        text="Account Recovery",
        bg=BG,
        fg=NAVY,
        font=("Segoe UI", 23, "bold")
    ).pack(pady=(7, 3))

    tk.Label(
        header,
        text="Securely recover access to your account",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack()

    card = tk.Frame(
        outer,
        bg=WHITE,
        padx=34,
        pady=26,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True)

    tk.Label(
        card,
        text="Select Account Type",
        bg=WHITE,
        fg=NAVY,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(0, 7))

    role_dropdown = ttk.Combobox(
        card,
        textvariable=selected_role,
        values=["Patient", "Staff", "Admin"],
        state="readonly",
        style="Recovery.TCombobox",
        font=("Segoe UI", 10)
    )
    role_dropdown.pack(fill="x", pady=(0, 20))

    form = tk.Frame(card, bg=WHITE)
    form.pack(fill="both", expand=True)

    fields = {}

    def clear_fields():
        for widget in form.winfo_children():
            widget.destroy()
        fields.clear()

    def add_field(label, variable, show=None):
        tk.Label(
            form,
            text=label,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(10, 5))

        entry = ttk.Entry(
            form,
            textvariable=variable,
            show=show,
            style="Recovery.TEntry",
            font=("Segoe UI", 10)
        )
        entry.pack(fill="x", ipady=2)
        fields[label] = entry
        return entry

    def add_button(text, command, primary=True):
        if primary:
            bg = BLUE
            fg = WHITE
            active_bg = BLUE_DARK
        else:
            bg = LIGHT
            fg = BLUE
            active_bg = "#DCE8F7"

        button = tk.Button(
            form,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            pady=11,
            cursor="hand2"
        )
        button.pack(fill="x", pady=(10, 0))
        return button

    def validate_password():
        password = new_password_var.get()
        confirm = confirm_password_var.get()

        if not password or not confirm:
            messagebox.showerror(
                "Missing Information",
                "Enter and confirm your new password.",
                parent=window
            )
            return False

        if len(password) < 8:
            messagebox.showerror(
                "Weak Password",
                "Your password must contain at least 8 characters.",
                parent=window
            )
            return False

        if password != confirm:
            messagebox.showerror(
                "Password Error",
                "The passwords do not match.",
                parent=window
            )
            return False

        return True

    def reset_patient_or_staff():
        username = username_var.get().strip()
        email = email_var.get().strip()
        phone = phone_var.get().strip()

        if not username or not email or not phone:
            messagebox.showerror(
                "Missing Information",
                "Complete all account verification fields.",
                parent=window
            )
            return

        if not validate_password():
            return

        role = selected_role.get().lower()

        success, message = reset_password_by_contact(
            username,
            role,
            email,
            phone,
            new_password_var.get()
        )

        if success:
            messagebox.showinfo(
                "Password Reset",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Recovery Failed",
                message,
                parent=window
            )

    def reset_admin():
        username = username_var.get().strip()
        recovery_key = recovery_key_var.get()

        if not username or not recovery_key:
            messagebox.showerror(
                "Missing Information",
                "Enter your administrator username and recovery key.",
                parent=window
            )
            return

        if not validate_password():
            return

        success, message = reset_admin_password(
            username,
            recovery_key,
            new_password_var.get()
        )

        if success:
            messagebox.showinfo(
                "Password Reset",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Recovery Failed",
                message,
                parent=window
            )

    def setup_admin_key():
        username = username_var.get().strip()
        current_password = current_password_var.get()
        recovery_key = new_recovery_key_var.get()
        confirm_key = confirm_recovery_key_var.get()

        if not all([username, current_password, recovery_key, confirm_key]):
            messagebox.showerror(
                "Missing Information",
                "Complete all recovery key setup fields.",
                parent=window
            )
            return

        if len(recovery_key) < 12:
            messagebox.showerror(
                "Weak Recovery Key",
                "Your recovery key must contain at least 12 characters.",
                parent=window
            )
            return

        if recovery_key != confirm_key:
            messagebox.showerror(
                "Recovery Key Error",
                "The recovery keys do not match.",
                parent=window
            )
            return

        success, message = set_admin_recovery_key(
            username,
            current_password,
            recovery_key
        )

        if success:
            messagebox.showinfo(
                "Recovery Key Saved",
                message + "\n\nKeep this key somewhere safe. You will need it if you forget your administrator password.",
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Setup Failed",
                message,
                parent=window
            )

    def change_mode(value):
        setup_mode.set(value)
        render()

    def render():
        clear_fields()

        role = selected_role.get()
        is_admin_setup = role == "Admin" and setup_mode.get()

        if is_admin_setup:
            heading = "Set Administrator Recovery Key"
            description = "Create a recovery key while you still have access to your account."
        elif role == "Admin":
            heading = "Reset Administrator Password"
            description = "Verify your recovery key to reset your password."
        else:
            heading = "Reset Your Password"
            description = "Verify your registered contact details to continue."

        tk.Label(
            form,
            text=heading,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            form,
            text=description,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=510,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        if role == "Admin":
            add_field("Administrator Username", username_var)

            if setup_mode.get():
                add_field(
                    "Current Administrator Password",
                    current_password_var,
                    "*"
                )
                add_field(
                    "New Recovery Key (minimum 12 characters)",
                    new_recovery_key_var,
                    "*"
                )
                add_field(
                    "Confirm Recovery Key",
                    confirm_recovery_key_var,
                    "*"
                )

                add_button(
                    "Save Recovery Key",
                    setup_admin_key
                )
                add_button(
                    "Back to Password Reset",
                    lambda: change_mode(False),
                    primary=False
                )
            else:
                add_field(
                    "Administrator Recovery Key",
                    recovery_key_var,
                    "*"
                )
                add_field(
                    "New Password",
                    new_password_var,
                    "*"
                )
                add_field(
                    "Confirm New Password",
                    confirm_password_var,
                    "*"
                )

                add_button(
                    "Reset Administrator Password",
                    reset_admin
                )
                add_button(
                    "Set Up / Change Recovery Key",
                    lambda: change_mode(True),
                    primary=False
                )
        else:
            add_field("Username", username_var)
            add_field("Registered Email", email_var)
            add_field("Registered Phone Number", phone_var)
            add_field("New Password", new_password_var, "*")
            add_field("Confirm New Password", confirm_password_var, "*")

            add_button(
                "Reset Password",
                reset_patient_or_staff
            )

        add_button(
            "Close",
            window.destroy,
            primary=False
        )

    def on_role_change(event=None):
        setup_mode.set(False)
        render()

    role_dropdown.bind(
        "<<ComboboxSelected>>",
        on_role_change
    )

    render()
