# views/diem_so_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.theme import *
from views.widgets import AppButton, DataTable, SearchBar, HeadingLabel, FormField
from models.diem_so import DiemSo


class DiemSoView(tk.Frame):
    COLS = [
        ("mssv",  "MSSV",       90,  "center"),
        ("cc",    "Chuyên cần", 90,  "center"),
        ("gk",    "Giữa kỳ",   90,  "center"),
        ("ck",    "Cuối kỳ",   90,  "center"),
        ("tk",    "Tổng kết",  90,  "center"),
        ("xl",    "Xếp loại",  90,  "center"),
        ("kq",    "Kết quả",   80,  "center"),
    ]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._ds_svc  = services["diem"]
        self._lop_svc = services["lop"]
        self._sv_svc  = services["sv"]
        self._status  = statusbar
        self._mode    = None
        self._ma_lop_hien_tai = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="Quản lý Điểm số", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        AppButton(hdr, "Xuất Excel bảng điểm", style="outline",
                  icon=ICON["export"], command=self._xuat_excel).pack(side="right")

        # Chọn lớp
        lop_frame = tk.Frame(self, bg=BG_APP)
        lop_frame.pack(fill="x", pady=(0, 8))
        tk.Label(lop_frame, text="Chọn lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._cb_lop = ttk.Combobox(lop_frame, textvariable=self._ma_lop_hien_tai,
                                    state="readonly", font=FONT_NORMAL, width=20)
        self._cb_lop.pack(side="left", padx=8)
        self._cb_lop.bind("<<ComboboxSelected>>", lambda e: self._tai_du_lieu())
        AppButton(lop_frame, "Xem", style="primary",
                  command=self._tai_du_lieu).pack(side="left")
        self._lbl_tk = tk.Label(lop_frame, text="", font=FONT_SMALL,
                                fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_tk.pack(side="right")
        self._cap_nhat_cb_lop()

        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)
        self._build_table(main)
        self._build_form(main)

    def _build_table(self, parent):
        left = tk.Frame(parent, bg=BG_APP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tbl_f = tk.Frame(left, bg=BG_APP)
        tbl_f.pack(fill="both", expand=True)
        self.table = DataTable(tbl_f, columns=self.COLS, height=18)
        sb = DataTable.them_scrollbar(tbl_f, self.table)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self._on_chon_hang)
        btn_row = tk.Frame(left, bg=BG_APP)
        btn_row.pack(fill="x", pady=(8, 0))
        AppButton(btn_row, "Thêm điểm", style="primary", icon=ICON["add"],
                  command=self._bat_dau_them).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Cập nhật",  style="outline", icon=ICON["edit"],
                  command=self._bat_dau_sua).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Xóa",       style="danger",  icon=ICON["delete"],
                  command=self._xoa).pack(side="left")

    def _build_form(self, parent):
        from views.widgets import Card
        right = Card(parent, padx=16, pady=16)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=240)
        self._form_title = HeadingLabel(right, "Nhập điểm", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(0, 10))
        self._f_mssv = FormField(right, "MSSV",        "VD: SV001", required=True)
        self._f_cc   = FormField(right, "Chuyên cần",  "0 - 10")
        self._f_gk   = FormField(right, "Giữa kỳ",    "0 - 10")
        self._f_ck   = FormField(right, "Cuối kỳ",    "0 - 10")
        for f in [self._f_mssv, self._f_cc, self._f_gk, self._f_ck]:
            f.pack(fill="x", pady=4)
        btn_row = tk.Frame(right, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))
        AppButton(btn_row, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x", expand=True, padx=(0, 4))
        AppButton(btn_row, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    def _cap_nhat_cb_lop(self):
        ma_lops = [lop.ma_lop for lop in self._lop_svc.lay_tat_ca()]
        self._cb_lop["values"] = ma_lops
        if ma_lops and not self._ma_lop_hien_tai.get():
            self._cb_lop.current(0)
            self._tai_du_lieu()

    def _tai_du_lieu(self):
        ma_lop = self._ma_lop_hien_tai.get()
        if not ma_lop:
            return
        bang_diem = self._ds_svc.bang_diem_lop(ma_lop)
        self.table.xoa_tat_ca()
        for row in bang_diem:
            self.table.chen_hang([
                row["MSSV"], row["Chuyên cần"], row["Giữa kỳ"],
                row["Cuối kỳ"], row["Tổng kết"], row["Xếp loại"], row["Kết quả"],
            ])
        if bang_diem:
            tk_data = self._ds_svc.thong_ke_lop(ma_lop)
            self._lbl_tk.config(
                text=f"TB: {tk_data.get('diem_tb','N/A')} | Đậu: {tk_data.get('ti_le_dau','?')}%"
            )

    def _on_chon_hang(self, _):
        row = self.table.lay_hang_chon()
        if not row:
            return
        self._f_mssv.set(row[0])
        def _safe(v): return "" if v in (None, "None", "N/A") else str(v)
        self._f_cc.set(_safe(row[1]))
        self._f_gk.set(_safe(row[2]))
        self._f_ck.set(_safe(row[3]))

    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Nhập điểm mới")
        for f in [self._f_mssv, self._f_cc, self._f_gk, self._f_ck]:
            f.clear()
        self._f_mssv.entry.config(state="normal")

    def _bat_dau_sua(self):
        if not self.table.lay_hang_chon():
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sinh viên.")
            return
        self._mode = "edit"
        self._form_title.config(text="Cập nhật điểm")
        self._f_mssv.entry.config(state="disabled")

    def _parse_diem(self, val):
        try:
            return float(val) if val else None
        except ValueError:
            return None

    def _luu(self):
        ma_lop = self._ma_lop_hien_tai.get()
        ds = DiemSo(
            mssv=self._f_mssv.get(), ma_lop=ma_lop,
            diem_chuyen_can=self._parse_diem(self._f_cc.get()),
            diem_giua_ky=self._parse_diem(self._f_gk.get()),
            diem_cuoi_ky=self._parse_diem(self._f_ck.get()),
        )
        ok, msg = (self._ds_svc.them(ds) if self._mode == "add"
                   else self._ds_svc.cap_nhat(ds))
        if ok:
            self._status.ok(msg)
            self._tai_du_lieu()
            self._mode = None
        else:
            self._status.err(msg)

    def _xoa(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dòng.")
            return
        ma_lop = self._ma_lop_hien_tai.get()
        if messagebox.askyesno("Xác nhận", f"Xóa điểm của {row[0]} trong {ma_lop}?"):
            ok, msg = self._ds_svc.xoa(row[0], ma_lop)
            if ok:
                self._status.ok(msg)
                self._tai_du_lieu()
            else:
                self._status.err(msg)

    def _huy(self):
        self._mode = None
        self._f_mssv.entry.config(state="normal")

    def _xuat_excel(self):
        ma_lop = self._ma_lop_hien_tai.get()
        if not ma_lop:
            messagebox.showwarning("Chưa chọn lớp", "Vui lòng chọn lớp trước.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
            initialfile=f"bang_diem_{ma_lop}.xlsx")
        if path:
            self._ds_svc.xuat_bang_diem_excel(ma_lop, path)
            self._status.ok(f"Đã xuất: {path}")