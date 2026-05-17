import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from views.theme import *
from views.widgets import (AppButton, Card, DataTable, HeadingLabel,
                           MutedLabel, FormField, StatusBar)
from models.diem_danh import TRANG_THAI_LIST, TRANG_THAI_ICON, TRANG_THAI_COLOR
from models.diem_danh import DiemDanh
from models.diem_so import DiemSo

# Helper: lấy thứ hiện tại dạng "Thứ 2" ... "Chủ nhật"

_WEEKDAY_MAP = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5",
                4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}


def _thu_hom_nay() -> str:
    return _WEEKDAY_MAP[date.today().weekday()]


def _ngay_hom_nay() -> str:
    return date.today().strftime("%d/%m/%Y")


class GiaoVienView(tk.Frame):

    def __init__(self, parent, services: dict, nguoi_dung, statusbar):
        super().__init__(parent, bg=BG_APP)
        self._svcs = services
        self._nd = nguoi_dung
        self._status = statusbar

        self._lop_cua_toi = self._lay_lop_cua_toi()

        self._build_ui()

    # Lấy lớp GV đang dạy
    def _lay_lop_cua_toi(self):
        all_lop = self._svcs["lop"].lay_tat_ca()
        ten_gv = self._nd.ho_ten.strip().lower()
        return [lop for lop in all_lop
                if lop.giang_vien.strip().lower() == ten_gv]

    def _build_ui(self):
        # Tiêu đề
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text=f"👋  Xin chào, {self._nd.ho_ten}",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        MutedLabel(hdr, f"Bạn đang dạy {len(self._lop_cua_toi)} lớp",
                   bg=BG_APP).pack(side="left", padx=12, pady=(6, 0))

        # Notebook tabs
        style = ttk.Style()
        style.configure("TNotebook", background=BG_APP, borderwidth=0)
        style.configure("TNotebook.Tab", font=FONT_BOLD, padding=(16, 8))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD), ("!selected", BG_APP)],
                  foreground=[("selected", PRIMARY), ("!selected", TEXT_MUTED)])

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True)

        self._tab_lich = tk.Frame(self._nb, bg=BG_APP)
        self._tab_diemdanh = tk.Frame(self._nb, bg=BG_APP)
        self._tab_diem = tk.Frame(self._nb, bg=BG_APP)
        self._tab_nhanxet = tk.Frame(self._nb, bg=BG_APP)

        self._nb.add(self._tab_lich, text="📅  Lịch dạy của tôi")
        self._nb.add(self._tab_diemdanh, text="✅  Điểm danh")
        self._nb.add(self._tab_diem, text="📊  Nhập điểm")
        self._nb.add(self._tab_nhanxet, text="📝  Nhận xét lớp")

        self._build_tab_lich()
        self._build_tab_diemdanh()
        self._build_tab_diem()
        self._build_tab_nhanxet()

    # TAB LỊCH DẠY
    def _build_tab_lich(self):
        p = self._tab_lich
        thu_hom_nay = _thu_hom_nay()

        if not self._lop_cua_toi:
            tk.Label(p, text="Bạn chưa được phân công lớp nào.",
                     font=FONT_NORMAL, fg=TEXT_MUTED, bg=BG_APP).pack(pady=40)
            return

        tk.Label(p, text="Lịch dạy trong tuần", font=FONT_HEADING,
                 fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w", pady=(8, 4))
        MutedLabel(p, f"Hôm nay: {thu_hom_nay} — {_ngay_hom_nay()}",
                   bg=BG_APP).pack(anchor="w", pady=(0, 12))

        thu_list = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        grid = tk.Frame(p, bg=BG_APP)
        grid.pack(fill="both", expand=True)

        for col, thu in enumerate(thu_list):
            bg = PRIMARY if thu == thu_hom_nay else BG_SIDEBAR
            cell = tk.Frame(grid, bg=bg, padx=8, pady=6)
            cell.grid(row=0, column=col, sticky="ew", padx=2, pady=(0, 2))
            grid.columnconfigure(col, weight=1)
            tk.Label(cell, text=thu, font=FONT_BOLD,
                     fg=TEXT_WHITE, bg=bg).pack()

        thu_map: dict[str, list] = {t: [] for t in thu_list}
        for lop in self._lop_cua_toi:
            for buoi in lop.lich_hoc:
                thu_map[buoi.thu].append((lop, buoi))

        max_rows = max((len(v) for v in thu_map.values()), default=0)

        for row in range(max_rows):
            for col, thu in enumerate(thu_list):
                items = thu_map[thu]
                bg_cell = BG_CARD if col % 2 == 0 else "#F0F4FF"
                if row < len(items):
                    lop, buoi = items[row]
                    highlight = thu == thu_hom_nay
                    cell = tk.Frame(grid, bg=PRIMARY_LITE if highlight else bg_cell,
                                    padx=6, pady=6,
                                    highlightbackground=PRIMARY if highlight else BORDER,
                                    highlightthickness=1)
                    cell.grid(row=row + 1, column=col, sticky="nsew",
                              padx=2, pady=2)
                    tk.Label(cell, text=lop.ma_lop, font=FONT_BOLD,
                             fg=PRIMARY, bg=cell["bg"]).pack(anchor="w")
                    tk.Label(cell, text=lop.ten_mon, font=FONT_SMALL,
                             fg=TEXT_MAIN, bg=cell["bg"],
                             wraplength=120, justify="left").pack(anchor="w")
                    tk.Label(cell, text=buoi.tiet, font=FONT_SMALL,
                             fg=TEXT_MUTED, bg=cell["bg"]).pack(anchor="w")
                    if buoi.phong:
                        tk.Label(cell, text=f"🏫 {buoi.phong}",
                                 font=FONT_SMALL, fg=TEXT_MUTED,
                                 bg=cell["bg"]).pack(anchor="w")

                    def _click(e, ml=lop.ma_lop):
                        self._chon_lop_diemdanh(ml)
                        self._nb.select(1)

                    for w in cell.winfo_children() + [cell]:
                        w.bind("<Button-1>", _click)
                        w.config(cursor="hand2")
                else:
                    # Ô trống
                    cell = tk.Frame(grid, bg=bg_cell, padx=6, pady=6)
                    cell.grid(row=row + 1, column=col, sticky="nsew",
                              padx=2, pady=2)

            grid.rowconfigure(row + 1, weight=1)

    # TAB ĐIỂM DANH
    def _build_tab_diemdanh(self):
        p = self._tab_diemdanh

        toolbar = tk.Frame(p, bg=BG_APP)
        toolbar.pack(fill="x", pady=(8, 6))

        tk.Label(toolbar, text="Lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._dd_lop_var = tk.StringVar()
        self._dd_cb_lop = ttk.Combobox(
            toolbar, textvariable=self._dd_lop_var,
            values=[lop.ma_lop for lop in self._lop_cua_toi],
            state="readonly", width=10, font=FONT_NORMAL)
        self._dd_cb_lop.pack(side="left", padx=(4, 16))
        self._dd_cb_lop.bind("<<ComboboxSelected>>",
                             lambda e: self._on_chon_lop_dd())

        tk.Label(toolbar, text="Buổi:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._dd_buoi_var = tk.StringVar()
        self._dd_cb_buoi = ttk.Combobox(
            toolbar, textvariable=self._dd_buoi_var,
            state="readonly", width=20, font=FONT_NORMAL)
        self._dd_cb_buoi.pack(side="left", padx=(4, 16))
        self._dd_cb_buoi.bind("<<ComboboxSelected>>",
                              lambda e: self._on_chon_buoi_dd())

        tk.Label(toolbar, text="Ngày:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._dd_ngay_var = tk.StringVar(value=_ngay_hom_nay())
        tk.Entry(toolbar, textvariable=self._dd_ngay_var,
                 font=FONT_NORMAL, width=12, relief="solid",
                 bd=1).pack(side="left", padx=(4, 16))

        AppButton(toolbar, "Tải / Tạo buổi", style="primary",
                  command=self._tai_buoi_diemdanh).pack(side="left", padx=(0, 8))
        AppButton(toolbar, "💾 Lưu điểm danh", style="success",
                  command=self._luu_diemdanh).pack(side="left")

        # Thống kê nhanh
        self._dd_lbl_tk = tk.Label(p, text="", font=FONT_SMALL,
                                   fg=TEXT_MUTED, bg=BG_APP)
        self._dd_lbl_tk.pack(anchor="w", pady=(0, 4))

        # Bảng điểm danh
        cols = [
            ("stt", "STT", 45, "center"),
            ("mssv", "MSSV", 90, "center"),
            ("hoten", "Họ và tên", 200, "w"),
        ]
        tbl_frame = tk.Frame(p, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)

        self._dd_table = DataTable(tbl_frame, columns=cols, height=18)
        sb = DataTable.them_scrollbar(tbl_frame, self._dd_table)
        self._dd_table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._dd_trang_thai_frame = tk.Frame(tbl_frame, bg=BG_APP)
        self._dd_trang_thai_frame.pack(side="left", fill="y", padx=(2, 0))

        self._dd_tt_vars: dict[str, tk.StringVar] = {}
        self._dd_sv_list: list = []  # danh sách sinh viên hiện tại

        # Ghi chú buổi
        gc_frame = tk.Frame(p, bg=BG_APP)
        gc_frame.pack(fill="x", pady=(6, 0))
        tk.Label(gc_frame, text="Ghi chú buổi học:", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_APP).pack(anchor="w")
        self._dd_ghi_chu = tk.Text(gc_frame, height=2, font=FONT_NORMAL,
                                   relief="solid", bd=1, wrap="word")
        self._dd_ghi_chu.pack(fill="x")

        if self._lop_cua_toi:
            self._dd_cb_lop.current(0)
            self._on_chon_lop_dd()

    def _chon_lop_diemdanh(self, ma_lop: str):
        vals = [lop.ma_lop for lop in self._lop_cua_toi]
        if ma_lop in vals:
            self._dd_lop_var.set(ma_lop)
            self._on_chon_lop_dd()

    def _on_chon_lop_dd(self):
        ma_lop = self._dd_lop_var.get()
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        if not lop:
            return
        buoi_vals = [f"{b.thu} — {b.tiet} ({b.gio})" for b in lop.lich_hoc]
        self._dd_cb_buoi["values"] = buoi_vals
        if buoi_vals:
            thu_hom_nay = _thu_hom_nay()
            idx = next((i for i, b in enumerate(lop.lich_hoc)
                        if b.thu == thu_hom_nay), 0)
            self._dd_cb_buoi.current(idx)
        self._xoa_bang_diemdanh()

    def _on_chon_buoi_dd(self):
        self._xoa_bang_diemdanh()

    def _lay_buoi_hoc_chon(self):
        ma_lop = self._dd_lop_var.get()
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        if not lop or not lop.lich_hoc:
            return None
        idx = self._dd_cb_buoi.current()
        if idx < 0 or idx >= len(lop.lich_hoc):
            return None
        return lop.lich_hoc[idx]

    def _tai_buoi_diemdanh(self):
        ma_lop = self._dd_lop_var.get()
        ngay = self._dd_ngay_var.get().strip()
        buoi = self._lay_buoi_hoc_chon()
        if not ma_lop or not buoi:
            messagebox.showwarning("Thiếu thông tin",
                                   "Vui lòng chọn lớp và buổi học.")
            return

        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        svcs = self._svcs["sv"]

        ds_sv = [svcs.tim_theo_khoa(mssv) for mssv in lop.danh_sach_mssv]
        ds_sv = [sv for sv in ds_sv if sv]

        dd_cu = self._svcs["dd"].tim_buoi(ma_lop, ngay, buoi.tiet)

        self._xoa_bang_diemdanh()
        self._dd_sv_list = ds_sv
        self._dd_tt_vars = {}

        hdr_frame = tk.Frame(self._dd_trang_thai_frame, bg=PRIMARY)
        hdr_frame.pack(fill="x")
        for tt in TRANG_THAI_LIST:
            tk.Label(hdr_frame, text=tt, font=FONT_BOLD,
                     fg=TEXT_WHITE, bg=PRIMARY,
                     width=10, pady=6).pack(side="left")

        for i, sv in enumerate(ds_sv):
            tag = "even" if i % 2 == 0 else "odd"
            self._dd_table.chen_hang([i + 1, sv.mssv, sv.ho_ten])

            tt_default = "Có mặt"
            if dd_cu and sv.mssv in dd_cu.ds_trang_thai:
                tt_default = dd_cu.ds_trang_thai[sv.mssv]

            var = tk.StringVar(value=tt_default)
            self._dd_tt_vars[sv.mssv] = var

            bg_row = BG_CARD if i % 2 == 0 else BG_TABLE_ODD
            row_f = tk.Frame(self._dd_trang_thai_frame, bg=bg_row, pady=3)
            row_f.pack(fill="x")
            for tt in TRANG_THAI_LIST:
                color = TRANG_THAI_COLOR[tt]
                rb = tk.Radiobutton(
                    row_f, variable=var, value=tt,
                    text=TRANG_THAI_ICON[tt],
                    font=FONT_BOLD, fg=color,
                    bg=bg_row, activebackground=bg_row,
                    selectcolor=bg_row,
                    indicatoron=False,
                    width=8, pady=2,
                    relief="flat", cursor="hand2",
                )
                rb.pack(side="left", padx=1)

        # Ghi chú
        self._dd_ghi_chu.delete("1.0", "end")
        if dd_cu and dd_cu.ghi_chu:
            self._dd_ghi_chu.insert("1.0", dd_cu.ghi_chu)

        self._cap_nhat_thong_ke_dd()

    def _cap_nhat_thong_ke_dd(self, *_):
        if not self._dd_tt_vars:
            return
        from collections import Counter
        c = Counter(v.get() for v in self._dd_tt_vars.values())
        self._dd_lbl_tk.config(
            text=(f"Tổng: {len(self._dd_tt_vars)} SV  |  "
                  f"✓ Có mặt: {c.get('Có mặt', 0)}  "
                  f"✗ Vắng: {c.get('Vắng', 0)}  "
                  f"P Phép: {c.get('Vắng có phép', 0)}  "
                  f"~ Trễ: {c.get('Trễ', 0)}")
        )

    def _luu_diemdanh(self):
        ma_lop = self._dd_lop_var.get()
        ngay = self._dd_ngay_var.get().strip()
        buoi = self._lay_buoi_hoc_chon()
        if not ma_lop or not buoi or not self._dd_tt_vars:
            messagebox.showwarning("Chưa có dữ liệu",
                                   "Vui lòng tải buổi điểm danh trước.")
            return

        ds_tt = {mssv: var.get() for mssv, var in self._dd_tt_vars.items()}
        ghi_chu = self._dd_ghi_chu.get("1.0", "end").strip()
        dd = DiemDanh(
            ma_lop=ma_lop, ngay=ngay,
            thu=buoi.thu, tiet=buoi.tiet,
            ds_trang_thai=ds_tt, ghi_chu=ghi_chu,
        )
        ok, msg = self._svcs["dd"].luu_buoi(dd)
        if ok:
            self._status.ok(msg)
            self._cap_nhat_thong_ke_dd()
        else:
            self._status.err(msg)

    def _xoa_bang_diemdanh(self):
        self._dd_table.xoa_tat_ca()
        for w in self._dd_trang_thai_frame.winfo_children():
            w.destroy()
        self._dd_tt_vars.clear()
        self._dd_sv_list.clear()
        self._dd_lbl_tk.config(text="")

    # TAB NHẬP ĐIỂM
    def _build_tab_diem(self):
        p = self._tab_diem

        toolbar = tk.Frame(p, bg=BG_APP)
        toolbar.pack(fill="x", pady=(8, 6))
        tk.Label(toolbar, text="Lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._d_lop_var = tk.StringVar()
        cb = ttk.Combobox(toolbar, textvariable=self._d_lop_var,
                          values=[lop.ma_lop for lop in self._lop_cua_toi],
                          state="readonly", width=12, font=FONT_NORMAL)
        cb.pack(side="left", padx=(4, 16))
        cb.bind("<<ComboboxSelected>>", lambda e: self._tai_bang_diem())

        AppButton(toolbar, "Tải bảng điểm", style="primary",
                  command=self._tai_bang_diem).pack(side="left", padx=(0, 8))
        AppButton(toolbar, "💾 Lưu tất cả", style="success",
                  command=self._luu_tat_ca_diem).pack(side="left")

        self._d_lbl_tk = tk.Label(p, text="", font=FONT_SMALL,
                                  fg=TEXT_MUTED, bg=BG_APP)
        self._d_lbl_tk.pack(anchor="w", pady=(0, 4))

        cols = [
            ("stt", "STT", 45, "center"),
            ("mssv", "MSSV", 90, "center"),
            ("hoten", "Họ và tên", 190, "w"),
            ("cc", "Chuyên cần", 90, "center"),
            ("gk", "Giữa kỳ", 90, "center"),
            ("ck", "Cuối kỳ", 90, "center"),
            ("tk", "Tổng kết", 90, "center"),
            ("xl", "Xếp loại", 90, "center"),
        ]
        tbl_wrap = tk.Frame(p, bg=BG_APP)
        tbl_wrap.pack(fill="both", expand=True)

        self._d_table = DataTable(tbl_wrap, columns=cols, height=16)
        sb = DataTable.them_scrollbar(tbl_wrap, self._d_table)
        self._d_table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._d_table.bind("<<TreeviewSelect>>", self._on_chon_sv_diem)

        # Form nhập điểm 1 SV
        form = Card(p, padx=12, pady=12)
        form.pack(fill="x", pady=(8, 0))
        tk.Label(form, text="Nhập điểm sinh viên đang chọn:",
                 font=FONT_BOLD, fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w")
        row_f = tk.Frame(form, bg=BG_CARD)
        row_f.pack(fill="x", pady=(6, 0))
        self._d_mssv_var = tk.StringVar()
        self._d_cc_var = tk.StringVar()
        self._d_gk_var = tk.StringVar()
        self._d_ck_var = tk.StringVar()

        for label, var, ph in [
            ("MSSV", self._d_mssv_var, "—"),
            ("Chuyên cần", self._d_cc_var, "0-10"),
            ("Giữa kỳ", self._d_gk_var, "0-10"),
            ("Cuối kỳ", self._d_ck_var, "0-10"),
        ]:
            col = tk.Frame(row_f, bg=BG_CARD)
            col.pack(side="left", padx=(0, 12))
            tk.Label(col, text=label, font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
            state = "disabled" if label == "MSSV" else "normal"
            tk.Entry(col, textvariable=var, font=FONT_NORMAL,
                     width=10, relief="solid", bd=1,
                     state=state).pack()

        AppButton(row_f, "Lưu điểm SV này", style="primary",
                  command=self._luu_diem_1_sv).pack(side="left",
                                                    pady=(14, 0))

        self._d_diem_map: dict[str, DiemSo] = {}  # mssv -> DiemSo

        if self._lop_cua_toi:
            cb.current(0)
            self._tai_bang_diem()

    def _tai_bang_diem(self):
        ma_lop = self._d_lop_var.get()
        if not ma_lop:
            return
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        sv_svc = self._svcs["sv"]
        ds_svc = self._svcs["diem"]

        self._d_table.xoa_tat_ca()
        self._d_diem_map.clear()

        ds_sv = [sv_svc.tim_theo_khoa(mssv)
                 for mssv in lop.danh_sach_mssv]
        ds_sv = [sv for sv in ds_sv if sv]

        dau = 0
        for i, sv in enumerate(ds_sv):
            diem = ds_svc.tim_diem(sv.mssv, ma_lop)
            if not diem:
                diem = DiemSo(mssv=sv.mssv, ma_lop=ma_lop)
            self._d_diem_map[sv.mssv] = diem

            def _fmt(v):
                return f"{v:.1f}" if v is not None else "—"

            dtk = diem.diem_tong_ket
            if dtk is not None and dtk >= 5.0:
                dau += 1

            self._d_table.chen_hang([
                i + 1, sv.mssv, sv.ho_ten,
                _fmt(diem.diem_chuyen_can),
                _fmt(diem.diem_giua_ky),
                _fmt(diem.diem_cuoi_ky),
                _fmt(dtk),
                diem.xep_loai,
            ])

        total = len(ds_sv)
        ti_le = round(dau / total * 100, 1) if total else 0
        self._d_lbl_tk.config(
            text=f"Tổng: {total} SV  |  Đã có điểm TK: {len([d for d in self._d_diem_map.values() if d.diem_tong_ket is not None])}  |  Tỉ lệ đậu: {ti_le}%"
        )

    def _on_chon_sv_diem(self, _):
        row = self._d_table.lay_hang_chon()
        if not row:
            return
        mssv = row[1]
        self._d_mssv_var.set(mssv)
        diem = self._d_diem_map.get(mssv)
        if diem:
            def _s(v): return str(v) if v is not None else ""

            self._d_cc_var.set(_s(diem.diem_chuyen_can))
            self._d_gk_var.set(_s(diem.diem_giua_ky))
            self._d_ck_var.set(_s(diem.diem_cuoi_ky))

    def _parse_diem(self, s: str):
        try:
            return float(s) if s.strip() else None
        except ValueError:
            return None

    def _luu_diem_1_sv(self):
        mssv = self._d_mssv_var.get()
        ma_lop = self._d_lop_var.get()
        if not mssv or not ma_lop:
            return
        diem = DiemSo(
            mssv=mssv, ma_lop=ma_lop,
            diem_chuyen_can=self._parse_diem(self._d_cc_var.get()),
            diem_giua_ky=self._parse_diem(self._d_gk_var.get()),
            diem_cuoi_ky=self._parse_diem(self._d_ck_var.get()),
        )
        ok_val, msg_val = diem.validate()
        if not ok_val:
            self._status.err(msg_val)
            return
        ds_svc = self._svcs["diem"]
        cu = ds_svc.tim_diem(mssv, ma_lop)
        ok, msg = ds_svc.cap_nhat(diem) if cu else ds_svc.them(diem)
        if ok:
            self._d_diem_map[mssv] = diem
            self._status.ok(msg)
            self._tai_bang_diem()
        else:
            self._status.err(msg)

    def _luu_tat_ca_diem(self):
        ds_svc = self._svcs["diem"]
        thanh_cong = 0
        for mssv, diem in self._d_diem_map.items():
            if any(v is not None for v in [
                diem.diem_chuyen_can, diem.diem_giua_ky, diem.diem_cuoi_ky
            ]):
                cu = ds_svc.tim_diem(mssv, diem.ma_lop)
                ok, _ = ds_svc.cap_nhat(diem) if cu else ds_svc.them(diem)
                if ok:
                    thanh_cong += 1
        self._status.ok(f"Đã lưu {thanh_cong} bản ghi điểm.")
        self._tai_bang_diem()

    # TAB NHẬN XÉT LỚP
    def _build_tab_nhanxet(self):
        p = self._tab_nhanxet

        toolbar = tk.Frame(p, bg=BG_APP)
        toolbar.pack(fill="x", pady=(8, 12))
        tk.Label(toolbar, text="Lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._nx_lop_var = tk.StringVar()
        cb = ttk.Combobox(toolbar, textvariable=self._nx_lop_var,
                          values=[lop.ma_lop for lop in self._lop_cua_toi],
                          state="readonly", width=12, font=FONT_NORMAL)
        cb.pack(side="left", padx=(4, 16))
        cb.bind("<<ComboboxSelected>>", lambda e: self._tai_nhan_xet())

        AppButton(toolbar, "💾 Lưu nhận xét", style="primary",
                  command=self._luu_nhan_xet).pack(side="left")
        self._nx_lbl_time = tk.Label(toolbar, text="", font=FONT_SMALL,
                                     fg=TEXT_MUTED, bg=BG_APP)
        self._nx_lbl_time.pack(side="right")

        card = Card(p, padx=16, pady=16)
        card.pack(fill="both", expand=True)

        HeadingLabel(card, "Nhận xét chung của giáo viên", bg=BG_CARD).pack(anchor="w")
        MutedLabel(card, "Nhận xét này áp dụng cho toàn bộ lớp học.",
                   bg=BG_CARD).pack(anchor="w", pady=(2, 10))

        self._nx_text = tk.Text(card, font=FONT_NORMAL, relief="solid",
                                bd=1, wrap="word", height=15,
                                padx=8, pady=8)
        self._nx_text.pack(fill="both", expand=True)

        mau = tk.Frame(card, bg=BG_CARD)
        mau.pack(fill="x", pady=(8, 0))
        MutedLabel(mau, "Gợi ý nhanh:", bg=BG_CARD).pack(side="left")
        for text in ["Tích cực", "Cần cố gắng", "Nghỉ nhiều", "Tốt"]:
            AppButton(mau, text, style="ghost",
                      command=lambda t=text: self._chen_mau(t)
                      ).pack(side="left", padx=4)

        if self._lop_cua_toi:
            cb.current(0)
            self._tai_nhan_xet()

    def _tai_nhan_xet(self):
        ma_lop = self._nx_lop_var.get()
        nx = self._svcs["nx"].lay_nhan_xet(ma_lop)
        self._nx_text.delete("1.0", "end")
        if nx:
            self._nx_text.insert("1.0", nx.noi_dung)
            self._nx_lbl_time.config(
                text=f"Cập nhật lần cuối: {nx.cap_nhat_luc}")
        else:
            self._nx_lbl_time.config(text="Chưa có nhận xét")

    def _luu_nhan_xet(self):
        ma_lop = self._nx_lop_var.get()
        noi_dung = self._nx_text.get("1.0", "end").strip()
        if not ma_lop:
            messagebox.showwarning("Chưa chọn lớp", "Vui lòng chọn lớp.")
            return
        ok, msg = self._svcs["nx"].luu_nhan_xet(
            ma_lop, self._nd.ten_dang_nhap, noi_dung)
        if ok:
            self._status.ok(msg)
            self._tai_nhan_xet()
        else:
            self._status.err(msg)

    def _chen_mau(self, text: str):
        self._nx_text.insert("end", text + " ")
        self._nx_text.focus()
