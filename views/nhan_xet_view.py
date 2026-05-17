# views/gv_tabs/nhan_xet_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import *
from views.widgets import AppButton, Card, HeadingLabel, MutedLabel


class NhanXetView(tk.Frame):

    def __init__(self, parent, services: dict, nguoi_dung,
                 lop_cua_toi: list, statusbar, **kw):
        super().__init__(parent, bg=BG_APP, **kw)
        self._svcs = services
        self._nd = nguoi_dung
        self._lop_list = lop_cua_toi
        self._status = statusbar
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="📝  Nhận xét lớp",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w",
                                                                pady=(0, 12))
        # Toolbar
        bar = tk.Frame(self, bg=BG_APP)
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="Lớp:", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        self._lop_var = tk.StringVar()
        cb = ttk.Combobox(bar, textvariable=self._lop_var,
                          values=[l.ma_lop for l in self._lop_list],
                          state="readonly", width=12, font=FONT_NORMAL)
        cb.pack(side="left", padx=(4, 16))
        cb.bind("<<ComboboxSelected>>", lambda e: self._tai())

        AppButton(bar, "💾 Lưu nhận xét", style="primary",
                  command=self._luu).pack(side="left")

        self._lbl_time = MutedLabel(bar, "", bg=BG_APP)
        self._lbl_time.pack(side="right")

        # Card nhận xét
        card = Card(self, padx=16, pady=16)
        card.pack(fill="both", expand=True)

        HeadingLabel(card, "Nhận xét chung của giảng viên",
                     bg=BG_CARD).pack(anchor="w")
        MutedLabel(card, "Áp dụng cho toàn bộ lớp học.",
                   bg=BG_CARD).pack(anchor="w", pady=(2, 10))

        self._text = tk.Text(card, font=FONT_NORMAL, relief="solid",
                             bd=1, wrap="word", height=15, padx=8, pady=8)
        self._text.pack(fill="both", expand=True)

        # Gợi ý nhanh
        mau = tk.Frame(card, bg=BG_CARD)
        mau.pack(fill="x", pady=(8, 0))
        MutedLabel(mau, "Gợi ý:", bg=BG_CARD).pack(side="left")
        for t in ["Lớp học tích cực", "Cần cải thiện", "Vắng nhiều",
                  "Chất lượng tốt", "Cần ôn tập thêm"]:
            AppButton(mau, t, style="ghost",
                      command=lambda s=t: self._chen(s)).pack(side="left",
                                                              padx=3)

        if self._lop_list:
            cb.current(0)
            self._tai()

    def _tai(self):
        ma_lop = self._lop_var.get()
        nx = self._svcs["nx"].lay_nhan_xet(ma_lop)
        self._text.delete("1.0", "end")
        if nx:
            self._text.insert("1.0", nx.noi_dung)
            self._lbl_time.config(
                text=f"Cập nhật lần cuối: {nx.cap_nhat_luc}")
        else:
            self._lbl_time.config(text="Chưa có nhận xét")

    def _luu(self):
        ma_lop = self._lop_var.get()
        noi_dung = self._text.get("1.0", "end").strip()
        if not ma_lop:
            messagebox.showwarning("Chưa chọn lớp",
                                   "Vui lòng chọn lớp.")
            return
        ok, msg = self._svcs["nx"].luu_nhan_xet(
            ma_lop, self._nd.ten_dang_nhap, noi_dung)
        if ok:
            self._status.ok(msg)
            self._tai()
        else:
            self._status.err(msg)

    def _chen(self, text: str):
        self._text.insert("end", text + " ")
        self._text.focus()
