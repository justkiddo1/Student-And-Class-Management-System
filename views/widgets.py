import tkinter as tk
from tkinter import ttk
from views.theme import *


class AppButton(tk.Button):
    STYLES = {
        "primary": {"bg": PRIMARY, "fg": TEXT_WHITE, "hover": PRIMARY_DARK},
        "success": {"bg": SUCCESS, "fg": TEXT_WHITE, "hover": "#1B5E20"},
        "danger":  {"bg": DANGER,  "fg": TEXT_WHITE, "hover": "#7F0000"},
        "outline": {"bg": BG_CARD, "fg": PRIMARY,    "hover": PRIMARY_LITE},
        "ghost":   {"bg": BG_APP,  "fg": TEXT_MUTED, "hover": BORDER},
    }

    def __init__(self, parent, text="", style="primary", icon="", width=None, command=None, **kwargs):
        s = self.STYLES.get(style, self.STYLES["primary"])
        label = f"{icon} {text}".strip() if icon else text
        cfg = dict(
            text=label, bg=s["bg"], fg=s["fg"],
            font=FONT_BOLD, relief="flat", cursor="hand2",
            padx=14, pady=6, bd=0,
            activebackground=s["hover"], activeforeground=s["fg"],
        )
        if width:   cfg["width"] = width
        if command: cfg["command"] = command
        cfg.update(kwargs)
        super().__init__(parent, **cfg)
        self._hover_bg  = s["hover"]
        self._normal_bg = s["bg"]
        self.bind("<Enter>", lambda e: self.config(bg=self._hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self._normal_bg))


class TitleLabel(tk.Label):
    def __init__(self, parent, text, **kw):
        super().__init__(parent, text=text, font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP, **kw)

class HeadingLabel(tk.Label):
    def __init__(self, parent, text, bg=BG_APP, **kw):
        super().__init__(parent, text=text, font=FONT_HEADING, fg=TEXT_MAIN, bg=bg, **kw)

class MutedLabel(tk.Label):
    def __init__(self, parent, text, bg=BG_APP, **kw):
        super().__init__(parent, text=text, font=FONT_SMALL, fg=TEXT_MUTED, bg=bg, **kw)


class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder="", show_char="", **kwargs):
        super().__init__(parent, font=FONT_NORMAL, relief="flat", bd=0, **kwargs)

        self._placeholder = placeholder
        self._show_char = show_char
        self._is_placeholder_active = True

        self._setup_placeholder()

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyPress>", self._on_key_press)

    def _setup_placeholder(self):
        self.config(fg=TEXT_MUTED, show="")
        self.delete(0, tk.END)
        self.insert(0, self._placeholder)
        self._is_placeholder_active = True

    def _on_focus_in(self, event=None):
        if self._is_placeholder_active:
            self.delete(0, tk.END)
            self.config(fg=TEXT_MAIN, show=self._show_char)
            self._is_placeholder_active = False

    def _on_focus_out(self, event=None):
        if not self.get().strip():
            self._setup_placeholder()

    def _on_key_press(self, event=None):
        if self._is_placeholder_active:
            self.delete(0, tk.END)
            self.config(fg=TEXT_MAIN, show=self._show_char)
            self._is_placeholder_active = False

    def get_value(self):
        if self._is_placeholder_active:
            return ""
        return self.get().strip()

    def set_value(self, value: str):
        self.delete(0, tk.END)
        if value:
            self.config(fg=TEXT_MAIN, show=self._show_char if self._show_char else "")
            self.insert(0, value)
            self._is_placeholder_active = False
        else:
            self._setup_placeholder()

    def clear(self):
        self.delete(0, tk.END)
        self._setup_placeholder()


# ── Card ─────────────────────────────────────────────────────────────────────
class Card(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG_CARD)
        kw.setdefault("padx", PAD)
        kw.setdefault("pady", PAD)
        super().__init__(parent, relief="flat", bd=1,
                         highlightbackground=BORDER, highlightthickness=1, **kw)


