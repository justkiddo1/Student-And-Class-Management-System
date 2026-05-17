# views/gv_tabs/nhap_diem_view.py
import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import AppButton, Card, DataTable, MutedLabel
from models.diem_so import DiemSo


class NhapDiemView(tk.Frame):
    COLS = [
        ("stt", "STT", 45, "center"),
        ("mssv", "MSSV", 90, "center"),
        ("hoten", "Họ và tên", 200, "w"),
        ("cc", "Chuyên cần", 95, "center"),
        ("gk", "Giữa kỳ", 95, "center"),
        ("ck", "Cuối kỳ", 95, "center"),
        ("tk", "Tổng kết", 95, "center"),
        ("xl", "Xếp loại", 90, "center"),
    ]

    def __init__(self, parent, services: dict,
                 lop_cua_toi: list, statusbar, **kw):
        super().__init__(parent, bg=BG_APP, **kw)
        self._svcs = services
        self._lop_list = lop_cua_toi
        self._status = statusbar
        self._diem_map: dict[str, DiemSo] = {}
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="📊  Nhập điểm",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w",
                                                                pady=(0, 12))
        # Toolbar
        bar = tk.Frame(self, bg=BG_APP)
        bar.pack(fill="x", pady=(0, 6))
        tk.Label(bar, text="Lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._lop_var = tk.StringVar()
        self._lop_cb = ttk.Combobox(
            bar, textvariable=self._lop_var,
            values=[l.ma_lop for l in self._lop_list],
            state="readonly", width=12, font=FONT_NORMAL)
        self._lop_cb.pack(side="left", padx=(4, 14))
        self._lop_cb.bind("<<ComboboxSelected>>",
                          lambda e: self._tai_bang())

        AppButton(bar, "Tải bảng điểm", style="primary",
                  command=self._tai_bang).pack(side="left", padx=(0, 8))
        AppButton(bar, "💾 Lưu tất cả", style="success",
                  command=self._luu_tat_ca).pack(side="left")

        self._lbl_tk = MutedLabel(self, "", bg=BG_APP)
        self._lbl_tk.pack(anchor="w", pady=(0, 4))

        # Bảng
        tbl_frame = tk.Frame(self, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)
        self._table = DataTable(tbl_frame, columns=self.COLS, height=17)
        sb = DataTable.them_scrollbar(tbl_frame, self._table)
        self._table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._table.bind("<<TreeviewSelect>>", self._on_chon)

        # Form nhập điểm nhanh
        form = Card(self, padx=12, pady=10)
        form.pack(fill="x", pady=(8, 0))
        tk.Label(form, text="Nhập điểm cho sinh viên đang chọn:",
                 font=FONT_BOLD, fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w")

        row_f = tk.Frame(form, bg=BG_CARD)
        row_f.pack(fill="x", pady=(6, 0))

        self._mssv_var = tk.StringVar()
        self._cc_var = tk.StringVar()
        self._gk_var = tk.StringVar()
        self._ck_var = tk.StringVar()

        for label, var, disabled in [
            ("MSSV", self._mssv_var, True),
            ("Chuyên cần", self._cc_var, False),
            ("Giữa kỳ", self._gk_var, False),
            ("Cuối kỳ", self._ck_var, False),
        ]:
            col = tk.Frame(row_f, bg=BG_CARD)
            col.pack(side="left", padx=(0, 12))
            tk.Label(col, text=label, font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
            tk.Entry(col, textvariable=var, font=FONT_NORMAL,
                     width=11, relief="solid", bd=1,
                     state="disabled" if disabled else "normal").pack()

        AppButton(row_f, "Lưu SV này", style="primary",
                  command=self._luu_1_sv).pack(side="left", pady=(14, 0))

        # Chọn lớp đầu tiên
        if self._lop_list:
            self._lop_cb.current(0)
            self._tai_bang()

    def _tai_bang(self):
        ma_lop = self._lop_var.get()
        if not ma_lop:
            return
        lop = self._svcs["lop"].tim_theo_khoa(ma_lop)
        sv_svc = self._svcs["sv"]
        ds_svc = self._svcs["diem"]

        self._table.xoa_tat_ca()
        self._diem_map.clear()

        ds_sv = [sv_svc.tim_theo_khoa(m) for m in lop.danh_sach_mssv]
        ds_sv = [s for s in ds_sv if s]

        dau = 0
        for i, sv in enumerate(ds_sv):
            diem = ds_svc.tim_diem(sv.mssv, ma_lop) or DiemSo(sv.mssv, ma_lop)
            self._diem_map[sv.mssv] = diem
            dtk = diem.diem_tong_ket
            if dtk and dtk >= 5.0:
                dau += 1

            def _f(v):
                return f"{v:.1f}" if v is not None else "—"

            self._table.chen_hang([
                i + 1, sv.mssv, sv.ho_ten,
                _f(diem.diem_chuyen_can), _f(diem.diem_giua_ky),
                _f(diem.diem_cuoi_ky), _f(dtk), diem.xep_loai,
            ])

        total = len(ds_sv)
        ti_le = round(dau / total * 100, 1) if total else 0
        co_dtk = sum(1 for d in self._diem_map.values()
                     if d.diem_tong_ket is not None)
        self._lbl_tk.config(
            text=f"Tổng: {total} SV  •  Đã có điểm TK: {co_dtk}  •  Tỉ lệ đậu: {ti_le}%"
        )

    def _on_chon(self, _):
        row = self._table.lay_hang_chon()
        if not row:
            return
        mssv = row[1]
        self._mssv_var.set(mssv)
        d = self._diem_map.get(mssv)
        if d:
            def _s(v): return str(v) if v is not None else ""

            self._cc_var.set(_s(d.diem_chuyen_can))
            self._gk_var.set(_s(d.diem_giua_ky))
            self._ck_var.set(_s(d.diem_cuoi_ky))

    def _parse(self, s):
        try:
            return float(s.strip()) if s.strip() else None
        except ValueError:
            return None

    def _luu_1_sv(self):
        mssv = self._mssv_var.get()
        ma_lop = self._lop_var.get()
        if not mssv or not ma_lop:
            return
        diem = DiemSo(mssv=mssv, ma_lop=ma_lop,
                      diem_chuyen_can=self._parse(self._cc_var.get()),
                      diem_giua_ky=self._parse(self._gk_var.get()),
                      diem_cuoi_ky=self._parse(self._ck_var.get()))
        ok_v, msg_v = diem.validate()
        if not ok_v:
            self._status.err(msg_v);
            return
        svc = self._svcs["diem"]
        cu = svc.tim_diem(mssv, ma_lop)
        ok, msg = svc.cap_nhat(diem) if cu else svc.them(diem)
        if ok:
            self._diem_map[mssv] = diem
            self._status.ok(msg)
            self._tai_bang()
        else:
            self._status.err(msg)

    def _luu_tat_ca(self):
        svc = self._svcs["diem"]
        n = 0
        for mssv, diem in self._diem_map.items():
            if any(v is not None for v in [diem.diem_chuyen_can,
                                           diem.diem_giua_ky,
                                           diem.diem_cuoi_ky]):
                cu = svc.tim_diem(mssv, diem.ma_lop)
                ok, _ = svc.cap_nhat(diem) if cu else svc.them(diem)
                if ok: n += 1
        self._status.ok(f"Đã lưu {n} bản ghi điểm.")
        self._tai_bang()
