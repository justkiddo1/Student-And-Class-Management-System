import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.theme import *
from views.widgets import AppButton, DataTable, HeadingLabel, FormField, Card
from models.diem_so import DiemSo


class DiemSoView(tk.Frame):
    COLS = [
        ("mssv", "MSSV", 90, "center"),
        ("cc", "Chuyên cần", 90, "center"),
        ("kt1", "KT lần 1", 85, "center"),
        ("kt2", "KT lần 2", 85, "center"),
        ("tl", "Tiểu luận", 85, "center"),
        ("gk", "Giữa kỳ", 80, "center"),
        ("ck", "Cuối kỳ", 85, "center"),
        ("tk", "Tổng kết", 85, "center"),
        ("xl", "Xếp loại", 95, "center"),
        ("kq", "Kết quả", 80, "center"),
    ]

    def __init__(self, parent, services, statusbar, lop_filter: list[str] | None = None):
        super().__init__(parent, bg=BG_APP)
        self._ds_svc = services["diem"]
        self._lop_svc = services["lop"]
        self._sv_svc = services["sv"]
        self._status = statusbar
        self._lop_filter = lop_filter
        self._mode = None
        self._ma_lop_hien_tai = tk.StringVar()
        self._lop_display_map: dict[str, str] = {}
        self._build_ui()
        self._khoa_form()

    # BUILD UI
    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(hdr, text="Quản lý Điểm số", font=FONT_TITLE,fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        AppButton(hdr, "Xuất Excel bảng điểm", style="outline",icon=ICON["export"],command=self._xuat_excel).pack(side="right")

        # Chọn lớp
        lop_bar = tk.Frame(self, bg=BG_APP)
        lop_bar.pack(fill="x", pady=(0, 8))

        tk.Label(lop_bar, text="Chọn lớp:", font=FONT_BOLD,fg=TEXT_MAIN, bg=BG_APP).pack(side="left", padx=(0, 8))

        self._cb_lop = ttk.Combobox(lop_bar, textvariable=self._ma_lop_hien_tai,
                                    state="readonly", font=FONT_NORMAL, width=32)
        self._cb_lop.pack(side="left")
        self._cb_lop.bind("<<ComboboxSelected>>", lambda e: self._on_chon_lop())

        AppButton(lop_bar, "Xem", style="primary",command=self._tai_du_lieu).pack(side="left", padx=(8, 0))

        self._lbl_tk = tk.Label(lop_bar, text="", font=FONT_SMALL,fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_tk.pack(side="right")

        # Body: bảng + form
        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)
        self._build_table(main)
        self._build_form(main)
        self._cap_nhat_cb_lop()

    # Bảng điểm
    def _build_table(self, parent):
        left = tk.Frame(parent, bg=BG_APP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tbl_f = tk.Frame(left, bg=BG_APP)
        tbl_f.pack(fill="both", expand=True)

        self.table = DataTable(tbl_f, columns=self.COLS, height=18)

        # Scrollbar dọc
        sb_y = DataTable.them_scrollbar(tbl_f, self.table)
        # Scrollbar ngang
        sb_x = ttk.Scrollbar(tbl_f, orient="horizontal",command=self.table.xview)
        self.table.configure(xscrollcommand=sb_x.set)

        sb_x.pack(side="bottom", fill="x")
        sb_y.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

        self.table.bind("<<TreeviewSelect>>", self._on_chon_hang)

        # Nút hành động
        btn_row = tk.Frame(left, bg=BG_APP)
        btn_row.pack(fill="x", pady=(8, 0))
        AppButton(btn_row, "Thêm điểm", style="primary", icon=ICON["add"],command=self._bat_dau_them).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Cập nhật", style="outline", icon=ICON["edit"],command=self._bat_dau_sua).pack(side="left")

    # Form nhập điểm
    def _build_form(self, parent):
        right = Card(parent, padx=16, pady=14)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=270)

        self._form_title = HeadingLabel(right, "Chi tiết điểm", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(0, 10))

        # Combobox MSSV
        tk.Label(right, text="Sinh viên *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._sv_var = tk.StringVar()
        self._cb_sv = ttk.Combobox(right, textvariable=self._sv_var,state="disabled", font=FONT_NORMAL, width=26)
        self._cb_sv.pack(fill="x", pady=(2, 10))

        # Section: Điểm thành phần
        self._section_lbl = tk.Label(right, text="── Điểm thành phần ──",font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        self._section_lbl.pack(anchor="w", pady=(0, 4))

        self._f_cc = FormField(right, "Chuyên cần (0–10)", "0 - 10")
        self._f_kt1 = FormField(right, "Kiểm tra lần 1 (0–10)", "0 - 10")
        self._f_kt2 = FormField(right, "Kiểm tra lần 2 (0–10)", "0 - 10")
        self._f_tl = FormField(right, "Tiểu luận (0–10)", "0 - 10")
        self._f_ck = FormField(right, "Thi cuối kỳ (0–10)", "0 - 10")

        for f in [self._f_cc, self._f_kt1, self._f_kt2, self._f_tl, self._f_ck]:
            f.pack(fill="x", pady=3)

        # Hiển thị điểm tự tính (readonly)
        gk_row = tk.Frame(right, bg=BG_CARD)
        gk_row.pack(fill="x", pady=(6, 0))
        tk.Label(gk_row, text="→ Điểm GK tự tính:",font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
        self._lbl_gk = tk.Label(gk_row, text="—",font=FONT_BOLD, fg=PRIMARY, bg=BG_CARD)
        self._lbl_gk.pack(side="right")

        tk_row = tk.Frame(right, bg=BG_CARD)
        tk_row.pack(fill="x", pady=(2, 8))
        tk.Label(tk_row, text="→ Tổng kết tự tính:",font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
        self._lbl_tktk = tk.Label(tk_row, text="—",font=FONT_BOLD, fg=SUCCESS, bg=BG_CARD)
        self._lbl_tktk.pack(side="right")

        # Bind auto-tính khi nhập
        for f in [self._f_cc, self._f_kt1, self._f_kt2, self._f_tl, self._f_ck]:
            f.entry.bind("<KeyRelease>", lambda e: self._cap_nhat_preview())

        # Nút Lưu / Hủy
        btn_row = tk.Frame(right, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(4, 0))
        AppButton(btn_row, "Lưu", style="primary", icon=ICON["save"],command=self._luu).pack(side="left", fill="x",expand=True, padx=(0, 4))
        AppButton(btn_row, "Hủy", style="ghost", command=self._huy).pack(side="left", fill="x", expand=True)

    def _section(self, parent, title):
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(fill="x", pady=(8, 2))
        tk.Label(f, text=title, font=FONT_SMALL, fg=TEXT_MUTED,bg=BG_CARD).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x",expand=True, padx=(6, 0), pady=5)

    # DỮ LIỆU
    def _cap_nhat_cb_lop(self):
        self._lop_display_map.clear()
        ds = []
        for lop in self._lop_svc.lay_tat_ca():
            if self._lop_filter is not None and lop.ma_lop not in self._lop_filter:
                continue
            display = f"{lop.ma_lop}  —  {lop.ten_mon}"
            self._lop_display_map[display] = lop.ma_lop
            ds.append(display)
        self._cb_lop["values"] = ds
        if ds:
            self._cb_lop.current(0)
            self._on_chon_lop()

    def _ma_lop_chon(self) -> str:
        return self._lop_display_map.get(self._ma_lop_hien_tai.get(), "")

    def _on_chon_lop(self):
        self._tai_du_lieu()
        self._huy()

    def _tai_du_lieu(self):
        ma_lop = self._ma_lop_chon()
        if not ma_lop:
            return
        bang_diem = self._bang_diem_mo_rong(ma_lop)
        self.table.xoa_tat_ca()
        for row in bang_diem:
            self.table.chen_hang([
                row["MSSV"],
                row["Chuyên cần"],
                row["KT1"],
                row["KT2"],
                row["Tiểu luận"],
                row["Giữa kỳ"],
                row["Cuối kỳ"],
                row["Tổng kết"],
                row["Xếp loại"],
                row["Kết quả"],
            ])
        if bang_diem:
            co_dtk = [r for r in bang_diem if r["Tổng kết"] not in (None, "—")]
            if co_dtk:
                tb = round(sum(float(r["Tổng kết"]) for r in co_dtk) / len(co_dtk), 2)
                dau = sum(1 for r in co_dtk if float(r["Tổng kết"]) >= 5.0)
                ti_le = round(dau / len(co_dtk) * 100, 1)
                self._lbl_tk.config(
                    text=f"TB: {tb}  |  Đậu: {ti_le}%  |  {len(bang_diem)} SV")
            else:
                self._lbl_tk.config(text=f"{len(bang_diem)} sinh viên — chưa có điểm")
        if self._mode == "add":
            self._cap_nhat_cb_sv_chua_co_diem(ma_lop)

    def _bang_diem_mo_rong(self, ma_lop: str) -> list[dict]:
        lop = self._lop_svc.tim_theo_khoa(ma_lop)
        if not lop:
            return []
        ket_qua = []
        for mssv in lop.danh_sach_mssv:
            ds = self._ds_svc.tim_diem(mssv, ma_lop)

            def _f(v):
                return f"{v:.1f}" if v is not None else "—"

            if ds:
                gk = ds.diem_giua_ky
                dtk = ds.diem_tong_ket
                ket_qua.append({
                    "MSSV": ds.mssv,
                    "Chuyên cần": _f(ds.diem_chuyen_can),
                    "KT1": _f(ds.diem_kt1),
                    "KT2": _f(ds.diem_kt2),
                    "Tiểu luận": _f(ds.diem_tieu_luan),
                    "Giữa kỳ": _f(gk),
                    "Cuối kỳ": _f(ds.diem_cuoi_ky),
                    "Tổng kết": dtk,
                    "Xếp loại": ds.xep_loai,
                    "Kết quả": ds.dau_hay_rot,
                })
            else:
                ket_qua.append({
                    "MSSV": mssv,
                    "Chuyên cần": "—", "KT1": "—", "KT2": "—",
                    "Tiểu luận": "—", "Giữa kỳ": "—",
                    "Cuối kỳ": "—", "Tổng kết": None,
                    "Xếp loại": "Chưa có điểm", "Kết quả": "Chưa xác định",
                })
        ket_qua.sort(key=lambda r: (
            r["Tổng kết"] is None,
            -(r["Tổng kết"] or 0),
        ))
        return ket_qua

    def _cap_nhat_cb_sv_chua_co_diem(self, ma_lop: str):
        lop = self._lop_svc.tim_theo_khoa(ma_lop)
        if not lop:
            self._cb_sv["values"] = []
            return
        items = []
        for mssv in lop.danh_sach_mssv:
            ds = self._ds_svc.tim_diem(mssv, ma_lop)
            if ds and ds.diem_tong_ket is not None:
                continue  # đã có đủ điểm, bỏ qua
            sv = self._sv_svc.tim_theo_khoa(mssv)
            ten = sv.ho_ten if sv else ""
            items.append(f"{mssv}  —  {ten}")
        self._cb_sv["values"] = items
        if items:
            self._cb_sv.current(0)
        self._sv_var.set(items[0] if items else "")

    def _mssv_tu_cb(self) -> str:
        val = self._sv_var.get()
        return val.split("—")[0].strip() if "—" in val else val.strip()

    # FORM LOGIC
    def _khoa_form(self):
        self._cb_sv.config(state="disabled")
        for f in [self._f_cc, self._f_kt1, self._f_kt2, self._f_tl, self._f_ck]:
            f.disable()
        self._lbl_gk.config(text="—")
        self._lbl_tktk.config(text="—")

    def _mo_form(self, khoa_sv=False):
        self._cb_sv.config(state="disabled" if khoa_sv else "readonly")
        for f in [self._f_cc, self._f_kt1, self._f_kt2, self._f_tl, self._f_ck]:
            f.enable()

    def _xoa_form(self):
        self._sv_var.set("")
        for f in [self._f_cc, self._f_kt1, self._f_kt2, self._f_tl, self._f_ck]:
            f.clear()
        self._lbl_gk.config(text="—")
        self._lbl_tktk.config(text="—")

    def _dien_form(self, ds: DiemSo):
        sv = self._sv_svc.tim_theo_khoa(ds.mssv)
        ten = sv.ho_ten if sv else ""
        self._sv_var.set(f"{ds.mssv}  —  {ten}")

        def _s(v): return f"{v:.1f}" if v is not None else ""

        self._f_cc.set(_s(ds.diem_chuyen_can))
        self._f_kt1.set(_s(ds.diem_kt1))
        self._f_kt2.set(_s(ds.diem_kt2))
        self._f_tl.set(_s(ds.diem_tieu_luan))
        self._f_ck.set(_s(ds.diem_cuoi_ky))
        self._cap_nhat_preview_tu_ds(ds)

    def _cap_nhat_preview(self):
        ds = self._build_diem_tu_form("__PREVIEW__", "__PREVIEW__")
        gk = ds.diem_giua_ky
        dtk = ds.diem_tong_ket
        self._lbl_gk.config(
            text=f"{gk:.2f}" if gk is not None else "—",
            fg=PRIMARY)
        self._lbl_tktk.config(
            text=f"{dtk:.2f}" if dtk is not None else "—",
            fg=SUCCESS if (dtk and dtk >= 5) else DANGER if dtk is not None else TEXT_MUTED)

    def _cap_nhat_preview_tu_ds(self, ds: DiemSo):
        gk = ds.diem_giua_ky
        dtk = ds.diem_tong_ket
        self._lbl_gk.config(
            text=f"{gk:.2f}" if gk is not None else "—", fg=PRIMARY)
        self._lbl_tktk.config(
            text=f"{dtk:.2f}" if dtk is not None else "—",
            fg=SUCCESS if (dtk and dtk >= 5) else DANGER if dtk is not None else TEXT_MUTED)

    def _parse(self, val: str) -> float | None:
        try:
            return float(val.strip()) if val.strip() else None
        except ValueError:
            return None

    def _build_diem_tu_form(self, mssv: str, ma_lop: str) -> DiemSo:
        return DiemSo(
            mssv=mssv,
            ma_lop=ma_lop,
            diem_chuyen_can=self._parse(self._f_cc.get()),
            diem_kt1=self._parse(self._f_kt1.get()),
            diem_kt2=self._parse(self._f_kt2.get()),
            diem_tieu_luan=self._parse(self._f_tl.get()),
            diem_cuoi_ky=self._parse(self._f_ck.get()),
        )

    # ACTIONS
    def _on_chon_hang(self, _):
        row = self.table.lay_hang_chon()
        if not row:
            return
        if self._mode == "add":
            return
        mssv = row[0]
        ma_lop = self._ma_lop_chon()
        ds = self._ds_svc.tim_diem(mssv, ma_lop)
        if ds:
            self._mode = None
            self._form_title.config(text="Chi tiết điểm")
            self._dien_form(ds)
            self._khoa_form()
        else:
            self._xoa_form()
            self._khoa_form()

    def _bat_dau_them(self):
        ma_lop = self._ma_lop_chon()
        if not ma_lop:
            self._status.info("Vui lòng chọn lớp trước.")
            return
        self._mode = "add"
        self._form_title.config(text="Nhập điểm mới")
        self._xoa_form()
        self._cap_nhat_cb_sv_chua_co_diem(ma_lop)
        self._mo_form(khoa_sv=False)

    def _bat_dau_sua(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sinh viên.")
            return
        mssv = row[0]
        ma_lop = self._ma_lop_chon()
        ds = self._ds_svc.tim_diem(mssv, ma_lop)
        if not ds:
            messagebox.showwarning("Chưa có điểm",f"Sinh viên {mssv} chưa có điểm. Hãy dùng 'Thêm điểm'.")
            return
        self._mode = "edit"
        self._form_title.config(text="Cập nhật điểm")
        self._dien_form(ds)
        self._mo_form(khoa_sv=True)  # SV không đổi

    def _luu(self):
        if self._mode is None:
            self._status.info("Bấm 'Thêm điểm' hoặc chọn sinh viên rồi 'Cập nhật'.")
            return

        ma_lop = self._ma_lop_chon()
        if not ma_lop:
            self._status.err("Vui lòng chọn lớp trước.")
            return

        if self._mode == "add":
            mssv = self._mssv_tu_cb()
        else:
            mssv = self._mssv_tu_cb()

        if not mssv:
            self._status.err("Vui lòng chọn sinh viên.")
            return

        ds = self._build_diem_tu_form(mssv, ma_lop)
        ok, msg = ds.validate()
        if not ok:
            self._status.err(msg)
            return

        if self._mode == "add":
            ok, msg = self._ds_svc.them(ds)
        else:
            ok, msg = self._ds_svc.cap_nhat(ds)

        if ok:
            self._status.ok(msg)
            self._tai_du_lieu()
            self._huy()
        else:
            self._status.err(msg)

    def _huy(self):
        self._mode = None
        self._form_title.config(text="Chi tiết điểm")
        self._xoa_form()
        self._khoa_form()

    # XUẤT EXCEL
    def _xuat_excel(self):
        ma_lop = self._ma_lop_chon()
        if not ma_lop:
            messagebox.showwarning("Chưa chọn lớp", "Vui lòng chọn lớp trước.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"bang_diem_{ma_lop}.xlsx")
        if path:
            self._xuat_excel_mo_rong(ma_lop, path)
            self._status.ok(f"Đã xuất: {path}")

    def _xuat_excel_mo_rong(self, ma_lop: str, duong_dan: str):
        from handlers.excel_handler import ExcelHandler
        rows = []
        for row in self._bang_diem_mo_rong(ma_lop):
            rows.append({
                "MSSV": row["MSSV"],
                "Chuyên cần": row["Chuyên cần"],
                "KT lần 1": row["KT1"],
                "KT lần 2": row["KT2"],
                "Tiểu luận": row["Tiểu luận"],
                "Giữa kỳ": row["Giữa kỳ"],
                "Cuối kỳ": row["Cuối kỳ"],
                "Tổng kết": row["Tổng kết"] if row["Tổng kết"] else "—",
                "Xếp loại": row["Xếp loại"],
                "Kết quả": row["Kết quả"],
            })
        ExcelHandler(duong_dan).ghi(rows)
