# views/gv_tabs/diem_danh_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from views.theme import *
from views.widgets import AppButton, DataTable, MutedLabel
from models.diem_danh import (DiemDanh, TRANG_THAI_LIST,
                              TRANG_THAI_ICON, TRANG_THAI_COLOR)

_WEEKDAY_MAP = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5",
                4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}


def _thu_hom_nay():  return _WEEKDAY_MAP[date.today().weekday()]


def _ngay_hom_nay(): return date.today().strftime("%d/%m/%Y")


class DiemDanhView(tk.Frame):
    COLS = [
        ("stt", "STT", 45, "center"),
        ("mssv", "MSSV", 90, "center"),
        ("hoten", "Họ và tên", 200, "w"),
    ]

    def __init__(self, parent, services: dict,
                 lop_cua_toi: list, statusbar, **kw):
        super().__init__(parent, bg=BG_APP, **kw)
        self._svcs = services
        self._lop_list = lop_cua_toi
        self._status = statusbar
        self._tt_vars: dict[str, tk.StringVar] = {}
        self._sv_list: list = []
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="✅  Điểm danh",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w",
                                                                pady=(0, 12))
        # Toolbar
        bar = tk.Frame(self, bg=BG_APP)
        bar.pack(fill="x", pady=(0, 6))

        for text, var_name, width, default in [
            ("Lớp:", "_lop_var", 10, None),
            ("Buổi:", "_buoi_var", 22, None),
        ]:
            tk.Label(bar, text=text, font=FONT_BOLD,
                     fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
            var = tk.StringVar()
            setattr(self, var_name, var)
            cb = ttk.Combobox(bar, textvariable=var,
                              state="readonly", width=width, font=FONT_NORMAL)
            cb.pack(side="left", padx=(4, 14))
            setattr(self, var_name.replace("_var", "_cb"), cb)

        tk.Label(bar, text="Ngày:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._ngay_var = tk.StringVar(value=_ngay_hom_nay())
        tk.Entry(bar, textvariable=self._ngay_var,
                 font=FONT_NORMAL, width=12,
                 relief="solid", bd=1).pack(side="left", padx=(4, 14))

        AppButton(bar, "Tải buổi", style="primary",
                  command=self._tai_buoi).pack(side="left", padx=(0, 8))
        AppButton(bar, "💾 Lưu", style="success",
                  command=self._luu).pack(side="left")

        # Thống kê
        self._lbl_tk = MutedLabel(self, "", bg=BG_APP)
        self._lbl_tk.pack(anchor="w", pady=(0, 4))

        # Bảng + trạng thái
        tbl_wrap = tk.Frame(self, bg=BG_APP)
        tbl_wrap.pack(fill="both", expand=True)

        self._table = DataTable(tbl_wrap, columns=self.COLS, height=20)
        sb = DataTable.them_scrollbar(tbl_wrap, self._table)
        self._table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tt_frame = tk.Frame(tbl_wrap, bg=BG_APP)
        self._tt_frame.pack(side="left", fill="y", padx=(2, 0))

        # Ghi chú
        gc = tk.Frame(self, bg=BG_APP)
        gc.pack(fill="x", pady=(6, 0))
        tk.Label(gc, text="Ghi chú buổi:",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP).pack(anchor="w")
        self._ghi_chu = tk.Text(gc, height=2, font=FONT_NORMAL,
                                relief="solid", bd=1, wrap="word")
        self._ghi_chu.pack(fill="x")

        # Điền combobox
        self._lop_cb["values"] = [l.ma_lop for l in self._lop_list]
        self._lop_cb.bind("<<ComboboxSelected>>", lambda e: self._on_chon_lop())
        if self._lop_list:
            self._lop_cb.current(0)
            self._on_chon_lop()

    def _on_chon_lop(self):
        ma_lop = self._lop_var.get()
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        if not lop:
            return
        buoi_vals = [f"{b.thu} — {b.tiet} ({b.gio})"
                     for b in lop.lich_hoc]
        self._buoi_cb["values"] = buoi_vals
        if buoi_vals:
            thu_hom = _thu_hom_nay()
            idx = next((i for i, b in enumerate(lop.lich_hoc)
                        if b.thu == thu_hom), 0)
            self._buoi_cb.current(idx)
        self._xoa_bang()

    def _lay_buoi_chon(self):
        ma_lop = self._lop_var.get()
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        if not lop or not lop.lich_hoc:
            return None
        idx = self._buoi_cb.current()
        if idx < 0 or idx >= len(lop.lich_hoc):
            return None
        return lop.lich_hoc[idx]

    def _tai_buoi(self):
        ma_lop = self._lop_var.get()
        ngay = self._ngay_var.get().strip()
        buoi = self._lay_buoi_chon()
        if not ma_lop or not buoi:
            messagebox.showwarning("Thiếu thông tin",
                                   "Vui lòng chọn lớp và buổi học.")
            return

        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        ds_sv = [self._svcs["sv"].tim_theo_khoa(m)
                 for m in lop.danh_sach_mssv]
        ds_sv = [s for s in ds_sv if s]

        dd_cu = self._svcs["dd"].tim_buoi(ma_lop, ngay, buoi.tiet)

        self._xoa_bang()
        self._sv_list = ds_sv
        self._tt_vars = {}

        # Header cột trạng thái
        hdr = tk.Frame(self._tt_frame, bg=PRIMARY)
        hdr.pack(fill="x")
        for tt in TRANG_THAI_LIST:
            tk.Label(hdr, text=tt, font=FONT_BOLD,
                     fg=TEXT_WHITE, bg=PRIMARY,
                     width=11, pady=6).pack(side="left")

        for i, sv in enumerate(ds_sv):
            self._table.chen_hang([i + 1, sv.mssv, sv.ho_ten])

            tt_default = "Có mặt"
            if dd_cu and sv.mssv in dd_cu.ds_trang_thai:
                tt_default = dd_cu.ds_trang_thai[sv.mssv]
            var = tk.StringVar(value=tt_default)
            self._tt_vars[sv.mssv] = var

            bg_row = BG_CARD if i % 2 == 0 else BG_TABLE_ODD
            row_f = tk.Frame(self._tt_frame, bg=bg_row, pady=3)
            row_f.pack(fill="x")

            for tt in TRANG_THAI_LIST:
                color = TRANG_THAI_COLOR[tt]
                tk.Radiobutton(
                    row_f, variable=var, value=tt,
                    text=TRANG_THAI_ICON[tt],
                    font=FONT_BOLD, fg=color,
                    bg=bg_row, activebackground=bg_row,
                    selectcolor=bg_row, indicatoron=False,
                    width=9, pady=2, relief="flat", cursor="hand2",
                ).pack(side="left", padx=1)

        self._ghi_chu.delete("1.0", "end")
        if dd_cu and dd_cu.ghi_chu:
            self._ghi_chu.insert("1.0", dd_cu.ghi_chu)
        self._cap_nhat_tk()

    def _cap_nhat_tk(self, *_):
        if not self._tt_vars:
            return
        from collections import Counter
        c = Counter(v.get() for v in self._tt_vars.values())
        self._lbl_tk.config(
            text=(f"Tổng: {len(self._tt_vars)} SV  |  "
                  f"✓ Có mặt: {c.get('Có mặt', 0)}  "
                  f"✗ Vắng: {c.get('Vắng', 0)}  "
                  f"P Phép: {c.get('Vắng có phép', 0)}  "
                  f"~ Trễ: {c.get('Trễ', 0)}")
        )

    def _luu(self):
        ma_lop = self._lop_var.get()
        ngay = self._ngay_var.get().strip()
        buoi = self._lay_buoi_chon()
        if not ma_lop or not buoi or not self._tt_vars:
            messagebox.showwarning("Chưa tải dữ liệu",
                                   "Vui lòng bấm 'Tải buổi' trước.")
            return
        ds_tt = {m: v.get() for m, v in self._tt_vars.items()}
        ghi_chu = self._ghi_chu.get("1.0", "end").strip()
        dd = DiemDanh(ma_lop=ma_lop, ngay=ngay,
                      thu=buoi.thu, tiet=buoi.tiet,
                      ds_trang_thai=ds_tt, ghi_chu=ghi_chu)
        ok, msg = self._svcs["dd"].luu_buoi(dd)
        if ok:
            self._status.ok(msg)
            self._cap_nhat_tk()
        else:
            self._status.err(msg)

    def _xoa_bang(self):
        self._table.xoa_tat_ca()
        for w in self._tt_frame.winfo_children():
            w.destroy()
        self._tt_vars.clear()
        self._sv_list.clear()
        self._lbl_tk.config(text="")
