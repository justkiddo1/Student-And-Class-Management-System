import tkinter as tk
from tkinter import messagebox
from views.theme import *
from views.widgets import PlaceholderEntry, AppButton


class LoginView(tk.Toplevel):

    def __init__(self, nguoi_dung_service, on_success):
        super().__init__()
        self._svc = nguoi_dung_service
        self._on_success = on_success

        self.title("Đăng nhập — Hệ thống Quản lý Lớp học")
        self.resizable(False, False)
        self.configure(bg=BG_APP)

        w, h = 440, 520
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.grab_set()   # Modal
        self._build_ui()
        self.bind("<Return>", lambda e: self._dang_nhap())

    def _build_ui(self):
        banner = tk.Frame(self, bg=BG_SIDEBAR, height=160)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(banner, text="🎓", font=("Segoe UI Emoji", 36),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(pady=(28, 4))
        tk.Label(banner, text="Hệ thống Quản lý Lớp học",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack()
        tk.Label(banner, text="Student Management System",
                 font=FONT_SMALL, bg=BG_SIDEBAR, fg="#90CAF9").pack()

        form = tk.Frame(self, bg=BG_APP, padx=40)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Đăng nhập tài khoản", font=FONT_HEADING,
                 fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w", pady=(24, 2))
        tk.Label(form, text="Nhập thông tin để tiếp tục", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(anchor="w", pady=(0, 20))

        self._build_field(form, "Tên đăng nhập", "Nhập tên đăng nhập...", "user")
        self.ent_user = self._last_entry
        tk.Frame(form, height=10, bg=BG_APP).pack()

        self._build_field(form, "Mật khẩu", "Nhập mật khẩu...", "lock", show="•")
        self.ent_pass = self._last_entry
        tk.Frame(form, height=20, bg=BG_APP).pack()

        AppButton(form, text="Đăng nhập", style="primary",
                  command=self._dang_nhap).pack(fill="x", ipady=4)

        self.lbl_err = tk.Label(form, text="", font=FONT_SMALL,
                                fg=DANGER, bg=BG_APP, wraplength=360)
        self.lbl_err.pack(pady=(8, 0))

        tk.Label(form, text="Mặc định: admin / admin123",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP).pack(pady=(16, 0))

    def _build_field(self, parent, label, placeholder, icon, show=""):
        row = tk.Frame(parent, bg=BG_APP)
        row.pack(fill="x")
        tk.Label(row, text=label, font=FONT_SMALL, fg=TEXT_MUTED,
                 bg=BG_APP).pack(anchor="w")

        border = tk.Frame(row, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x", pady=(3, 0))
        inner = tk.Frame(border, bg=BG_CARD)
        inner.pack(fill="x")

        tk.Label(inner, text={"user": "👤", "lock": "🔒"}.get(icon, ""),
                 font=("Segoe UI Emoji", 11),
                 bg=BG_CARD, padx=8).pack(side="left")

        entry = PlaceholderEntry(inner, placeholder=placeholder,
                                 show_char=show, bg=BG_CARD)
        entry.pack(side="left", fill="x", expand=True, pady=8, padx=(0, 8))
        entry.bind("<FocusIn>",  lambda e: border.config(bg=PRIMARY))
        entry.bind("<FocusOut>", lambda e: border.config(bg=BORDER))

        self._last_entry = entry

    def _dang_nhap(self):
        ten = self.ent_user.get_value().strip()
        mk  = self.ent_pass.get_value()

        if not ten or not mk:
            self.lbl_err.config(text="Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        ok, msg = self._svc.dang_nhap(ten, mk)
        if ok:
            self.destroy()
            self._on_success()
        else:
            self.lbl_err.config(text=msg)
            self.ent_pass.delete(0, tk.END)
            self.ent_pass._set_placeholder()