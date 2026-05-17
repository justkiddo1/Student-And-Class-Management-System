import tkinter as tk
from tkinter import messagebox
from views.theme import *
from views.widgets import StatusBar
from models.nguoi_dung import NguoiDung


class GiaoVienMainView(tk.Tk):
    MENU = [
        ("lich_day", "📅", "Lịch dạy"),
        ("lop_cua_toi", "🏫", "Lớp của tôi"),
        ("diem_danh", "✅", "Điểm danh"),
        ("nhap_diem", "📊", "Nhập điểm"),
        ("nhan_xet", "📝", "Nhận xét"),
    ]

    def __init__(self, services: dict, nguoi_dung: NguoiDung):
        super().__init__()
        self._svcs = services
        self._nd = nguoi_dung

        self.title(f"SMS — Giảng viên: {nguoi_dung.ho_ten}")
        self.configure(bg=BG_APP)
        self.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.minsize(WIN_MIN_W, WIN_MIN_H)

        self._active_tab = tk.StringVar(value="lich_day")
        self._frame_hien_tai = None

        # Lấy danh sách lớp GV dạy (dùng chung nhiều tab)
        self._lop_cua_toi = self._lay_lop_cua_toi()

        self._build_ui()
        self._hien_thi_tab("lich_day")

    # Lấy lớp GV dạy
    def _lay_lop_cua_toi(self):
        all_lop = self._svcs["lop"].lay_tat_ca()
        ten_gv = self._nd.ho_ten.strip().lower()
        return [lop for lop in all_lop
                if lop.giang_vien.strip().lower() == ten_gv]

    # Build UI
    def _build_ui(self):
        # Topbar
        topbar = tk.Frame(self, bg=BG_SIDEBAR, height=TOPBAR_H)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🎓 SMS — Giảng viên",
                 font=(FONT_FAMILY, 14, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE, padx=16).pack(side="left", fill="y")

        tk.Label(topbar,
                 text=f"👤  {self._nd.ho_ten}  |  GIẢNG VIÊN",
                 font=FONT_SMALL, bg=BG_SIDEBAR, fg="#90CAF9",
                 padx=16).pack(side="right", fill="y")

        # Body
        body = tk.Frame(self, bg=BG_APP)
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        self._sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Content area
        self._content = tk.Frame(body, bg=BG_APP)
        self._content.pack(side="left", fill="both", expand=True)

        # Statusbar
        self.statusbar = StatusBar(self)
        self.statusbar.pack(side="bottom", fill="x")

    def _build_sidebar(self):
        tk.Frame(self._sidebar, height=16, bg=BG_SIDEBAR).pack()

        self._sidebar_btns: dict[str, tuple] = {}
        for tab_id, icon, label in self.MENU:
            btn = self._make_sidebar_btn(tab_id, icon, label)
            self._sidebar_btns[tab_id] = btn

        # Nút đăng xuất ở dưới cùng
        tk.Frame(self._sidebar, bg=BG_SIDEBAR).pack(expand=True)
        self._make_sidebar_btn("_logout", ICON["logout"], "Đăng xuất",
                               is_logout=True)

    def _make_sidebar_btn(self, tab_id, icon, label, is_logout=False):
        bg_normal = BG_SIDEBAR
        bg_hover = "#283593"

        frame = tk.Frame(self._sidebar, bg=bg_normal, cursor="hand2")
        frame.pack(fill="x", pady=1)

        lbl = tk.Label(frame,
                       text=f"  {icon}  {label}",
                       font=FONT_NORMAL, bg=bg_normal,
                       fg="#B0BEC5", anchor="w", padx=8, pady=10)
        lbl.pack(fill="x")

        def enter(_):
            if self._active_tab.get() != tab_id:
                frame.config(bg=bg_hover);
                lbl.config(bg=bg_hover)

        def leave(_):
            if self._active_tab.get() != tab_id:
                frame.config(bg=bg_normal);
                lbl.config(bg=bg_normal)

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

    # Chuyển tab
    def _hien_thi_tab(self, tab_id: str):
        for tid, (fr, lb) in self._sidebar_btns.items():
            if tid == tab_id:
                fr.config(bg=PRIMARY);
                lb.config(bg=PRIMARY, fg=TEXT_WHITE)
            else:
                fr.config(bg=BG_SIDEBAR);
                lb.config(bg=BG_SIDEBAR, fg="#B0BEC5")

        self._active_tab.set(tab_id)

        if self._frame_hien_tai:
            self._frame_hien_tai.destroy()

        frame = self._load_frame(tab_id)
        frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        self._frame_hien_tai = frame

    def _load_frame(self, tab_id: str) -> tk.Frame:
        if tab_id == "lich_day":
            from views.gv_tabs.lich_day_view import LichDayView
            return LichDayView(
                self._content, self._lop_cua_toi,
                on_click_lop=lambda ml: self._hien_thi_tab("lop_cua_toi")
            )
        if tab_id == "lop_cua_toi":
            from views.gv_tabs.lop_cua_toi_view import LopCuaToiView
            return LopCuaToiView(
                self._content, self._svcs, self._lop_cua_toi,
                statusbar=self.statusbar
            )
        if tab_id == "diem_danh":
            from views.gv_tabs.diem_danh_view import DiemDanhView
            return DiemDanhView(
                self._content, self._svcs, self._lop_cua_toi,
                statusbar=self.statusbar
            )
        if tab_id == "nhap_diem":
            from views.gv_tabs.nhap_diem_view import NhapDiemView
            return NhapDiemView(
                self._content, self._svcs, self._lop_cua_toi,
                statusbar=self.statusbar
            )
        if tab_id == "nhan_xet":
            from views.gv_tabs.nhan_xet_view import NhanXetView
            return NhanXetView(
                self._content, self._svcs, self._nd, self._lop_cua_toi,
                statusbar=self.statusbar
            )
        return tk.Frame(self._content, bg=BG_APP)

    # Đăng xuất
    def _dang_xuat(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self._svcs["nd"].dang_xuat()
            self.destroy()
            import main
            main.khoi_chay()
