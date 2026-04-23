# views/nguoi_dung_view.py
import tkinter as tk
from tkinter import messagebox
from views.theme import *
from views.widgets import AppButton, Card, DataTable, HeadingLabel, FormField
from models.nguoi_dung import NguoiDung


class NguoiDungView(tk.Frame):
    COLS = [
        ("tdn",    "Tên đăng nhập", 130, "w"),
        ("hoten",  "Họ tên",        180, "w"),
        ("email",  "Email",         180, "w"),
        ("vaitro", "Vai trò",        80, "center"),
        ("tt",     "Trạng thái",     90, "center"),
    ]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._nd_svc = services["nd"]
        self._status = statusbar
        self._mode   = None
        self._build_ui()
        self._tai_du_lieu()

    def _build_ui(self):
        tk.Label(self, text="Quản lý Tài khoản", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w", pady=(0, 12))
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
        AppButton(btn_row, "Thêm", style="primary", icon=ICON["add"],
                  command=self._bat_dau_them).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Khóa/Mở", style="outline",
                  command=self._doi_trang_thai).pack(side="left", padx=(0, 6))
        AppButton(btn_row, "Xóa", style="danger", icon=ICON["delete"],
                  command=self._xoa).pack(side="left")

    def _build_form(self, parent):
        right = Card(parent, padx=16, pady=16)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=260)
        self._form_title = HeadingLabel(right, "Thêm tài khoản", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(0, 10))
        self._f_tdn   = FormField(right, "Tên đăng nhập", "vd: gv_an",  required=True)
        self._f_hoten = FormField(right, "Họ tên",        "Nguyễn Thị A", required=True)
        self._f_email = FormField(right, "Email",          "gv@school.edu", required=True)
        self._f_mk    = FormField(right, "Mật khẩu",      "Tối thiểu 6 ký tự",
                                  required=True, show="•")
        for f in [self._f_tdn, self._f_hoten, self._f_email, self._f_mk]:
            f.pack(fill="x", pady=4)
        tk.Label(right, text="Vai trò", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", pady=(4, 0))
        self._vt_var = tk.StringVar(value="user")
        vt_frame = tk.Frame(right, bg=BG_CARD)
        vt_frame.pack(anchor="w")
        for v, l in (("admin", "Admin"), ("user", "Giáo viên")):
            tk.Radiobutton(vt_frame, text=l, variable=self._vt_var, value=v,
                           font=FONT_SMALL, bg=BG_CARD).pack(side="left")
        btn_row = tk.Frame(right, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(12, 0))
        AppButton(btn_row, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x", expand=True, padx=(0, 4))
        AppButton(btn_row, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    def _tai_du_lieu(self):
        ds = self._nd_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for nd in ds:
            self.table.chen_hang([
                nd.ten_dang_nhap, nd.ho_ten, nd.email,
                nd.vai_tro, "✓ Hoạt động" if nd.kich_hoat else "✗ Bị khóa",
            ])

    def _on_chon_hang(self, _):
        row = self.table.lay_hang_chon()
        if not row:
            return
        nd = self._nd_svc.tim_theo_khoa(row[0])
        if nd:
            self._f_tdn.set(nd.ten_dang_nhap)
            self._f_hoten.set(nd.ho_ten)
            self._f_email.set(nd.email)
            self._vt_var.set(nd.vai_tro)

    def _bat_dau_them(self):
        self._mode = "add"
        self._form_title.config(text="Thêm tài khoản")
        for f in [self._f_tdn, self._f_hoten, self._f_email, self._f_mk]:
            f.clear()
        self._f_tdn.entry.config(state="normal")

    def _luu(self):
        nd = NguoiDung.tao_tai_khoan(
            ten_dang_nhap=self._f_tdn.get(),
            mat_khau=self._f_mk.get(),
            ho_ten=self._f_hoten.get(),
            email=self._f_email.get(),
            vai_tro=self._vt_var.get(),
        )
        ok, msg = self._nd_svc.them(nd)
        if ok:
            self._status.ok(msg)
            self._tai_du_lieu()
            self._mode = None
        else:
            self._status.err(msg)

    def _doi_trang_thai(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một tài khoản.")
            return
        nd = self._nd_svc.tim_theo_khoa(row[0])
        if nd:
            if nd.kich_hoat:
                ok, msg = self._nd_svc.khoa_tai_khoan(nd.ten_dang_nhap)
            else:
                ok, msg = self._nd_svc.mo_khoa_tai_khoan(nd.ten_dang_nhap)
            if ok:
                self._status.ok(msg)
                self._tai_du_lieu()
            else:
                self._status.err(msg)

    def _xoa(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một tài khoản.")
            return
        if messagebox.askyesno("Xác nhận", f"Xóa tài khoản '{row[0]}'?"):
            ok, msg = self._nd_svc.xoa(row[0])
            if ok:
                self._status.ok(msg)
                self._tai_du_lieu()
            else:
                self._status.err(msg)

    def _huy(self):
        self._mode = None