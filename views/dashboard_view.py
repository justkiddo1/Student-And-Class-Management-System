# views/dashboard_view.py
import tkinter as tk
from views.theme import *
from views.widgets import Card, HeadingLabel, MutedLabel


class DashboardView(tk.Frame):

    def __init__(self, parent, services: dict, on_navigate=None):
        super().__init__(parent, bg=BG_APP)
        self._svcs = services
        self._on_navigate = on_navigate
        # Khởi tạo external service (API + Crawl)
        from services.api_service import ExternalDataService
        self._ext_svc = ExternalDataService()
        self._build_ui()

    def _build_ui(self):
        # ── Tiêu đề ─────────────────────────────────────────────────
        tk.Label(self, text="Dashboard", font=FONT_TITLE,
                 fg=TEXT_MAIN, bg=BG_APP).pack(anchor="w")
        tk.Label(self, text="Tổng quan hệ thống quản lý",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP).pack(anchor="w", pady=(0, 16))

        # ── Thẻ thống kê ─────────────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG_APP)
        cards_frame.pack(fill="x", pady=(0, 16))

        stats = [
            ("👤", "Sinh viên",  str(self._svcs["sv"].dem()),   PRIMARY,  "sinh_vien"),
            ("🏫", "Lớp học",    str(self._svcs["lop"].dem()),  SUCCESS,  "lop_hoc"),
            ("📊", "Điểm số",    str(self._svcs["diem"].dem()), INFO,     "diem_so"),
            ("⚙",  "Tài khoản", str(self._svcs["nd"].dem()),   ACCENT,   "nguoi_dung"),
        ]
        for i, (icon, label, value, color, tab) in enumerate(stats):
            self._make_stat_card(cards_frame, icon, label, value, color, tab, i)

        # ── Hai cột dưới ─────────────────────────────────────────────
        row2 = tk.Frame(self, bg=BG_APP)
        row2.pack(fill="both", expand=True)

        self._build_recent_students(row2)
        self._build_class_stats(row2)

    def _make_stat_card(self, parent, icon, label, value, color, tab, col):
        card = tk.Frame(parent, bg=color, padx=20, pady=16,
                        cursor="hand2", relief="flat")
        card.grid(row=0, column=col, padx=(0, 10) if col < 3 else 0,
                  sticky="ew")
        parent.columnconfigure(col, weight=1)

        tk.Label(card, text=icon, font=("Segoe UI Emoji", 24),
                 bg=color, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(card, text=value, font=(FONT_FAMILY, 26, "bold"),
                 bg=color, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(card, text=label, font=FONT_SMALL,
                 bg=color, fg="rgba(255,255,255,0.8)").pack(anchor="w")

        # Click để chuyển tab
        for w in card.winfo_children() + [card]:
            w.bind("<Button-1>", lambda e, t=tab: self._on_navigate and self._on_navigate(t))

    def _build_recent_students(self, parent):
        card = Card(parent)
        card.pack(side="left", fill="both", expand=True,
                  padx=(0, 8), pady=0)

        HeadingLabel(card, "Sinh viên mới nhất", bg=BG_CARD).pack(anchor="w")
        MutedLabel(card, "5 sinh viên gần đây", bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        ds = self._svcs["sv"].lay_tat_ca()[-5:][::-1]
        if not ds:
            tk.Label(card, text="Chưa có dữ liệu", font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack()
            return

        for sv in ds:
            row = tk.Frame(card, bg=BG_CARD, pady=4)
            row.pack(fill="x")
            tk.Label(row, text="👤", font=("Segoe UI Emoji", 11),
                     bg=BG_CARD).pack(side="left", padx=(0, 8))
            tk.Label(row, text=sv.ho_ten, font=FONT_BOLD,
                     fg=TEXT_MAIN, bg=BG_CARD).pack(side="left")
            tk.Label(row, text=sv.mssv, font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(side="right")
            tk.Frame(card, height=1, bg=BORDER).pack(fill="x")

    def _build_class_stats(self, parent):
        card = Card(parent)
        card.pack(side="left", fill="both", expand=True,
                  padx=(8, 0), pady=0)

        HeadingLabel(card, "Sĩ số các lớp", bg=BG_CARD).pack(anchor="w")
        MutedLabel(card, "Tình trạng lớp học", bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        ds_lop = self._svcs["lop"].thong_ke_si_so()
        if not ds_lop:
            tk.Label(card, text="Chưa có dữ liệu", font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack()
            return

        for item in ds_lop:
            row = tk.Frame(card, bg=BG_CARD, pady=6)
            row.pack(fill="x")

            info = tk.Frame(row, bg=BG_CARD)
            info.pack(fill="x")
            tk.Label(info, text=item["ma_lop"], font=FONT_BOLD,
                     fg=TEXT_MAIN, bg=BG_CARD).pack(side="left")
            pct = int(item["si_so_hien_tai"] / item["si_so_toi_da"] * 100)
            tk.Label(info, text=f'{item["si_so_hien_tai"]}/{item["si_so_toi_da"]}',
                     font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(side="right")

            # Progress bar
            bar_bg = tk.Frame(row, bg=BORDER, height=6)
            bar_bg.pack(fill="x", pady=(2, 0))
            color = SUCCESS if pct < 80 else (WARNING if pct < 95 else DANGER)
            tk.Frame(bar_bg, bg=color, height=6,
                     width=int(bar_bg.winfo_reqwidth() * pct / 100)).pack(side="left")
            tk.Frame(card, height=1, bg=BORDER).pack(fill="x")