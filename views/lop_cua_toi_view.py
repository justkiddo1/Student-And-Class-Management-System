import tkinter as tk
from tkinter import ttk
from views.theme import *
from views.widgets import AppButton, Card, DataTable, HeadingLabel, MutedLabel


class LopCuaToiView(tk.Frame):
    COLS_SV = [
        ("stt", "STT", 45, "center"),
        ("mssv", "MSSV", 90, "center"),
        ("hoten", "Họ và tên", 200, "w"),
        ("gt", "Giới tính", 75, "center"),
        ("ns", "Ngày sinh", 95, "center"),
        ("email", "Email", 200, "w"),
        ("sdt", "Số ĐT", 110, "center"),
    ]

    def __init__(self, parent, services: dict,
                 lop_cua_toi: list, statusbar, **kw):
        super().__init__(parent, bg=BG_APP, **kw)
        self._svcs = services
        self._lop_list = lop_cua_toi
        self._status = statusbar
        self._lop_chon = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🏫  Lớp của tôi",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w",
                                                                pady=(0, 4))
        MutedLabel(self,
                   f"Bạn đang phụ trách {len(self._lop_list)} lớp — "
                   "chọn lớp để xem danh sách sinh viên.",
                   bg=BG_APP).pack(anchor="w", pady=(0, 12))

        main = tk.Frame(self, bg=BG_APP)
        main.pack(fill="both", expand=True)

        self._build_panel_lop(main)
        self._build_panel_sv(main)

        # Chọn lớp đầu tiên nếu có
        if self._lop_list:
            self._chon_lop(self._lop_list[0])

    # Panel trái: danh sách lớp
    def _build_panel_lop(self, parent):
        left = tk.Frame(parent, bg=BG_APP, width=260)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        HeadingLabel(left, "Danh sách lớp", bg=BG_APP).pack(anchor="w",
                                                            pady=(0, 8))

        if not self._lop_list:
            tk.Label(left, text="Chưa có lớp nào.",
                     font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP).pack()
            return

        self._lop_btns: dict[str, tk.Frame] = {}

        scroll_frame = tk.Frame(left, bg=BG_APP)
        scroll_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_frame, bg=BG_APP,
                           bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(scroll_frame, orient="vertical",
                           command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_APP)
        cwin = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(cwin, width=e.width)

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>", _on_configure)

        for lop in self._lop_list:
            self._make_lop_card(inner, lop)

    def _make_lop_card(self, parent, lop):
        loai_color = {
            "Lý thuyết": INFO,
            "Thực hành": SUCCESS,
            "Online": ACCENT,
        }.get(lop.loai_hinh, PRIMARY)

        card = tk.Frame(parent, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=12, pady=10, cursor="hand2")
        card.pack(fill="x", pady=(0, 6))

        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x")
        tk.Label(top, text=lop.ma_lop, font=FONT_BOLD,
                 fg=PRIMARY, bg=BG_CARD).pack(side="left")
        tk.Label(top, text=f"  {lop.loai_hinh}",
                 font=FONT_SMALL, fg=TEXT_WHITE,
                 bg=loai_color, padx=6, pady=2).pack(side="right")

        tk.Label(card, text=lop.ten_mon, font=FONT_NORMAL,
                 fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w")
        tk.Label(card, text=f"👥 {lop.si_so_hien_tai}/{lop.si_so_toi_da} SV",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        tk.Label(card, text=lop.lich_hoc_str, font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_CARD,
                 wraplength=200, justify="left").pack(anchor="w")

        self._lop_btns[lop.ma_lop] = card

        def _click(e, l=lop):
            self._chon_lop(l)

        for w in card.winfo_children() + [card]:
            w.bind("<Button-1>", _click)

    def _chon_lop(self, lop):
        # Reset border
        for ma, card in self._lop_btns.items():
            card.config(highlightbackground=BORDER)
        # Highlight lớp chọn
        if lop.ma_lop in self._lop_btns:
            self._lop_btns[lop.ma_lop].config(
                highlightbackground=PRIMARY, highlightthickness=2)

        self._lop_chon = lop
        self._tai_ds_sv(lop)

    # Panel phải: danh sách sinh viên
    def _build_panel_sv(self, parent):
        right = tk.Frame(parent, bg=BG_APP)
        right.pack(side="left", fill="both", expand=True)

        self._lbl_lop = HeadingLabel(right, "Danh sách sinh viên",
                                     bg=BG_APP)
        self._lbl_lop.pack(anchor="w", pady=(0, 4))

        self._lbl_info = MutedLabel(right, "", bg=BG_APP)
        self._lbl_info.pack(anchor="w", pady=(0, 8))

        tbl_frame = tk.Frame(right, bg=BG_APP)
        tbl_frame.pack(fill="both", expand=True)

        self._table = DataTable(tbl_frame, columns=self.COLS_SV, height=22)
        sb = DataTable.them_scrollbar(tbl_frame, self._table)
        self._table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _tai_ds_sv(self, lop):
        self._lbl_lop.config(
            text=f"{lop.ma_lop} — {lop.ten_mon}")
        self._lbl_info.config(
            text=f"GV: {lop.giang_vien}  •  {lop.loai_hinh}  •  "
                 f"Sĩ số: {lop.si_so_hien_tai}/{lop.si_so_toi_da}  •  "
                 f"Lịch: {lop.lich_hoc_str}")

        self._table.xoa_tat_ca()
        sv_svc = self._svcs["sv"]

        for i, mssv in enumerate(lop.danh_sach_mssv):
            sv = sv_svc.tim_theo_khoa(mssv)
            if sv:
                self._table.chen_hang([
                    i + 1, sv.mssv, sv.ho_ten,
                    sv.gioi_tinh, sv.ngay_sinh,
                    sv.email, sv.so_dien_thoai,
                ])
            else:
                self._table.chen_hang([i + 1, mssv, "—", "—", "—", "—", "—"])