# ── DataTable ────────────────────────────────────────────────────────────────
class DataTable(ttk.Treeview):
    def __init__(self, parent, columns: list, height=15, selectmode="browse", **kw):
        """
        columns: list of (id, header, width, anchor)
        selectmode: "browse" (single) hoặc "extended" (multi)
        """
        col_ids = [c[0] for c in columns]
        super().__init__(parent, columns=col_ids, show="headings",
                         height=height, selectmode=selectmode, **kw)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG_CARD, foreground=TEXT_MAIN,
                        rowheight=30, fieldbackground=BG_CARD,
                        font=FONT_NORMAL, borderwidth=0)
        style.configure("Treeview.Heading",
                        background=PRIMARY, foreground=TEXT_WHITE,
                        font=FONT_BOLD, relief="flat", padding=6)
        style.map("Treeview",
                  background=[("selected", PRIMARY)],
                  foreground=[("selected", TEXT_WHITE)])
        style.map("Treeview.Heading",
                  background=[("active", PRIMARY_DARK)])

        for col_id, header, width, anchor in columns:
            self.heading(col_id, text=header)
            self.column(col_id, width=width, anchor=anchor, minwidth=60)

        self.tag_configure("odd",  background=BG_CARD)
        self.tag_configure("even", background=BG_TABLE_ODD)

    def xoa_tat_ca(self):
        for item in self.get_children():
            self.delete(item)

    def chen_hang(self, values: list):
        tag = "even" if len(self.get_children()) % 2 == 0 else "odd"
        self.insert("", tk.END, values=values, tags=(tag,))

    def lay_hang_chon(self) -> tuple | None:
        sel = self.selection()
        return self.item(sel[0], "values") if sel else None

    @staticmethod
    def them_scrollbar(parent, table):
        sb = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=sb.set)
        return sb


# ── SearchBar ────────────────────────────────────────────────────────────────
class SearchBar(tk.Frame):
    def __init__(self, parent, placeholder="Tìm kiếm...", on_search=None, **kw):
        kw.setdefault("bg", BG_APP)
        super().__init__(parent, **kw)

        border = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x")
        inner = tk.Frame(border, bg=BG_CARD)
        inner.pack(fill="x")

        tk.Label(inner, text=ICON["search"], bg=BG_CARD,
                 fg=TEXT_MUTED, font=FONT_NORMAL, padx=6).pack(side="left")

        self.entry = PlaceholderEntry(inner, placeholder=placeholder, bg=BG_CARD)
        self.entry.pack(side="left", fill="x", expand=True, pady=6)

        if on_search:
            self.entry.bind("<KeyRelease>", lambda e: on_search(self.get()))
            self.entry.bind("<Return>",     lambda e: on_search(self.get()))

    def get(self):
        return self.entry.get_value()


# ── StatusBar ────────────────────────────────────────────────────────────────
class StatusBar(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", BG_SIDEBAR)
        super().__init__(parent, height=28, **kw)
        self.pack_propagate(False)
        self._label = tk.Label(self, text="", font=FONT_SMALL,
                               bg=BG_SIDEBAR, fg="#90CAF9", padx=10)
        self._label.pack(side="left", fill="y")

    def set(self, msg: str, color: str = "#90CAF9"):
        self._label.config(text=msg, fg=color)
        self.after(4000, lambda: self._label.config(text=""))

    def ok(self,   msg): self.set(f"✓ {msg}", "#A5D6A7")
    def err(self,  msg): self.set(f"✕ {msg}", "#EF9A9A")
    def info(self, msg): self.set(f"ℹ {msg}", "#90CAF9")


# ── FormField ────────────────────────────────────────────────────────────────
class FormField(tk.Frame):
    def __init__(self, parent, label, placeholder="",
                 required=False, show="", **kw):
        kw.setdefault("bg", BG_CARD)
        super().__init__(parent, **kw)

        tk.Label(self, text=label + (" *" if required else ""),
                 font=FONT_SMALL, fg=TEXT_MUTED,
                 bg=BG_CARD, anchor="w").pack(fill="x")

        self._border = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        self._border.pack(fill="x", pady=(2, 0))
        inner = tk.Frame(self._border, bg=BG_CARD)
        inner.pack(fill="x")

        self.entry = PlaceholderEntry(inner, placeholder=placeholder,
                                      show_char=show, bg=BG_CARD)
        self.entry.pack(fill="x", padx=6, pady=5)

        self.entry.bind("<FocusIn>",  lambda e: self._border.config(bg=PRIMARY))
        self.entry.bind("<FocusOut>", lambda e: self._border.config(bg=BORDER))

    def get(self) -> str:
        return self.entry.get_value()

    def set(self, v: str):
        self.entry.set_value(v)

    def clear(self):
        self.entry.clear()
        self._border.config(bg=BORDER)

    def enable(self):
        self.entry.config(state="normal")

    def disable(self):
        self.entry.config(state="disabled")