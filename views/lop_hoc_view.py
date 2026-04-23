# views/lop_hoc_view.py
import tkinter as tk
from tkinter import messagebox
from views.theme import *
from views.widgets import AppButton, Card, DataTable, SearchBar, HeadingLabel, FormField
from models.lop_hoc import LopHoc


class LopHocView(tk.Frame):
    COLS = [
        ("ma_lop",    "Mã lớp",    90,  "center"),
        ("ten_mon",   "Tên môn",   200, "w"),
        ("ma_mon",    "Mã môn",    80,  "center"),
        ("gv",        "Giảng viên",160, "w"),
        ("si_so",     "Sĩ số",     70,  "center"),
        ("phong",     "Phòng",     70,  "center"),
        ("lich",      "Lịch học",  130, "w"),
    ]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._lop_svc = services["lop"]
        self._status  = statusbar
        self._mode    = None
        self._build_ui()
        self._tai_du_lieu()

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
        right = Card(parent, padx=16, pady=16)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=280)
        self._form_title = HeadingLabel(right, "Thêm lớp học", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(0, 10))
        self._f_malop  = FormField(right, "Mã lớp",     "VD: CNTT01", required=True)
        self._f_tenmon = FormField(right, "Tên môn",    "Lập trình Python", required=True)
        self._f_mamon  = FormField(right, "Mã môn",     "VD: IT101", required=True)
        self._f_gv     = FormField(right, "Giảng viên", "Họ tên GV", required=True)
        self._f_siso   = FormField(right, "Sĩ số tối đa","50")
        self._f_phong  = FormField(right, "Phòng học",  "VD: P201")
        self._f_lich   = FormField(right, "Lịch học",   "Thứ 2, 7:30-9:30")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso, self._f_phong, self._f_lich]:
            f.pack(fill="x", pady=3)
        btn_row = tk.Frame(right, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))
        AppButton(btn_row, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x", expand=True, padx=(0, 4))
        AppButton(btn_row, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    def _tai_du_lieu(self, ds=None):
        if ds is None:
            ds = self._lop_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for lop in ds:
            self.table.chen_hang([
                lop.ma_lop, lop.ten_mon, lop.ma_mon, lop.giang_vien,
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
            self._f_lich.set(lop.lich_hoc)

    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Thêm lớp học")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso, self._f_phong, self._f_lich]:
            f.clear()
        self._f_malop.entry.config(state="normal")

    def _bat_dau_sua(self):
        if not self.table.lay_hang_chon():
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp.")
            return
        self._mode = "edit"
        self._form_title.config(text="Cập nhật lớp học")
        self._f_malop.entry.config(state="disabled")

    def _luu(self):
        try:
            siso = int(self._f_siso.get() or 50)
        except ValueError:
            self._status.err("Sĩ số phải là số nguyên.")
            return
        lop = LopHoc(
            ma_lop=self._f_malop.get(), ten_mon=self._f_tenmon.get(),
            ma_mon=self._f_mamon.get(), giang_vien=self._f_gv.get(),
            si_so_toi_da=siso, phong_hoc=self._f_phong.get(),
            lich_hoc=self._f_lich.get(),
        )
        if self._mode == "add":
            ok, msg = self._lop_svc.them(lop)
        else:
            lop_cu = self._lop_svc.tim_theo_khoa(lop.ma_lop)
            if lop_cu:
                lop.danh_sach_mssv = lop_cu.danh_sach_mssv
            ok, msg = self._lop_svc.cap_nhat(lop)
        if ok:
            self._status.ok(msg)
            self._tai_du_lieu()
            self._mode = None
        else:
            self._status.err(msg)

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
        self._f_malop.entry.config(state="normal")