"""
views/lop_hoc_view.py  —  Nâng cấp toàn diện module Lớp học
Chức năng:
  - CRUD lớp học (thêm/sửa/xóa + các trường mới: học kỳ, năm học, tín chỉ, trạng thái, ngày)
  - Quản lý sinh viên trong lớp (thêm/xóa SV, tìm kiếm SV để thêm)
  - Xem danh sách SV của lớp
  - Tìm kiếm/lọc lớp theo mã, tên môn, giảng viên, học kỳ, trạng thái
  - Thông tin tổng quan lớp (sĩ số, tỷ lệ, trạng thái)
"""
import tkinter as tk
from tkinter import messagebox, ttk
from views.theme import *
from views.widgets import AppButton, Card, DataTable, SearchBar, HeadingLabel, FormField
from models.lop_hoc import (LopHoc, BuoiHoc, THU_LIST,
                            lay_tiet_list, lay_gio,
                            TRANG_THAI_LIST, TRANG_THAI_COLOR)


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

    def _on_loai_thay_doi(self, *_):
        loai = self._loai_var.get()
        tiet_list = lay_tiet_list(loai)
        for r in self._rows:
            cb: ttk.Combobox = r["cb_tiet"]
            tiet_cu = r["tiet_var"].get()
            cb["values"] = tiet_list
            if tiet_cu not in tiet_list:
                r["tiet_var"].set(tiet_list[0] if tiet_list else "")
            self._cap_nhat_gio(r)

    def _cap_nhat_gio(self, r: dict):
        loai = self._loai_var.get()
        tiet = r["tiet_var"].get()
        r["lbl_gio"].config(text=lay_gio(loai, tiet))

    def them_hang(self, thu="Thứ 2", tiet="", phong=""):
        loai = self._loai_var.get()
        tiet_list = lay_tiet_list(loai)
        if tiet not in tiet_list:
            tiet = tiet_list[0] if tiet_list else ""

        row_frame = tk.Frame(self._list_frame, bg=self._bg, pady=3)
        row_frame.pack(fill="x")

        thu_var = tk.StringVar(value=thu)
        tiet_var = tk.StringVar(value=tiet)
        phong_var = tk.StringVar(value=phong)

        cb_thu = ttk.Combobox(row_frame, textvariable=thu_var,
                              values=THU_LIST, state="readonly",
                              width=9, font=FONT_SMALL)
        cb_thu.pack(side="left", padx=(0, 4))

        cb_tiet = ttk.Combobox(row_frame, textvariable=tiet_var,
                               values=tiet_list, state="readonly",
                               width=11, font=FONT_SMALL)
        cb_tiet.pack(side="left", padx=(0, 4))

        lbl_gio = tk.Label(row_frame, text=lay_gio(loai, tiet),
                           font=FONT_SMALL, fg=TEXT_MUTED,
                           bg=self._bg, width=16, anchor="w")
        lbl_gio.pack(side="left", padx=(0, 4))

        tk.Label(row_frame, text="Phòng", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=self._bg).pack(side="left")
        ent_phong = tk.Entry(row_frame, textvariable=phong_var,
                             font=FONT_SMALL, width=7,
                             relief="solid", bd=1)
        ent_phong.pack(side="left", padx=(3, 6))

        row_data = {
            "frame": row_frame, "thu_var": thu_var,
            "tiet_var": tiet_var, "phong_var": phong_var,
            "cb_tiet": cb_tiet, "lbl_gio": lbl_gio,
        }

        def _on_tiet_change(*_, r=row_data):
            self._cap_nhat_gio(r)

        tiet_var.trace_add("write", _on_tiet_change)

        tk.Button(row_frame, text="✕", font=FONT_SMALL,
                  fg=DANGER, bg=self._bg, relief="flat", cursor="hand2",
                  command=lambda r=row_data: self._xoa_hang(r)).pack(side="left")

        self._rows.append(row_data)

    def _xoa_hang(self, row_data: dict):
        row_data["frame"].destroy()
        self._rows.remove(row_data)

    def lay_buoi_hoc(self) -> list[BuoiHoc]:
        loai = self._loai_var.get()
        return [BuoiHoc(thu=r["thu_var"].get(), tiet=r["tiet_var"].get(),
                        gio=lay_gio(loai, r["tiet_var"].get()),
                        phong=r["phong_var"].get().strip())
                for r in self._rows]

    def set_buoi_hoc(self, buoi_list: list[BuoiHoc]):
        self.xoa_tat_ca()
        for b in buoi_list:
            self.them_hang(b.thu, b.tiet, b.phong)

    def xoa_tat_ca(self):
        for r in list(self._rows):
            r["frame"].destroy()
        self._rows.clear()

    def set_state(self, enabled: bool):
        state_cb = "readonly" if enabled else "disabled"
        state_ent = "normal" if enabled else "disabled"
        state_btn = "normal" if enabled else "disabled"
        for r in self._rows:
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


