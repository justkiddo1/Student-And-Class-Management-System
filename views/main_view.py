# views/main_view.py
import tkinter as tk
from tkinter import messagebox
from views.theme import *
from views.widgets import StatusBar


class MainView(tk.Tk):
    def __init__(self, services: dict):
        super().__init__()
        self._svcs = services          # {"sv": ..., "lop": ..., "diem": ..., "nd": ...}
        self._nd_svc = services["nd"]

        self.title("Hệ thống Quản lý Lớp học & Sinh viên")
        self.configure(bg=BG_APP)
        self.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.minsize(WIN_MIN_W, WIN_MIN_H)

        self._active_tab = tk.StringVar(value="dashboard")
        self._frame_hien_tai = None

        self._build_ui()
        self._hien_thi_tab("dashboard")

    def _build_ui(self):
        # ── Topbar ───────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=BG_SIDEBAR, height=TOPBAR_H)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🎓 SMS", font=(FONT_FAMILY, 15, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE, padx=16).pack(side="left", fill="y")

        # Thông tin người dùng
        nd = self._nd_svc.nguoi_dung_hien_tai
        tk.Label(topbar, text=f"👤  {nd.ho_ten}  |  {nd.vai_tro.upper()}",
                 font=FONT_SMALL, bg=BG_SIDEBAR, fg="#90CAF9",
                 padx=16).pack(side="right", fill="y")

        # ── Body ─────────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG_APP)
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        self._sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Content
        self._content = tk.Frame(body, bg=BG_APP)
        self._content.pack(side="left", fill="both", expand=True)

        # ── Statusbar ────────────────────────────────────────────────
        self.statusbar = StatusBar(self)
        self.statusbar.pack(side="bottom", fill="x")

    def _build_sidebar(self):
        nd = self._nd_svc.nguoi_dung_hien_tai

        menu_items = [
            ("dashboard", ICON["dashboard"], "Dashboard"),
            ("sinh_vien", ICON["student"],   "Sinh viên"),
            ("lop_hoc",   ICON["class"],     "Lớp học"),
            ("diem_so",   ICON["grade"],     "Điểm số"),
        ]
        if nd and nd.la_admin:
            menu_items.append(("nguoi_dung", ICON["user"], "Tài khoản"))

        tk.Frame(self._sidebar, height=16, bg=BG_SIDEBAR).pack()

        self._sidebar_btns = {}
        for tab_id, icon, label in menu_items:
            btn = self._make_sidebar_btn(tab_id, icon, label)
            self._sidebar_btns[tab_id] = btn

        # Nút đăng xuất
        tk.Frame(self._sidebar, bg=BG_SIDEBAR).pack(expand=True)
        self._make_sidebar_btn("_logout", ICON["logout"], "Đăng xuất",
                               is_logout=True)

    def _make_sidebar_btn(self, tab_id, icon, label, is_logout=False):
        bg_normal = BG_SIDEBAR
        bg_hover  = "#283593"
        bg_active = PRIMARY

        frame = tk.Frame(self._sidebar, bg=bg_normal, cursor="hand2")
        frame.pack(fill="x", pady=1)

        lbl = tk.Label(frame,
                       text=f"  {icon}  {label}",
                       font=FONT_NORMAL, bg=bg_normal,
                       fg="#B0BEC5", anchor="w", padx=8, pady=10)
        lbl.pack(fill="x")

        def enter(_):
            if self._active_tab.get() != tab_id:
                frame.config(bg=bg_hover); lbl.config(bg=bg_hover)
        def leave(_):
            if self._active_tab.get() != tab_id:
                frame.config(bg=bg_normal); lbl.config(bg=bg_normal)
        def click(_):
            if is_logout:
                self._dang_xuat()
            else:
                self._hien_thi_tab(tab_id)

        for w in (frame, lbl):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)

        return (frame, lbl)

    def _hien_thi_tab(self, tab_id: str):
        # Reset màu sidebar
        for tid, (fr, lb) in self._sidebar_btns.items():
            if tid == tab_id:
                fr.config(bg=PRIMARY); lb.config(bg=PRIMARY, fg=TEXT_WHITE)
            else:
                fr.config(bg=BG_SIDEBAR); lb.config(bg=BG_SIDEBAR, fg="#B0BEC5")

        self._active_tab.set(tab_id)

        # Xóa content cũ
        if self._frame_hien_tai:
            self._frame_hien_tai.destroy()

        # Load frame mới
        frame = self._load_frame(tab_id)
        frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        self._frame_hien_tai = frame

    def _load_frame(self, tab_id: str) -> tk.Frame:
        if tab_id == "dashboard":
            from views.dashboard_view import DashboardView
            return DashboardView(self._content, self._svcs,
                                 on_navigate=self._hien_thi_tab)
        if tab_id == "sinh_vien":
            from views.sinh_vien_view import SinhVienView
            return SinhVienView(self._content, self._svcs,
                                statusbar=self.statusbar)
        if tab_id == "lop_hoc":
            from views.lop_hoc_view import LopHocView
            return LopHocView(self._content, self._svcs,
                              statusbar=self.statusbar)
        if tab_id == "diem_so":
            from views.diem_so_view import DiemSoView
            return DiemSoView(self._content, self._svcs,
                              statusbar=self.statusbar)
        if tab_id == "nguoi_dung":
            from views.nguoi_dung_view import NguoiDungView
            return NguoiDungView(self._content, self._svcs,
                                 statusbar=self.statusbar)
        return tk.Frame(self._content, bg=BG_APP)

    def _dang_xuat(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self._nd_svc.dang_xuat()
            self.destroy()
            # Khởi động lại app
            import main
            main.khoi_chay()