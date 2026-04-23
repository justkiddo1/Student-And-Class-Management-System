import tkinter as tk
import threading
from views.theme import *
from views.widgets import Card, HeadingLabel, MutedLabel


class WeatherWidget(Card):

    def __init__(self, parent, external_svc, **kw):
        super().__init__(parent, **kw)
        self._svc = external_svc
        self._build_ui()
        self._tai_du_lieu()

    def _build_ui(self):
        HeadingLabel(self, "🌤️  Thời tiết hôm nay", bg=BG_CARD).pack(anchor="w")
        MutedLabel(self, "Tp. Hồ Chí Minh", bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        self._content = tk.Frame(self, bg=BG_CARD)
        self._content.pack(fill="x")

        self._lbl_loading = tk.Label(
            self._content, text="⏳ Đang tải...",
            font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD
        )
        self._lbl_loading.pack(anchor="w")

    def _tai_du_lieu(self):
        def _fetch():
            data = self._svc.lay_thoi_tiet("Ho Chi Minh City")
            self.after(0, lambda: self._hien_thi(data))

        threading.Thread(target=_fetch, daemon=True).start()

    def _hien_thi(self, data: dict):
        # Xóa loading
        for w in self._content.winfo_children():
            w.destroy()

        if "loi" in data:
            tk.Label(self._content, text=f"⚠️ {data['loi']}",
                     font=FONT_SMALL, fg=WARNING, bg=BG_CARD,
                     wraplength=200).pack(anchor="w")
            return

        top = tk.Frame(self._content, bg=BG_CARD)
        top.pack(fill="x")
        tk.Label(top, text=data.get("icon_emoji", "🌡️"),
                 font=("Segoe UI Emoji", 32), bg=BG_CARD).pack(side="left")
        right = tk.Frame(top, bg=BG_CARD)
        right.pack(side="left", padx=8)
        tk.Label(right, text=f"{data['nhiet_do']}°C",
                 font=(FONT_FAMILY, 24, "bold"),
                 fg=TEXT_MAIN, bg=BG_CARD).pack(anchor="w")
        tk.Label(right, text=data["mo_ta"],
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")

        tk.Frame(self._content, height=8, bg=BG_CARD).pack()
        details = [
            ("💧 Độ ẩm",   f"{data['do_am']}%"),
            ("💨 Gió",     f"{data['gio']} km/h"),
            ("🌡️ Cảm giác", f"{data['cam_giac']}°C"),
        ]
        for label, value in details:
            row = tk.Frame(self._content, bg=BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(side="left")
            tk.Label(row, text=value, font=FONT_SMALL,
                     fg=TEXT_MAIN, bg=BG_CARD).pack(side="right")

        tk.Label(self._content,
                 text=f"Cập nhật: {data.get('cap_nhat', '')}",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", pady=(6, 0))

        tk.Button(self._content, text="↺ Làm mới",
                  font=FONT_SMALL, fg=PRIMARY, bg=BG_CARD,
                  relief="flat", cursor="hand2",
                  command=self._refresh).pack(anchor="w", pady=(4, 0))

    def _refresh(self):
        for w in self._content.winfo_children():
            w.destroy()
        tk.Label(self._content, text="⏳ Đang tải...",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        # Force refresh cache
        self._svc._lan_cuoi_cap_nhat_tt = None
        self._tai_du_lieu()


class HolidayWidget(Card):

    def __init__(self, parent, external_svc, **kw):
        super().__init__(parent, **kw)
        self._svc = external_svc
        self._build_ui()
        self._tai_du_lieu()

    def _build_ui(self):
        HeadingLabel(self, "🎉  Ngày lễ sắp đến", bg=BG_CARD).pack(anchor="w")
        MutedLabel(self, "Trong 30 ngày tới (crawl từ web)", bg=BG_CARD).pack(anchor="w", pady=(0, 10))
        self._content = tk.Frame(self, bg=BG_CARD)
        self._content.pack(fill="x")
        tk.Label(self._content, text="⏳ Đang crawl...",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")

    def _tai_du_lieu(self):
        def _fetch():
            ds = self._svc.lay_ngay_le_sap_den(30)
            self.after(0, lambda: self._hien_thi(ds))

        threading.Thread(target=_fetch, daemon=True).start()

    def _hien_thi(self, ds: list):
        for w in self._content.winfo_children():
            w.destroy()

        if not ds:
            tk.Label(self._content, text="Không có ngày lễ nào trong 30 ngày tới.",
                     font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
            return

        for item in ds[:6]:   # Hiển thị tối đa 6
            row = tk.Frame(self._content, bg=BG_CARD, pady=4)
            row.pack(fill="x")

            con_lai = item.get("con_lai", 0)
            mau = SUCCESS if con_lai > 7 else (WARNING if con_lai > 2 else DANGER)

            badge = tk.Label(row, text=f"  {con_lai}d  ",
                             font=FONT_SMALL, fg=TEXT_WHITE,
                             bg=mau)
            badge.pack(side="right")

            tk.Label(row, text=item["ten"], font=FONT_SMALL,
                     fg=TEXT_MAIN, bg=BG_CARD).pack(side="left")
            tk.Label(row, text=item["ngay"], font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(side="left", padx=6)

            tk.Frame(self._content, height=1, bg=BORDER).pack(fill="x")

        MutedLabel(self._content, "Nguồn: Wikipedia VN", bg=BG_CARD).pack(anchor="e", pady=(4, 0))