# Quản lý Sinh viên trong lớp

class QuanLySinhVienPopup(tk.Toplevel):

    COLS_DS = [
        ("stt", "STT", 45, "center"),
        ("mssv", "MSSV", 90, "center"),
        ("hoten", "Họ và tên", 200, "w"),
        ("gt", "Giới tính", 75, "center"),
        ("ns", "Ngày sinh", 95, "center"),
        ("email", "Email", 190, "w"),
    ]
    COLS_TIM = [
        ("mssv", "MSSV", 90, "center"),
        ("hoten", "Họ và tên", 200, "w"),
        ("lop", "Lớp HL", 80, "center"),
        ("gt", "Giới tính", 75, "center"),
    ]

    def __init__(self, parent, lop: LopHoc, services: dict, on_save=None):
        super().__init__(parent)
        self._lop = lop
        self._svcs = services
        self._on_save = on_save

        self.title(f"Quản lý Sinh viên — {lop.ma_lop}: {lop.ten_mon}")
        self.configure(bg=BG_APP)
        w, h = 1050, 680
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.grab_set()
        self.resizable(True, True)

        self._build_ui()
        self._tai_ds_sv()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_SIDEBAR, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text=f"👥  {self._lop.ma_lop} — {self._lop.ten_mon}",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE, padx=16).pack(side="left", fill="y")

        # Thông tin tóm tắt
        info_txt = (f"GV: {self._lop.giang_vien}  |  "
                    f"Sĩ số: {self._lop.si_so_hien_tai}/{self._lop.si_so_toi_da}  |  "
                    f"Còn chỗ: {self._lop.con_cho}")
        self._lbl_info_hdr = tk.Label(hdr, text=info_txt,
                                      font=FONT_SMALL, bg=BG_SIDEBAR, fg="#90CAF9",
                                      padx=16)
        self._lbl_info_hdr.pack(side="right", fill="y")

        # notebook 2 tab
        nb_style = ttk.Style()
        nb_style.configure("Popup.TNotebook", background=BG_APP, borderwidth=0)
        nb_style.configure("Popup.TNotebook.Tab", font=FONT_BOLD, padding=(16, 8))

        self._nb = ttk.Notebook(self, style="Popup.TNotebook")
        self._nb.pack(fill="both", expand=True, padx=PAD, pady=(PAD, 0))

        self._tab_ds = tk.Frame(self._nb, bg=BG_APP)
        self._tab_them = tk.Frame(self._nb, bg=BG_APP)
        self._nb.add(self._tab_ds, text="📋  Danh sách sinh viên")
        self._nb.add(self._tab_them, text="➕  Thêm sinh viên vào lớp")

        self._build_tab_ds()
        self._build_tab_them()

        # Statusbar popup
        self._status_lbl = tk.Label(self, text="", font=FONT_SMALL,
                                    bg=BG_SIDEBAR, fg="#A5D6A7",
                                    padx=12, anchor="w", height=2)
        self._status_lbl.pack(fill="x", side="bottom")

    # Tab 1: Danh sách SV trong lớp
    def _build_tab_ds(self):
        p = self._tab_ds

        bar = tk.Frame(p, bg=BG_APP)
        bar.pack(fill="x", pady=(8, 6))

        self._search_ds = SearchBar(bar, placeholder="Tìm trong danh sách...",
                                    on_search=self._loc_ds)
        self._search_ds.pack(side="left", fill="x", expand=True, padx=(0, 8))

        AppButton(bar, "🗑  Xóa khỏi lớp", style="danger",
                  command=self._xoa_sv_khoi_lop).pack(side="right")

        self._lbl_stat = tk.Label(p, text="", font=FONT_SMALL,
                                  fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_stat.pack(anchor="w", pady=(0, 4))

        tbl_f = tk.Frame(p, bg=BG_APP)
        tbl_f.pack(fill="both", expand=True)
        self._tbl_ds = DataTable(tbl_f, columns=self.COLS_DS, height=18)
        sb = DataTable.them_scrollbar(tbl_f, self._tbl_ds)
        self._tbl_ds.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _tai_ds_sv(self):
        self._tbl_ds.xoa_tat_ca()
        sv_svc = self._svcs["sv"]
        ds = []
        for mssv in self._lop.danh_sach_mssv:
            sv = sv_svc.tim_theo_khoa(mssv)
            ds.append(sv)

        # Lọc nếu có từ khóa
        tu_khoa = self._search_ds.get().lower() if hasattr(self, "_search_ds") else ""

        for i, sv in enumerate(ds):
            if sv is None:
                continue
            if tu_khoa and tu_khoa not in sv.ho_ten.lower() and tu_khoa not in sv.mssv.lower():
                continue
            self._tbl_ds.chen_hang([
                i + 1, sv.mssv, sv.ho_ten,
                sv.gioi_tinh, sv.ngay_sinh, sv.email,
            ])

        total = len([s for s in ds if s])
        self._lbl_stat.config(text=f"Tổng: {total} sinh viên trong lớp")
        self._cap_nhat_header()

    def _loc_ds(self, tu_khoa=""):
        self._tai_ds_sv()

    def _xoa_sv_khoi_lop(self):
        row = self._tbl_ds.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sinh viên.", parent=self)
            return
        mssv = row[1]
        ten = row[2]
        if not messagebox.askyesno("Xác nhận",
                                   f"Xóa sinh viên {mssv} — {ten} khỏi lớp {self._lop.ma_lop}?",
                                   parent=self):
            return
        ok, msg = self._svcs["lop"].xoa_sv_khoi_lop(self._lop.ma_lop, mssv)
        if ok:
            # Cập nhật lại object lớp
            self._lop = self._svcs["lop"].tim_theo_khoa(self._lop.ma_lop)
            self._tai_ds_sv()
            self._set_status(f"✓ Đã xóa {mssv} khỏi lớp.", "#A5D6A7")
            if self._on_save:
                self._on_save()
        else:
            self._set_status(f"✕ {msg}", "#EF9A9A")

    # Tab 2: Thêm SV vào lớp
    def _build_tab_them(self):
        p = self._tab_them

        guide = tk.Label(p,
                         text="Tìm kiếm sinh viên chưa có trong lớp → Chọn một hoặc nhiều → Nhấn 'Thêm vào lớp'",
                         font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP)
        guide.pack(anchor="w", pady=(8, 4))

        bar = tk.Frame(p, bg=BG_APP)
        bar.pack(fill="x", pady=(0, 6))

        self._search_them = SearchBar(bar, placeholder="Tìm theo MSSV hoặc họ tên...",
                                      on_search=self._tim_sv)
        self._search_them.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Lọc giới tính
        tk.Label(bar, text="Giới tính:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(side="left")
        self._gt_var = tk.StringVar(value="Tất cả")
        cb_gt = ttk.Combobox(bar, textvariable=self._gt_var,
                             values=["Tất cả", "Nam", "Nữ"],
                             state="readonly", width=7, font=FONT_SMALL)
        cb_gt.pack(side="left", padx=(4, 8))
        cb_gt.bind("<<ComboboxSelected>>", lambda e: self._tim_sv())

        AppButton(bar, "➕  Thêm vào lớp", style="primary",
                  command=self._them_sv_vao_lop).pack(side="right")

        self._lbl_them_stat = tk.Label(p, text="", font=FONT_SMALL,
                                       fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_them_stat.pack(anchor="w", pady=(0, 4))

        tbl_f = tk.Frame(p, bg=BG_APP)
        tbl_f.pack(fill="both", expand=True)
        self._tbl_tim = DataTable(tbl_f, columns=self.COLS_TIM, height=18,
                                  selectmode="extended")
        sb = DataTable.them_scrollbar(tbl_f, self._tbl_tim)
        self._tbl_tim.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Load ngay
        self._tim_sv()

    def _tim_sv(self, tu_khoa=""):
        tu_khoa = self._search_them.get() if hasattr(self, "_search_them") else ""
        gt = self._gt_var.get() if hasattr(self, "_gt_var") else "Tất cả"

        ds_trong_lop = set(self._lop.danh_sach_mssv)
        tat_ca = self._svcs["sv"].tim_nang_cao(
            tu_khoa=tu_khoa,
            gioi_tinh="" if gt == "Tất cả" else gt,
        )
        # Loại những SV đã có trong lớp
        chua_co = [sv for sv in tat_ca if sv.mssv not in ds_trong_lop]

        self._tbl_tim.xoa_tat_ca()
        for sv in chua_co:
            self._tbl_tim.chen_hang([sv.mssv, sv.ho_ten, sv.ma_lop, sv.gioi_tinh])

        self._lbl_them_stat.config(
            text=f"Tìm thấy {len(chua_co)} sinh viên chưa có trong lớp "
                 f"(Ctrl+Click để chọn nhiều)")

    def _them_sv_vao_lop(self):
        sel = self._tbl_tim.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn ít nhất một sinh viên.", parent=self)
            return

        # Kiểm tra còn chỗ
        so_chon = len(sel)
        if so_chon > self._lop.con_cho:
            messagebox.showwarning(
                "Lớp sắp đầy",
                f"Lớp chỉ còn {self._lop.con_cho} chỗ, bạn đang chọn {so_chon} sinh viên.",
                parent=self)
            return

        thanh_cong = 0
        loi_list = []
        for item_id in sel:
            values = self._tbl_tim.item(item_id, "values")
            mssv = values[0]
            ok, msg = self._svcs["lop"].them_sv_vao_lop(self._lop.ma_lop, mssv)
            if ok:
                thanh_cong += 1
            else:
                loi_list.append(f"{mssv}: {msg}")

        # Cập nhật lại lop object
        self._lop = self._svcs["lop"].tim_theo_khoa(self._lop.ma_lop)

        msg_out = f"✓ Đã thêm {thanh_cong} sinh viên vào lớp."
        if loi_list:
            msg_out += f"  ({len(loi_list)} lỗi)"
        self._set_status(msg_out, "#A5D6A7")

        # Refresh cả 2 tab
        self._tai_ds_sv()
        self._tim_sv()
        if self._on_save:
            self._on_save()

    def _cap_nhat_header(self):
        info_txt = (f"GV: {self._lop.giang_vien}  |  "
                    f"Sĩ số: {self._lop.si_so_hien_tai}/{self._lop.si_so_toi_da}  |  "
                    f"Còn chỗ: {self._lop.con_cho}")
        self._lbl_info_hdr.config(text=info_txt)

    def _set_status(self, msg, color="#A5D6A7"):
        self._status_lbl.config(text=f"  {msg}", fg=color)
        self.after(5000, lambda: self._status_lbl.config(text=""))


# LopHocView
class LopHocView(tk.Frame):
    COLS = [
        ("ma_lop", "Mã lớp", 90, "center"),
        ("ten_mon", "Tên môn", 180, "w"),
        ("ma_mon", "Mã môn", 75, "center"),
        ("loai", "Loại hình", 90, "center"),
        ("gv", "Giảng viên", 155, "w"),
        ("hk", "Học kỳ", 60, "center"),
        ("tc", "Tín chỉ", 55, "center"),
        ("si_so", "Sĩ số", 75, "center"),
        ("tt", "Trạng thái", 110, "center"),
        ("lich", "Lịch học", 200, "w"),
    ]

    LOAI_HINH = ["Lý thuyết", "Thực hành", "Online"]
    HOC_KY = ["1", "2", "Hè"]
    NAM_HOC = ["2023-2024", "2024-2025", "2025-2026", "2026-2027"]
    TIN_CHI = ["1", "2", "3", "4", "5"]

    def __init__(self, parent, services, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._lop_svc = services["lop"]
        self._sv_svc = services["sv"]
        self._svcs = services
        self._status = statusbar
        self._mode = None
        self._loai_var = tk.StringVar(value="Lý thuyết")
        self._tt_var = tk.StringVar(value="Đang học")
        self._build_ui()
        self._tai_du_lieu()
        self._khoa_form()

    # Layout chính
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="Quản lý Lớp học", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")

        # Thanh lọc
        filter_bar = tk.Frame(self, bg=BG_APP)
        filter_bar.pack(fill="x", pady=(0, 6))

        SearchBar(filter_bar, placeholder="Tìm theo mã lớp, tên môn, giảng viên...",
                  on_search=self._tim_kiem).pack(side="left", fill="x",
                                                 expand=True, padx=(0, 8))

        # Lọc học kỳ
        tk.Label(filter_bar, text="HK:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(side="left")
        self._loc_hk = ttk.Combobox(filter_bar, width=5, state="readonly",
                                    font=FONT_SMALL,
                                    values=["Tất cả"] + self.HOC_KY)
        self._loc_hk.current(0)
        self._loc_hk.pack(side="left", padx=(3, 8))
        self._loc_hk.bind("<<ComboboxSelected>>", lambda e: self._tim_kiem())

        # Lọc trạng thái
        tk.Label(filter_bar, text="Trạng thái:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(side="left")
        self._loc_tt = ttk.Combobox(filter_bar, width=14, state="readonly",
                                    font=FONT_SMALL,
                                    values=["Tất cả"] + TRANG_THAI_LIST)
        self._loc_tt.current(0)
        self._loc_tt.pack(side="left", padx=(3, 8))
        self._loc_tt.bind("<<ComboboxSelected>>", lambda e: self._tim_kiem())

        # Lọc loại hình
        tk.Label(filter_bar, text="Loại:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(side="left")
        self._loc_loai = ttk.Combobox(filter_bar, width=10, state="readonly",
                                      font=FONT_SMALL,
                                      values=["Tất cả"] + self.LOAI_HINH)
        self._loc_loai.current(0)
        self._loc_loai.pack(side="left", padx=(3, 0))
        self._loc_loai.bind("<<ComboboxSelected>>", lambda e: self._tim_kiem())

        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)
        self._build_table(main)
        self._build_form(main)

    # Bảng danh sách lớp
    def _build_table(self, parent):
        left = tk.Frame(parent, bg=BG_APP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tbl_frame = tk.Frame(left, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)
        self.table = DataTable(tbl_frame, columns=self.COLS, height=17)
        sb = DataTable.them_scrollbar(tbl_frame, self.table)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self._on_chon_hang)

        btn_row = tk.Frame(left, bg=BG_APP)
        btn_row.pack(fill="x", pady=(8, 0))
        AppButton(btn_row, "Thêm mới", style="primary", icon=ICON["add"],
                  command=self._bat_dau_them).pack(side="left", padx=(0, 5))
        AppButton(btn_row, "Sửa", style="outline", icon=ICON["edit"],
                  command=self._bat_dau_sua).pack(side="left", padx=(0, 5))
        AppButton(btn_row, "Xóa", style="danger", icon=ICON["delete"],
                  command=self._xoa).pack(side="left", padx=(0, 5))
        AppButton(btn_row, "👥 Quản lý SV", style="outline",
                  command=self._mo_popup_sv).pack(side="left", padx=(0, 5))
        AppButton(btn_row, "Làm mới", style="ghost", icon=ICON["refresh"],
                  command=self._tai_du_lieu).pack(side="right")
        self._lbl_count = tk.Label(btn_row, text="", font=FONT_SMALL,
                                   fg=TEXT_MUTED, bg=BG_APP)
        self._lbl_count.pack(side="right", padx=8)

    # Form bên phải
    def _build_form(self, parent):
        right = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        right.config(width=440)

        # Canvas cuộn
        canvas = tk.Canvas(right, bg=BG_CARD, bd=0,
                           highlightthickness=0, width=420)
        vscroll = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

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
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        pad = {"fill": "x", "pady": 3, "padx": 16}

        self._form_title = HeadingLabel(inner, "Thêm lớp học", bg=BG_CARD)
        self._form_title.pack(anchor="w", pady=(12, 8), padx=16)

        # Nhóm 1: Thông tin cơ bản
        self._section(inner, "📋  Thông tin cơ bản")

        self._f_malop = FormField(inner, "Mã lớp *", "VD: CNTT01", required=True)
        self._f_tenmon = FormField(inner, "Tên môn *", "Lập trình Python", required=True)
        self._f_mamon = FormField(inner, "Mã môn *", "VD: IT001", required=True)
        self._f_gv = FormField(inner, "Giảng viên *", "Nguyễn Văn A", required=True)
        self._f_siso = FormField(inner, "Sĩ số tối đa", "50")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.pack(**pad)

        # Nhóm 2: Học kỳ / Năm học / Tín chỉ
        self._section(inner, "📅  Học vụ")

        row_hk = tk.Frame(inner, bg=BG_CARD)
        row_hk.pack(fill="x", padx=16, pady=3)

        # Học kỳ
        col1 = tk.Frame(row_hk, bg=BG_CARD)
        col1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(col1, text="Học kỳ *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._hk_var = tk.StringVar(value="1")
        self._cb_hk = ttk.Combobox(col1, textvariable=self._hk_var,
                                   values=self.HOC_KY, state="readonly",
                                   font=FONT_NORMAL, width=6)
        self._cb_hk.pack(fill="x", pady=(2, 0))

        # Năm học
        col2 = tk.Frame(row_hk, bg=BG_CARD)
        col2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(col2, text="Năm học *", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._nh_var = tk.StringVar(value="2024-2025")
        self._cb_nh = ttk.Combobox(col2, textvariable=self._nh_var,
                                   values=self.NAM_HOC, font=FONT_NORMAL, width=11)
        self._cb_nh.pack(fill="x", pady=(2, 0))

        # Tín chỉ
        col3 = tk.Frame(row_hk, bg=BG_CARD)
        col3.pack(side="left", fill="x", expand=True)
        tk.Label(col3, text="Số tín chỉ", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._tc_var = tk.StringVar(value="3")
        self._cb_tc = ttk.Combobox(col3, textvariable=self._tc_var,
                                   values=self.TIN_CHI, state="readonly",
                                   font=FONT_NORMAL, width=5)
        self._cb_tc.pack(fill="x", pady=(2, 0))

        # Ngày bắt đầu / kết thúc
        row_ng = tk.Frame(inner, bg=BG_CARD)
        row_ng.pack(fill="x", padx=16, pady=3)

        col_bd = tk.Frame(row_ng, bg=BG_CARD)
        col_bd.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(col_bd, text="Ngày bắt đầu", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._f_ngay_bd = tk.Entry(col_bd, font=FONT_NORMAL,
                                   relief="solid", bd=1)
        self._f_ngay_bd.pack(fill="x", pady=(2, 0), ipady=4)

        col_kt = tk.Frame(row_ng, bg=BG_CARD)
        col_kt.pack(side="left", fill="x", expand=True)
        tk.Label(col_kt, text="Ngày kết thúc", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        self._f_ngay_kt = tk.Entry(col_kt, font=FONT_NORMAL,
                                   relief="solid", bd=1)
        self._f_ngay_kt.pack(fill="x", pady=(2, 0), ipady=4)

        # Nhóm 3: Trạng thái
        self._section(inner, "🏷  Trạng thái lớp")

        tt_frame = tk.Frame(inner, bg=BG_CARD)
        tt_frame.pack(fill="x", padx=16, pady=(4, 8))
        self._tt_btns: dict[str, tk.Button] = {}
        for tt in TRANG_THAI_LIST:
            color = TRANG_THAI_COLOR[tt]
            btn = tk.Button(
                tt_frame, text=tt, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=5,
                command=lambda t=tt: self._chon_trang_thai(t)
            )
            btn.pack(side="left", padx=(0, 6))
            self._tt_btns[tt] = btn
        self._chon_trang_thai("Đang học")

        # Nhóm 4: Loại hình
        self._section(inner, "🎓  Loại hình học")

        loai_frame = tk.Frame(inner, bg=BG_CARD)
        loai_frame.pack(anchor="w", padx=16, pady=(4, 0))
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

        self._lbl_loai_hint = tk.Label(inner,
                                       text="(Lý thuyết: 3 tiết/buổi)",
                                       font=FONT_SMALL, fg=PRIMARY, bg=BG_CARD)
        self._lbl_loai_hint.pack(anchor="w", padx=16, pady=(2, 0))

        # Nhóm 5: Lịch học
        self._section(inner, "📆  Lịch học trong tuần")

        col_hdr = tk.Frame(inner, bg=BG_CARD)
        col_hdr.pack(fill="x", padx=16, pady=(0, 2))
        for text, w in [("Thứ", 75), ("Tiết học", 90), ("Giờ học", 120), ("Phòng", 60)]:
            tk.Label(col_hdr, text=text, font=FONT_SMALL, fg=TEXT_MUTED,
                     bg=BG_CARD, width=w // 7, anchor="w").pack(side="left", padx=2)

        self._lich_picker = LichHocPicker(inner,
                                          loai_hinh_var=self._loai_var,
                                          bg=BG_CARD)
        self._lich_picker.pack(fill="x", padx=16, pady=(0, 12))

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 8))

        # Nút Lưu / Hủy
        AppButton(btn_outer, "Lưu", style="primary", icon=ICON["save"],
                  command=self._luu).pack(side="left", fill="x",
                                          expand=True, padx=(0, 6))
        AppButton(btn_outer, "Hủy", style="ghost",
                  command=self._huy).pack(side="left", fill="x", expand=True)

    def _section(self, parent, title: str):
        """Tiêu đề phân đoạn trong form."""
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(f, text=title, font=FONT_BOLD, fg=PRIMARY,
                 bg=BG_CARD).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x",
                                              expand=True, padx=(8, 0), pady=6)

    # Trạng thái và loại hình
    def _chon_trang_thai(self, tt: str):
        self._tt_var.set(tt)
        color = TRANG_THAI_COLOR.get(tt, PRIMARY)
        for t, btn in self._tt_btns.items():
            if t == tt:
                btn.config(bg=color, fg=TEXT_WHITE)
            else:
                btn.config(bg=BORDER, fg=TEXT_MAIN)

    def _chon_loai(self, loai: str):
        self._loai_var.set(loai)
        self._cap_nhat_loai_btn(loai)
        hints = {
            "Lý thuyết": "(Lý thuyết: 3 tiết/buổi)",
            "Thực hành": "(Thực hành: 5 tiết/buổi)",
            "Online": "(Online: 3 tiết/buổi)",
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
        self._f_ngay_bd.config(state="disabled")
        self._f_ngay_kt.config(state="disabled")
        self._cb_hk.config(state="disabled")
        self._cb_nh.config(state="disabled")
        self._cb_tc.config(state="disabled")
        self._lich_picker.set_state(False)
        for btn in self._loai_btns.values():
            btn.config(state="disabled", cursor="arrow")
        for btn in self._tt_btns.values():
            btn.config(state="disabled", cursor="arrow")

    def _mo_form(self, khoa_malop=False):
        for f in [self._f_tenmon, self._f_mamon, self._f_gv, self._f_siso]:
            f.enable()
        if khoa_malop:
            self._f_malop.disable()
        else:
            self._f_malop.enable()
        self._f_ngay_bd.config(state="normal")
        self._f_ngay_kt.config(state="normal")
        self._cb_hk.config(state="readonly")
        self._cb_nh.config(state="normal")
        self._cb_tc.config(state="readonly")
        self._lich_picker.set_state(True)
        for btn in self._loai_btns.values():
            btn.config(state="normal", cursor="hand2")
        for btn in self._tt_btns.values():
            btn.config(state="normal", cursor="hand2")

    # Dữ liệu
    def _tai_du_lieu(self, ds=None):
        if ds is None:
            ds = self._lop_svc.lay_tat_ca()
        self.table.xoa_tat_ca()
        for lop in ds:
            tt_color = TRANG_THAI_COLOR.get(getattr(lop, "trang_thai", "Đang học"), "#333")
            self.table.chen_hang([
                lop.ma_lop, lop.ten_mon, lop.ma_mon,
                getattr(lop, "loai_hinh", "Lý thuyết"),
                lop.giang_vien,
                getattr(lop, "hoc_ky", "1"),
                getattr(lop, "so_tin_chi", "3"),
                f"{lop.si_so_hien_tai}/{lop.si_so_toi_da}",
                getattr(lop, "trang_thai", "Đang học"),
                lop.lich_hoc_str,
            ])
        self._lbl_count.config(text=f"Tổng: {len(ds)} lớp")

    def _tim_kiem(self, tu_khoa=""):
        from views.widgets import SearchBar as SB
        # Lấy từ khóa từ thanh search
        hk_chon = self._loc_hk.get()
        tt_chon = self._loc_tt.get()
        loai_chon = self._loc_loai.get()

        ds = self._lop_svc.lay_tat_ca()

        if tu_khoa:
            kw = tu_khoa.lower()
            ds = [l for l in ds if
                  kw in l.ma_lop.lower() or
                  kw in l.ten_mon.lower() or
                  kw in l.giang_vien.lower() or
                  kw in getattr(l, "ma_mon", "").lower()]

        if hk_chon != "Tất cả":
            ds = [l for l in ds if getattr(l, "hoc_ky", "") == hk_chon]
        if tt_chon != "Tất cả":
            ds = [l for l in ds if getattr(l, "trang_thai", "") == tt_chon]
        if loai_chon != "Tất cả":
            ds = [l for l in ds if getattr(l, "loai_hinh", "") == loai_chon]

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

        self._hk_var.set(getattr(lop, "hoc_ky", "1"))
        self._nh_var.set(getattr(lop, "nam_hoc", "2024-2025"))
        self._tc_var.set(str(getattr(lop, "so_tin_chi", 3)))

        ngay_bd = getattr(lop, "ngay_bat_dau", "")
        ngay_kt = getattr(lop, "ngay_ket_thuc", "")
        self._f_ngay_bd.config(state="normal")
        self._f_ngay_kt.config(state="normal")
        self._f_ngay_bd.delete(0, "end")
        self._f_ngay_bd.insert(0, ngay_bd)
        self._f_ngay_kt.delete(0, "end")
        self._f_ngay_kt.insert(0, ngay_kt)
        self._f_ngay_bd.config(state="disabled")
        self._f_ngay_kt.config(state="disabled")

        self._chon_trang_thai(getattr(lop, "trang_thai", "Đang học"))
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
        self._hk_var.set("1")
        self._nh_var.set("2024-2025")
        self._tc_var.set("3")
        self._f_ngay_bd.config(state="normal")
        self._f_ngay_kt.config(state="normal")
        self._f_ngay_bd.delete(0, "end")
        self._f_ngay_kt.delete(0, "end")
        self._chon_trang_thai("Đang học")
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
            self._status.info("Vui lòng bấm 'Thêm mới' hoặc chọn lớp rồi 'Sửa'.")
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

        try:
            tc = int(self._tc_var.get() or 3)
        except ValueError:
            tc = 3

        lop = LopHoc(
            ma_lop=self._f_malop.get().strip(),
            ten_mon=self._f_tenmon.get().strip(),
            ma_mon=self._f_mamon.get().strip(),
            giang_vien=self._f_gv.get().strip(),
            si_so_toi_da=siso,
            loai_hinh=self._loai_var.get(),
            hoc_ky=self._hk_var.get(),
            nam_hoc=self._nh_var.get().strip(),
            so_tin_chi=tc,
            ngay_bat_dau=self._f_ngay_bd.get().strip(),
            ngay_ket_thuc=self._f_ngay_kt.get().strip(),
            trang_thai=self._tt_var.get(),
        )
        lop.lich_hoc = buoi_list

        if self._mode == "edit":
            lop_cu = self._lop_svc.tim_theo_khoa(lop.ma_lop)
            if lop_cu:
                lop.danh_sach_mssv = lop_cu.danh_sach_mssv

        ok, msg = (self._lop_svc.them(lop) if self._mode == "add"
                   else self._lop_svc.cap_nhat(lop))

        if ok:
            self._status.ok("Lưu lớp học thành công!")
            self._tai_du_lieu()
            self._huy()
        else:
            self._status.err(msg or "Lưu thất bại")

    def _xoa(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một lớp.")
            return
        ma_lop = row[0]
        lop = self._lop_svc.tim_theo_khoa(ma_lop)
        si_so = lop.si_so_hien_tai if lop else 0
        canh_bao = f"\n⚠️  Lớp đang có {si_so} sinh viên!" if si_so > 0 else ""
        if messagebox.askyesno("Xác nhận xóa",
                               f"Bạn có chắc muốn xóa lớp {ma_lop}?{canh_bao}"):
            ok, msg = self._lop_svc.xoa(ma_lop)
            if ok:
                self._status.ok(msg)
                self._tai_du_lieu()
            else:
                self._status.err(msg)

    def _huy(self):
        self._mode = None
        self._form_title.config(text="Thông tin lớp học")
        for f in [self._f_malop, self._f_tenmon, self._f_mamon,
                  self._f_gv, self._f_siso]:
            f.clear()
        self._lich_picker.xoa_tat_ca()
        self._chon_loai("Lý thuyết")
        self._chon_trang_thai("Đang học")
        self._khoa_form()

    # Popup quản lý SV
    def _mo_popup_sv(self):
        row = self.table.lay_hang_chon()
        if not row:
            messagebox.showwarning("Chưa chọn",
                                   "Vui lòng chọn một lớp để quản lý sinh viên.")
            return
        lop = self._lop_svc.tim_theo_khoa(row[0])
        if not lop:
            self._status.err("Không tìm thấy lớp.")
            return

        def _on_save():
            self._tai_du_lieu()
            self._status.ok(f"Đã cập nhật danh sách SV lớp {lop.ma_lop}.")

        QuanLySinhVienPopup(self, lop, self._svcs, on_save=_on_save)
