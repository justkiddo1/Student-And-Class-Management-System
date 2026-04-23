# views/sinh_vien_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from views.theme import *
from views.widgets import (AppButton, Card, DataTable, SearchBar,
                            HeadingLabel, FormField)
from models.sinh_vien import SinhVien


class SinhVienView(tk.Frame):
    """Tab quản lý sinh viên — CRUD đầy đủ."""

    COLS = [
        ("mssv",     "MSSV",         90,  "center"),
        ("ho_ten",   "Họ và tên",    180, "w"),
        ("ngay_sinh","Ngày sinh",     90,  "center"),
        ("gioi_tinh","Giới tính",     75,  "center"),
        ("ma_lop",   "Lớp",          80,  "center"),
        ("email",    "Email",        180, "w"),
        ("sdt",      "Số ĐT",        105, "center"),
    ]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._sv_svc  = services["sv"]
        self._lop_svc = services["lop"]
        self._status  = statusbar
        self._mode    = None   # "add" | "edit"
        self._build_ui()
        self._tai_du_lieu()

    # ================================================================== #
    def _build_ui(self):
        # ── Header ───────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="Quản lý Sinh viên", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        AppButton(hdr, "Xuất CSV",   style="outline", icon=ICON["export"],
                  command=self._xuat_csv).pack(side="right", padx=(4, 0))
        AppButton(hdr, "Nhập CSV",   style="outline", icon=ICON["import"],
                  command=self._nhap_csv).pack(side="right", padx=4)
        AppButton(hdr, "Xuất Excel", style="outline", icon=ICON["export"],
                  command=self._xuat_excel).pack(side="right", padx=4)

        # ── Thanh tìm kiếm + lọc ─────────────────────────────────────
        toolbar = tk.Frame(self, bg=BG_APP)
        toolbar.pack(fill="x", pady=(0, 8))

        SearchBar(toolbar, placeholder="Tìm theo tên, MSSV...",
                  on_search=self._tim_kiem).pack(side="left", fill="x",
                                                 expand=True, padx=(0, 8))

        # Lọc theo lớp
        tk.Label(toolbar, text="Lớp:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(side="left")
        self._loc_lop = ttk.Combobox(toolbar, width=10, state="readonly",
                                     font=FONT_SMALL)
        self._loc_lop.pack(side="left", padx=4)
        self._loc_lop.bind("<<ComboboxSelected>>", lambda e: self._tim_kiem())

        # Lọc theo giới tính
        self._loc_gt = ttk.Combobox(toolbar, width=8, state="readonly",
                                    font=FONT_SMALL,
                                    values=["Tất cả", "Nam", "Nữ"])
        self._loc_gt.current(0)
        self._loc_gt.pack(side="left", padx=4)
        self._loc_gt.bind("<<ComboboxSelected>>", lambda e: self._tim_kiem())

        # ── Nội dung chính: bảng bên trái + form bên phải ────────────
        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)

        self._build_table(main)
        self._build_form(main)

    def _build_table(self, parent):
        left = tk.Frame(parent, bg=BG_APP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Bảng + scrollbar
        tbl_frame = tk.Frame(left, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)

        self.table = DataTable(tbl_frame, columns=self.COLS, height=18)
        sb = DataTable.them_scrollbar(tbl_frame, self.table)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self._on_chon_hang)

        # Nút hành động dưới bảng
        btn_row = tk.Frame(left, bg=BG_APP)
        btn_row.pack(fill="x", pady=(8, 0))
        AppButton(btn_row, "Thêm mới", style="primary", icon=ICON["add"],
                  command=self._bat_dau_them).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Sửa",  style="outline", icon=ICON["edit"],
                  command=self._bat_dau_sua).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Xóa",  style="danger",  icon=ICON["delete"],
                  command=self._xoa).pack(side="left")
        AppButton(btn_row, "Làm mới", style="ghost", icon=ICON["refresh"],
                  command=self._tai_du_lieu).pack(side="right")

        self._lbl_count = tk.Label(btn_row, text="", font=FONT_SMALL,
                                   fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_count.pack(side="right", padx=8)

    def _build_form(self, parent):
        right = Card(parent, padx=16, pady=16)
        right.pack(side="right", fill="y", ipadx=4)
        right.pack_propagate(False)
        right.config(width=280)

        self._form_title = HeadingLabel(right, "Thêm sinh viên", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(0, 12))

        self._f_mssv   = FormField(right, "MSSV",        "VD: SV001", required=True)
        self._f_hoten  = FormField(right, "Họ và tên",   "Nguyễn Văn A", required=True)
        self._f_ns     = FormField(right, "Ngày sinh",   "DD/MM/YYYY", required=True)
        self._f_email  = FormField(right, "Email",       "email@gmail.com", required=True)
        self._f_sdt    = FormField(right, "Số điện thoại","0xxxxxxxxx", required=True)
        self._f_diachi = FormField(right, "Địa chỉ",     "Tùy chọn")

        for f in [self._f_mssv, self._f_hoten, self._f_ns,
                  self._f_email, self._f_sdt, self._f_diachi]:
            f.pack(fill="x", pady=4)

        # Giới tính
        tk.Label(right, text="Giới tính", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", pady=(4, 0))
        self._gt_var = tk.StringVar(value="Nam")
        gt_frame = tk.Frame(right, bg=BG_CARD)
        gt_frame.pack(anchor="w")
        for g in ("Nam", "Nữ"):
            tk.Radiobutton(gt_frame, text=g, variable=self._gt_var,
                           value=g, font=FONT_SMALL, bg=BG_CARD,
                           fg=TEXT_MAIN, activebackground=BG_CARD).pack(side="left")

        # Lớp
        tk.Label(right, text="Lớp *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", pady=(8, 0))
        self._lop_var = tk.StringVar()
        self._cb_lop  = ttk.Combobox(right, textvariable=self._lop_var,
                                     font=FONT_SMALL, state="readonly")
        self._cb_lop.pack(fill="x", pady=(2, 10))

        # Nút lưu / hủy
        btn_row = tk.Frame(right, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(6, 0))
        AppButton(btn_row, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x",
                                         expand=True, padx=(0, 4))
        AppButton(btn_row, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

        self._cap_nhat_cb_lop()

    # ================================================================== #
    #  DATA
    # ================================================================== #
    def _tai_du_lieu(self, ds=None):
        if ds is None:
            ds = self._sv_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for sv in ds:
            self.table.chen_hang([
                sv.mssv, sv.ho_ten, sv.ngay_sinh,
                sv.gioi_tinh, sv.ma_lop, sv.email, sv.so_dien_thoai,
            ])
        self._lbl_count.config(text=f"Tổng: {len(ds)} sinh viên")
        self._cap_nhat_cb_lop()

    def _cap_nhat_cb_lop(self):
        ma_lops = ["Tất cả"] + sorted({
            lop.ma_lop for lop in self._lop_svc.lay_tat_ca()
        })
        self._loc_lop["values"] = ma_lops
        if not self._loc_lop.get():
            self._loc_lop.current(0)

        ma_lops_form = [lop.ma_lop for lop in self._lop_svc.lay_tat_ca()]
        self._cb_lop["values"] = ma_lops_form
        if ma_lops_form and not self._lop_var.get():
            self._cb_lop.current(0)

    def _tim_kiem(self, tu_khoa=""):
        lop_chon = self._loc_lop.get()
        gt_chon  = self._loc_gt.get()
        ds = self._sv_svc.tim_nang_cao(
            tu_khoa=tu_khoa,
            ma_lop="" if lop_chon == "Tất cả" else lop_chon,
            gioi_tinh="" if gt_chon == "Tất cả" else gt_chon,
        )
        self._tai_du_lieu(ds)

    # ================================================================== #
    #  CRUD
    # ================================================================== #
    def _on_chon_hang(self, _):
        row = self.table.lay_hang_chon()
        if row:
            mssv = row[0]
            sv = self._sv_svc.tim_theo_khoa(mssv)
            if sv:
                self._dien_form(sv)

    def _dien_form(self, sv: SinhVien):
        self._f_mssv.set(sv.mssv)
        self._f_hoten.set(sv.ho_ten)
        self._f_ns.set(sv.ngay_sinh)
        self._f_email.set(sv.email)
        self._f_sdt.set(sv.so_dien_thoai)
        self._f_diachi.set(sv.dia_chi)
        self._gt_var.set(sv.gioi_tinh)
        self._lop_var.set(sv.ma_lop)

    def _xoa_form(self):
        for f in [self._f_mssv, self._f_hoten, self._f_ns,
                  self._f_email, self._f_sdt, self._f_diachi]:
            f.clear()
        self._gt_var.set("Nam")
        if self._cb_lop["values"]:
            self._cb_lop.current(0)

    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Thêm sinh viên")
        self._xoa_form()
        self._f_mssv.entry.config(state="normal")

    def _bat_dau_sua(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sinh viên.")
            return
        self._mode = "edit"
        self._form_title.config(text="Cập nhật sinh viên")
        self._f_mssv.entry.config(state="disabled")

    def _luu(self):
        sv = SinhVien(
            mssv=self._f_mssv.get(),
            ho_ten=self._f_hoten.get(),
            ngay_sinh=self._f_ns.get(),
            gioi_tinh=self._gt_var.get(),
            email=self._f_email.get(),
            so_dien_thoai=self._f_sdt.get(),
            ma_lop=self._lop_var.get(),
            dia_chi=self._f_diachi.get(),
        )
        if self._mode == "add":
            ok, msg = self._sv_svc.them(sv)
            # Đồng bộ thêm vào lớp
            if ok:
                self._lop_svc.them_sv_vao_lop(sv.ma_lop, sv.mssv)
        else:
            ok, msg = self._sv_svc.cap_nhat(sv)

        if ok:
            self._status.ok(msg)
            self._tai_du_lieu()
            self._mode = None
        else:
            self._status.err(msg)

    def _xoa(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sinh viên.")
            return
        mssv = row[0]
        if messagebox.askyesno("Xác nhận", f"Xóa sinh viên {mssv}?"):
            ok, msg = self._sv_svc.xoa(mssv)
            if ok:
                self._lop_svc.xoa_sv_khoi_lop(row[4], mssv)
                self._status.ok(msg)
                self._tai_du_lieu()
                self._xoa_form()
            else:
                self._status.err(msg)

    def _huy(self):
        self._mode = None
        self._xoa_form()
        self._f_mssv.entry.config(state="normal")

    # ================================================================== #
    #  EXPORT / IMPORT
    # ================================================================== #
    def _xuat_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile="sinh_vien.csv")
        if path:
            self._sv_svc.xuat_csv(path)
            self._status.ok(f"Đã xuất CSV: {path}")

    def _xuat_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
            initialfile="sinh_vien.xlsx")
        if path:
            self._sv_svc.xuat_excel(path)
            self._status.ok(f"Đã xuất Excel: {path}")

    def _nhap_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv")])
        if path:
            tc, tb, loi = self._sv_svc.nhap_tu_csv(path)
            self._tai_du_lieu()
            msg = f"Nhập xong: {tc} thành công, {tb} thất bại."
            if loi:
                msg += "\n" + "\n".join(loi[:5])
            messagebox.showinfo("Kết quả nhập", msg)