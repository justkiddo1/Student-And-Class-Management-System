import tkinter as tk
from tkinter import messagebox, ttk
from views.theme import *
from views.widgets import AppButton, Card, DataTable, SearchBar, HeadingLabel, FormField
from models.lop_hoc import LopHoc, BuoiHoc, THU_LIST, lay_tiet_list, lay_gio


# LichHocPicker
class LichHocPicker(tk.Frame):
    def __init__(self, parent, loai_hinh_var: tk.StringVar, bg=BG_CARD, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._bg = bg
        self._loai_var = loai_hinh_var
        self._rows: list[dict] = []

        self._list_frame = tk.Frame(self, bg=bg)
        self._list_frame.pack(fill="x")

        AppButton(self, "＋  Thêm buổi học", style="outline",
                  command=self.them_hang).pack(anchor="w", pady=(6, 0))

        self._loai_var.trace_add("write", self._on_loai_thay_doi)

    # Xử lý khi loại hình thay đổi
    def _on_loai_thay_doi(self, *_):
        loai = self._loai_var.get()
        tiet_list = lay_tiet_list(loai)
        for r in self._rows:
            cb: ttk.Combobox = r["cb_tiet"]
            tiet_cu = r["tiet_var"].get()
            cb["values"] = tiet_list
            if tiet_cu not in tiet_list:
                r["tiet_var"].set(tiet_list[0] if tiet_list else "")
            # Cập nhật label giờ
            self._cap_nhat_gio(r)

    def _cap_nhat_gio(self, r: dict):
        loai = self._loai_var.get()
        tiet = r["tiet_var"].get()
        r["lbl_gio"].config(text=lay_gio(loai, tiet))

    # Thêm / Xóa hàng
    def them_hang(self, thu="Thứ 2", tiet="", phong=""):
        loai = self._loai_var.get()
        tiet_list = lay_tiet_list(loai)
        if tiet not in tiet_list:
            tiet = tiet_list[0] if tiet_list else ""

        row_frame = tk.Frame(self._list_frame, bg=self._bg, pady=3)
        row_frame.pack(fill="x")

        thu_var  = tk.StringVar(value=thu)
        tiet_var = tk.StringVar(value=tiet)
        phong_var = tk.StringVar(value=phong)

        # Thứ
        cb_thu = ttk.Combobox(row_frame, textvariable=thu_var,
                              values=THU_LIST, state="readonly",
                              width=9, font=FONT_SMALL)
        cb_thu.pack(side="left", padx=(0, 4))

        # Tiết — values phụ thuộc loại hình
        cb_tiet = ttk.Combobox(row_frame, textvariable=tiet_var,
                               values=tiet_list, state="readonly",
                               width=11, font=FONT_SMALL)
        cb_tiet.pack(side="left", padx=(0, 4))

        # Giờ học — tự cập nhật khi đổi tiết hoặc loại hình
        lbl_gio = tk.Label(row_frame,
                           text=lay_gio(loai, tiet),
                           font=FONT_SMALL, fg=TEXT_MUTED,
                           bg=self._bg, width=16, anchor="w")
        lbl_gio.pack(side="left", padx=(0, 4))

        # Phòng
        tk.Label(row_frame, text="Phòng", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=self._bg).pack(side="left")
        ent_phong = tk.Entry(row_frame, textvariable=phong_var,
                             font=FONT_SMALL, width=7,
                             relief="solid", bd=1)
        ent_phong.pack(side="left", padx=(3, 6))

        row_data = {
            "frame":    row_frame,
            "thu_var":  thu_var,
            "tiet_var": tiet_var,
            "phong_var":phong_var,
            "cb_tiet":  cb_tiet,
            "lbl_gio":  lbl_gio,
        }

        # Cập nhật giờ khi đổi tiết
        def _on_tiet_change(*_, r=row_data):
            self._cap_nhat_gio(r)
        tiet_var.trace_add("write", _on_tiet_change)

        # Nút xóa hàng
        btn_xoa = tk.Button(row_frame, text="✕", font=FONT_SMALL,
                            fg=DANGER, bg=self._bg, relief="flat",
                            cursor="hand2",
                            command=lambda r=row_data: self._xoa_hang(r))
        btn_xoa.pack(side="left")

        self._rows.append(row_data)

    def _xoa_hang(self, row_data: dict):
        row_data["frame"].destroy()
        self._rows.remove(row_data)

    # Public API
    def lay_buoi_hoc(self) -> list[BuoiHoc]:
        loai = self._loai_var.get()
        result = []
        for r in self._rows:
            tiet = r["tiet_var"].get()
            result.append(BuoiHoc(
                thu=r["thu_var"].get(),
                tiet=tiet,
                gio=lay_gio(loai, tiet),
                phong=r["phong_var"].get().strip(),
            ))
        return result

    def set_buoi_hoc(self, buoi_list: list[BuoiHoc]):
        self.xoa_tat_ca()
        for b in buoi_list:
            self.them_hang(b.thu, b.tiet, b.phong)

    def xoa_tat_ca(self):
        for r in list(self._rows):
            r["frame"].destroy()
        self._rows.clear()

    def set_state(self, enabled: bool):
        state_cb  = "readonly" if enabled else "disabled"
        state_ent = "normal"   if enabled else "disabled"
        state_btn = "normal"   if enabled else "disabled"
        for r in self._rows:
            r["cb_tiet"].config(state=state_cb)
            for child in r["frame"].winfo_children():
                cls = child.__class__.__name__
                try:
                    if cls == "Combobox":
                        child.config(state=state_cb)
                    elif cls == "Entry":
                        child.config(state=state_ent)
                    elif cls == "Button":
                        child.config(state=state_btn)
                except Exception:
                    pass


# LopHocView
class LopHocView(tk.Frame):
    COLS = [
        ("ma_lop",  "Mã lớp",    90,  "center"),
        ("ten_mon", "Tên môn",   200, "w"),
        ("ma_mon",  "Mã môn",    80,  "center"),
        ("loai",    "Loại hình", 90,  "center"),
        ("gv",      "Giảng viên",160, "w"),
        ("si_so",   "Sĩ số",     70,  "center"),
        ("lich",    "Lịch học",  220, "w"),
    ]

    LOAI_HINH = ["Lý thuyết", "Thực hành", "Online"]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._lop_svc  = services["lop"]
        self._status   = statusbar
        self._mode     = None
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

    # Bảng danh sách
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

    # Form bên phải
    def _build_form(self, parent):
        right = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=420)

        # Canvas cuộn
        canvas = tk.Canvas(right, bg=BG_CARD, bd=0,
                           highlightthickness=0, width=400)
        vscroll = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        # Nút Lưu/Hủy luôn hiển thị ở dưới
        btn_outer = tk.Frame(right, bg=BG_CARD, pady=8, padx=16)
        btn_outer.pack(side="bottom", fill="x")
        tk.Frame(right, bg=BORDER, height=1).pack(side="bottom", fill="x")

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_CARD)
        canvas_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_resize(e):
            canvas.itemconfig(canvas_win, width=e.width)
        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        pad = {"fill": "x", "pady": 3, "padx": 16}

        self._form_title = HeadingLabel(inner, "Thêm lớp học", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(12, 8), padx=16)

        # Loại hình (toggle buttons)
        tk.Label(inner, text="Loại hình học *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16)
        loai_frame = tk.Frame(inner, bg=BG_CARD)
        loai_frame.pack(anchor="w", padx=16, pady=(3, 8))
        self._loai_btns: dict[str, tk.Button] = {}
        for loai in self.LOAI_HINH:
            btn = tk.Button(
                loai_frame, text=loai, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=12, pady=5,
                command=lambda l=loai: self._chon_loai(l)
            )
            btn.pack(side="left", padx=(0, 4))
            self._loai_btns[loai] = btn
        self._cap_nhat_loai_btn("Lý thuyết")

        # Thông tin cơ bản
        self._f_malop  = FormField(inner, "Mã lớp *",     "VD: CNTT01", required=True)
        self._f_tenmon = FormField(inner, "Tên môn *",    "Lập trình Python", required=True)
        self._f_mamon  = FormField(inner, "Mã môn *",     "VD: IT001", required=True)
        self._f_gv     = FormField(inner, "Giảng viên *", "Phan Thị Ngọc Mai", required=True)
        self._f_siso   = FormField(inner, "Sĩ số tối đa","50")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.pack(**pad)

        # Lịch học picker
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(10, 6))

        lich_hdr = tk.Frame(inner, bg=BG_CARD)
        lich_hdr.pack(fill="x", padx=16, pady=(0, 4))
        tk.Label(lich_hdr, text="📅  Lịch học trong tuần",
                 font=FONT_BOLD, fg=TEXT_MAIN, bg=BG_CARD).pack(side="left")

        self._lbl_loai_hint = tk.Label(
            lich_hdr, text="(Lý thuyết: 3 tiết/buổi)",
            font=FONT_SMALL, fg=PRIMARY, bg=BG_CARD)
        self._lbl_loai_hint.pack(side="left", padx=8)


        col_hdr = tk.Frame(inner, bg=BG_CARD)
        col_hdr.pack(fill="x", padx=16, pady=(0, 2))
        for text, w in [("Thứ", 75), ("Tiết học", 90), ("Giờ học", 120), ("Phòng", 60)]:
            tk.Label(col_hdr, text=text, font=FONT_SMALL, fg=TEXT_MUTED,
                     bg=BG_CARD, width=w//7, anchor="w").pack(side="left", padx=2)

        self._lich_picker = LichHocPicker(inner,
                                          loai_hinh_var=self._loai_var,
                                          bg=BG_CARD)
        self._lich_picker.pack(fill="x", padx=16, pady=(0, 10))

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 8))

        # Lưu / Hủy
        AppButton(btn_outer, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x",
                                          expand=True, padx=(0, 6))
        AppButton(btn_outer, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    # Loại hình toggle
    def _chon_loai(self, loai: str):
        self._loai_var.set(loai)
        self._cap_nhat_loai_btn(loai)
        # Cập nhật hint
        hints = {
            "Lý thuyết": "(Lý thuyết: 3 tiết/buổi)",
            "Thực hành": "(Thực hành: 5 tiết/buổi)",
            "Online":    "(Online: 3 tiết/buổi)",
        }
        self._lbl_loai_hint.config(text=hints.get(loai, ""))

    def _cap_nhat_loai_btn(self, active: str):
        colors = {"Lý thuyết": INFO, "Thực hành": SUCCESS, "Online": ACCENT}
        for loai, btn in self._loai_btns.items():
            if loai == active:
                btn.config(bg=colors.get(loai, PRIMARY), fg=TEXT_WHITE)
            else:
                btn.config(bg=BORDER, fg=TEXT_MAIN)

    # Khóa / Mở form
    def _khoa_form(self):
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.disable()
        self._lich_picker.set_state(False)
        for btn in self._loai_btns.values():
            btn.config(state="disabled", cursor="arrow")

    def _mo_form(self, khoa_malop=False):
        for f in [self._f_tenmon, self._f_mamon, self._f_gv, self._f_siso]:
            f.enable()
        if khoa_malop:
            self._f_malop.disable()
        else:
            self._f_malop.enable()
        self._lich_picker.set_state(True)
        for btn in self._loai_btns.values():
            btn.config(state="normal", cursor="hand2")

    # Dữ liệu
    def _tai_du_lieu(self, ds=None):
        if ds is None:
            ds = self._lop_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for lop in ds:
            self.table.chen_hang([
                lop.ma_lop, lop.ten_mon, lop.ma_mon,
                getattr(lop, "loai_hinh", "Lý thuyết"),
                lop.giang_vien,
                f"{lop.si_so_hien_tai}/{lop.si_so_toi_da}",
                lop.lich_hoc_str,
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
            self._dien_form(lop)

    def _dien_form(self, lop: LopHoc):
        self._f_malop.set(lop.ma_lop)
        self._f_tenmon.set(lop.ten_mon)
        self._f_mamon.set(lop.ma_mon)
        self._f_gv.set(lop.giang_vien)
        self._f_siso.set(str(lop.si_so_toi_da))
        loai = getattr(lop, "loai_hinh", "Lý thuyết")
        self._chon_loai(loai)
        self._lich_picker.set_buoi_hoc(lop.lich_hoc)

    # CRUD
    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Thêm lớp học mới")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.clear()
        self._chon_loai("Lý thuyết")
        self._lich_picker.xoa_tat_ca()
        self._lich_picker.them_hang()
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
            siso = int(self._f_siso.get() or 50)
        except ValueError:
            self._status.err("Sĩ số phải là số nguyên.")
            return

        buoi_list = self._lich_picker.lay_buoi_hoc()
        if not buoi_list:
            self._status.err("Vui lòng thêm ít nhất một buổi học.")
            return

        lop = LopHoc(
            ma_lop=self._f_malop.get().strip(),
            ten_mon=self._f_tenmon.get().strip(),
            ma_mon=self._f_mamon.get().strip(),
            giang_vien=self._f_gv.get().strip(),
            si_so_toi_da=siso,
            loai_hinh=self._loai_var.get(),
        )
        lop.lich_hoc = buoi_list

        if self._mode == "edit":
            lop_cu = self._lop_svc.tim_theo_khoa(lop.ma_lop)
            if lop_cu:
                lop.danh_sach_mssv = lop_cu.danh_sach_mssv

        ok, msg = (self._lop_svc.them(lop) if self._mode == "add"
                   else self._lop_svc.cap_nhat(lop))

        if ok:
            self._status.ok("Lưu thành công!")
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
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.clear()
        self._lich_picker.xoa_tat_ca()
        self._chon_loai("Lý thuyết")
        self._khoa_form()