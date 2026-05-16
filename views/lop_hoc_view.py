import tkinter as tk
from tkinter import messagebox, ttk
from views.theme import *
from views.widgets import AppButton, Card, DataTable, SearchBar, HeadingLabel, FormField
from models.lop_hoc import LopHoc


class LopHocView(tk.Frame):
    COLS = [
        ("ma_lop",  "Mã lớp",    90,  "center"),
        ("ten_mon", "Tên môn",   200, "w"),
        ("ma_mon",  "Mã môn",    80,  "center"),
        ("loai",    "Loại hình", 90,  "center"),
        ("gv",      "Giảng viên",160, "w"),
        ("si_so",   "Sĩ số",     70,  "center"),
        ("phong",   "Phòng",     70,  "center"),
        ("lich",    "Lịch học",  130, "w"),
    ]

    LOAI_HINH = ["Lý thuyết", "Thực hành", "Online"]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._lop_svc = services["lop"]
        self._status  = statusbar
        self._mode    = None
        self._loai_var = tk.StringVar(value="Lý thuyết")
        self._build_ui()
        self._tai_du_lieu()
        self._khoa_form()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="Quản lý Lớp học", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")

        SearchBar(self, placeholder="Tìm theo tên môn, giảng viên...",
                  on_search=self._tim_kiem).pack(fill="x", pady=(0, 8))

        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)
        self._build_table(main)
        self._build_form(main)

    def _build_table(self, parent):
        left = tk.Frame(parent, bg=BG_APP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tbl_frame = tk.Frame(left, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)
        self.table = DataTable(tbl_frame, columns=self.COLS, height=18)
        sb = DataTable.them_scrollbar(tbl_frame, self.table)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self._on_chon_hang)
        btn_row = tk.Frame(left, bg=BG_APP)
        btn_row.pack(fill="x", pady=(8, 0))
        AppButton(btn_row, "Thêm mới", style="primary", icon=ICON["add"],
                  command=self._bat_dau_them).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Sửa", style="outline", icon=ICON["edit"],
                  command=self._bat_dau_sua).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Xóa", style="danger", icon=ICON["delete"],
                  command=self._xoa).pack(side="left")
        self._lbl_count = tk.Label(btn_row, text="", font=FONT_SMALL,
                                   fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_count.pack(side="right")

    def _build_form(self, parent):
        # Outer card container - fixed width, fills height
        right = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=360)

        # Scrollable inner area
        canvas = tk.Canvas(right, bg=BG_CARD, bd=0,
                           highlightthickness=0, width=340)
        vscroll = ttk.Scrollbar(right, orient="vertical",
                                command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        # Bottom button row — always visible, outside the scroll area
        btn_outer = tk.Frame(right, bg=BG_CARD, pady=8, padx=16)
        btn_outer.pack(side="bottom", fill="x")
        tk.Frame(right, bg=BORDER, height=1).pack(side="bottom", fill="x")

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner scrollable frame
        inner = tk.Frame(canvas, bg=BG_CARD)
        canvas_win = canvas.create_window((0, 0), window=inner,
                                          anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(e):
            canvas.itemconfig(canvas_win, width=e.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)

        # Mouse wheel scroll
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        #Form content inside inner
        pad = {"fill": "x", "pady": 3, "padx": 16}

        self._form_title = HeadingLabel(inner, "Thêm lớp học", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(12, 8), padx=16)

        # Loại hình học — toggle buttons
        tk.Label(inner, text="Loại hình học *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16)
        loai_frame = tk.Frame(inner, bg=BG_CARD)
        loai_frame.pack(anchor="w", padx=16, pady=(3, 6))
        self._loai_btns = {}
        for loai in self.LOAI_HINH:
            btn = tk.Button(
                loai_frame, text=loai, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=4,
                command=lambda l=loai: self._chon_loai(l)
            )
            btn.pack(side="left", padx=(0, 4))
            self._loai_btns[loai] = btn
        self._cap_nhat_loai_btn("Lý thuyết")

        self._f_malop  = FormField(inner, "Mã lớp *",      "VD: CNTT01", required=True)
        self._f_tenmon = FormField(inner, "Tên môn *",      "Lập trình Python", required=True)
        self._f_mamon  = FormField(inner, "Mã môn *",       "VD: IT001", required=True)
        self._f_gv     = FormField(inner, "Giảng viên *",   "Phan Thị Ngọc Mai", required=True)
        self._f_siso   = FormField(inner, "Sĩ số tối đa",  "30")
        self._f_phong  = FormField(inner, "Phòng học",      "A105")

        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso, self._f_phong]:
            f.pack(**pad)

        tk.Label(inner, text="Lịch học *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16, pady=(4, 0))
        self._lich_var = tk.StringVar()
        self._cb_lich = ttk.Combobox(inner, textvariable=self._lich_var,
                                     font=FONT_NORMAL, state="readonly")
        self._cb_lich["values"] = [
            "Tiết 1-3 (7h00 - 9h20)",
            "Tiết 4-6 (9h45 - 11h50)",
            "Tiết 7-9 (12h30 - 14h45)",
            "Tiết 10-12 (15h00 - 17h20)",
            "Tiết 13-15 (18h20 - 20h20)"
        ]
        self._cb_lich.pack(fill="x", padx=16, pady=(3, 12))

        # ── Lưu / Hủy buttons (always visible at bottom) ─────────
        AppButton(btn_outer, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x",
                                          expand=True, padx=(0, 6))
        AppButton(btn_outer, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    # Khóa / Mở form
    def _khoa_form(self):
        """Disable toàn bộ field — chờ người dùng bấm Thêm mới hoặc Sửa."""
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso, self._f_phong]:
            f.disable()
        self._cb_lich.config(state="disabled")
        for btn in self._loai_btns.values():
            btn.config(state="disabled", cursor="arrow")

    def _mo_form(self, khoa_malop=False):
        """Enable toàn bộ field."""
        for f in [self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso, self._f_phong]:
            f.enable()
        if khoa_malop:
            self._f_malop.disable()
        else:
            self._f_malop.enable()
        self._cb_lich.config(state="readonly")
        for btn in self._loai_btns.values():
            btn.config(state="normal", cursor="hand2")

    # Loại hình toggle
    def _chon_loai(self, loai: str):
        self._loai_var.set(loai)
        self._cap_nhat_loai_btn(loai)

    def _cap_nhat_loai_btn(self, active: str):
        for loai, btn in self._loai_btns.items():
            if loai == active:
                btn.config(bg=PRIMARY, fg=TEXT_WHITE)
            else:
                btn.config(bg=BORDER, fg=TEXT_MAIN)

    # Data
    def _tai_du_lieu(self, ds=None):
        if ds is None:
            ds = self._lop_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for lop in ds:
            loai = getattr(lop, "loai_hinh", "Lý thuyết")
            self.table.chen_hang([
                lop.ma_lop, lop.ten_mon, lop.ma_mon, loai,
                lop.giang_vien,
                f"{lop.si_so_hien_tai}/{lop.si_so_toi_da}",
                lop.phong_hoc, lop.lich_hoc,
            ])
        self._lbl_count.config(text=f"Tổng: {len(ds)} lớp")

    def _tim_kiem(self, tu_khoa=""):
        ds = [lop for lop in self._lop_svc.lay_tat_ca()
              if tu_khoa.lower() in lop.ten_mon.lower()
              or tu_khoa.lower() in lop.giang_vien.lower()
              or tu_khoa.lower() in lop.ma_lop.lower()]
        self._tai_du_lieu(ds)

    def _on_chon_hang(self, _):
        row = self.table.lay_hang_chon()
        if not row:
            return
        lop = self._lop_svc.tim_theo_khoa(row[0])
        if lop:
            self._f_malop.set(lop.ma_lop)
            self._f_tenmon.set(lop.ten_mon)
            self._f_mamon.set(lop.ma_mon)
            self._f_gv.set(lop.giang_vien)
            self._f_siso.set(str(lop.si_so_toi_da))
            self._f_phong.set(lop.phong_hoc)
            self._lich_var.set(lop.lich_hoc)
            loai = getattr(lop, "loai_hinh", "Lý thuyết")
            self._chon_loai(loai)

    # CRUD
    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Thêm lớp học")
        self._f_malop.clear(); self._f_tenmon.clear()
        self._f_mamon.clear(); self._f_gv.clear()
        self._f_siso.clear();  self._f_phong.clear()
        self._lich_var.set("")
        self._chon_loai("Lý thuyết")
        self._mo_form(khoa_malop=False)

    def _bat_dau_sua(self):
        if not self.table.lay_hang_chon():
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp.")
            return
        self._mode = "edit"
        self._form_title.config(text="Cập nhật lớp học")
        self._mo_form(khoa_malop=True)

    def _luu(self):
        if self._mode is None:
            self._status.info("Vui lòng bấm 'Thêm mới' trước.")
            return
        try:
            siso = int(self._f_siso.get() or 30)
        except ValueError:
            self._status.err("Sĩ số phải là số nguyên.")
            return
        lich_hoc = self._lich_var.get().strip()
        if not lich_hoc:
            self._status.err("Vui lòng chọn lịch học.")
            return

        lop = LopHoc(
            ma_lop=self._f_malop.get().strip(),
            ten_mon=self._f_tenmon.get().strip(),
            ma_mon=self._f_mamon.get().strip(),
            giang_vien=self._f_gv.get().strip(),
            si_so_toi_da=siso,
            phong_hoc=self._f_phong.get().strip(),
            lich_hoc=lich_hoc,
        )

        if hasattr(lop, "loai_hinh"):
            lop.loai_hinh = self._loai_var.get()

        if self._mode == "add":
            ok, msg = self._lop_svc.them(lop)
        else:
            lop_cu = self._lop_svc.tim_theo_khoa(lop.ma_lop)
            if lop_cu:
                lop.danh_sach_mssv = lop_cu.danh_sach_mssv
            ok, msg = self._lop_svc.cap_nhat(lop)

        if ok:
            self._status.ok("✅ Lưu thành công!")
            self._tai_du_lieu()
            self._huy()
        else:
            self._status.err(msg or "Lưu thất bại")

    def _xoa(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp.")
            return
        if messagebox.askyesno("Xác nhận", f"Xóa lớp {row[0]}?"):
            ok, msg = self._lop_svc.xoa(row[0])
            if ok:
                self._status.ok(msg)
                self._tai_du_lieu()
            else:
                self._status.err(msg)

    def _huy(self):
        self._mode = None
        self._form_title.config(text="Thêm lớp học")
        self._f_malop.clear(); self._f_tenmon.clear()
        self._f_mamon.clear(); self._f_gv.clear()
        self._f_siso.clear();  self._f_phong.clear()
        self._lich_var.set("")
        self._chon_loai("Lý thuyết")
        self._khoa_form()