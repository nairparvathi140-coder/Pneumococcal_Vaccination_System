
"""Central theme manager for the PneumoCare application."""
import tkinter as tk
from tkinter import ttk

THEMES = {
    "dark": {
        "bg": "#000000",
        "panel": "#000000",
        "sidebar": "#000000",
        "sidebar_hover": "#10313A",
        "text": "#00E5FF",
        "muted": "#80DDE8",
        "border": "#00E5FF",
        "blue": "#00E5FF",
        "green": "#00E5FF",
        "red": "#00E5FF",
        "danger": "#000000",
        "danger_hover": "#10313A",
        "input": "#000000",
        "selected": "#10313A",
        "table_heading": "#000000",
        "button": "#000000",
        "button_hover": "#10313A",
        "soft": "#000000"
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#FFFFFF",
        "sidebar": "#FFFFFF",
        "sidebar_hover": "#EAF2FA",
        "text": "#17345B",
        "muted": "#52657D",
        "border": "#17345B",
        "blue": "#17345B",
        "green": "#17345B",
        "red": "#17345B",
        "danger": "#FFFFFF",
        "danger_hover": "#EAF2FA",
        "input": "#FFFFFF",
        "selected": "#DCEBFA",
        "table_heading": "#FFFFFF",
        "button": "#FFFFFF",
        "button_hover": "#EAF2FA",
        "soft": "#FFFFFF"
    }
}

# Original colours used by older modules.
LEGACY = {
    "#F3F6FB": "bg",
    "#EAF1F7": "bg",
    "#EAF4FA": "soft",
    "#FFFFFF": "panel",
    "#FFF": "panel",
    "#172B4D": "text",
    "#243247": "text",
    "#17324A": "text",
    "#718096": "muted",
    "#61798D": "muted",
    "#A9BBD3": "muted",
    "#8FA4BF": "muted",
    "#E3EAF3": "border",
    "#D5E2EC": "border",
    "#EAF0F8": "table_heading",
    "#DCEBFA": "selected",
    "#2878D0": "blue",
    "#087EBD": "blue",
    "#159D79": "green",
    "#D9534F": "red",
    "#243B60": "sidebar_hover",
    "#A93232": "danger",
    "#812727": "danger_hover"
}


def get_theme_colors(theme_name="light"):
    """Return the selected application palette."""
    return THEMES.get(theme_name, THEMES["light"])


def configure_theme_styles(style=None, theme_name="light"):
    """Apply the selected palette to ttk widgets."""
    if style is None:
        style = ttk.Style()

    t = get_theme_colors(theme_name)
    style.theme_use("clam")

    style.configure(
        ".",
        background=t["bg"],
        foreground=t["text"],
        fieldbackground=t["input"],
        font=("Segoe UI", 10)
    )

    style.configure(
        "TFrame",
        background=t["bg"]
    )

    style.configure(
        "TLabelframe",
        background=t["bg"],
        bordercolor=t["border"],
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=t["bg"],
        foreground=t["text"],
        font=("Segoe UI", 10, "bold")
    )

    style.configure(
        "TLabel",
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

    style.map(
        "TEntry",
        fieldbackground=[("disabled", t["input"])],
        foreground=[("disabled", t["muted"])]
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
        fieldbackground=[
            ("readonly", t["input"]),
            ("disabled", t["input"])
        ],
        foreground=[
            ("readonly", t["text"]),
            ("disabled", t["muted"])
        ],
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
        padding=(12, 7),
        relief="solid",
        borderwidth=1,
        font=("Segoe UI", 9, "bold")
    )

    style.map(
        "TButton",
        background=[
            ("pressed", t["selected"]),
            ("active", t["button_hover"])
        ],
        foreground=[
            ("disabled", t["muted"]),
            ("active", t["text"])
        ]
    )

    style.configure(
        "TNotebook",
        background=t["bg"],
        bordercolor=t["border"],
        tabmargins=(2, 5, 2, 0)
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


def apply_theme(widget, theme_name="light"):
    """Apply the selected theme recursively to an existing Tk widget tree."""
    t = get_theme_colors(theme_name)

    bg = t["bg"]
    fg = t["text"]
    border = t["border"]

    configure_theme_styles(theme_name=theme_name)

    try:
        if isinstance(widget, (tk.Tk, tk.Toplevel)):
            widget.configure(bg=bg)

        elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.configure(
                bg=bg,
                highlightbackground=border,
                highlightcolor=border,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

        elif isinstance(widget, tk.Canvas):
            widget.configure(
                bg=bg,
                highlightbackground=border,
                highlightcolor=border
            )

        elif isinstance(widget, (tk.Label, tk.Message)):
            widget.configure(
                bg=bg,
                fg=fg
            )

        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=bg,
                fg=fg,
                activebackground=t["button_hover"],
                activeforeground=fg,
                disabledforeground=t["muted"],
                highlightbackground=border,
                highlightcolor=border,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

        elif isinstance(widget, (tk.Entry, tk.Spinbox)):
            widget.configure(
                bg=t["input"],
                fg=fg,
                insertbackground=fg,
                selectbackground=t["selected"],
                selectforeground=fg,
                highlightbackground=border,
                highlightcolor=border,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=t["input"],
                fg=fg,
                insertbackground=fg,
                selectbackground=t["selected"],
                selectforeground=fg,
                highlightbackground=border,
                highlightcolor=border,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

        elif isinstance(widget, (tk.Checkbutton, tk.Radiobutton)):
            widget.configure(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=t["panel"]
            )

        elif isinstance(widget, tk.Listbox):
            widget.configure(
                bg=t["input"],
                fg=fg,
                selectbackground=t["selected"],
                selectforeground=fg,
                highlightbackground=border,
                highlightcolor=border,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

        elif isinstance(widget, tk.Menubutton):
            widget.configure(
                bg=t["button"],
                fg=fg,
                activebackground=t["button_hover"],
                activeforeground=fg
            )

    except (tk.TclError, TypeError):
        pass

    # Recolour every nested widget as well.
    try:
        children = widget.winfo_children()
    except tk.TclError:
        children = []

    for child in children:
        apply_theme(child, theme_name)
