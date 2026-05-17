import tkinter as tk
from datetime import date
from views.theme import *
from views.widgets import MutedLabel

_WEEKDAY_MAP = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5",
                4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}


def _thu_hom_nay() -> str:
    return _WEEKDAY_MAP[date.today().weekday()]


def _ngay_hom_nay() -> str:
    return date.today().strftime("%d/%m/%Y")


class LichDayView(tk.Frame):

    def __init__(self, parent, lop_cua_toi: list,
                 on_click_lop=None, **kw):
        super().__init__(parent, bg=BG_APP, **kw)
        self._lop_list = lop_cua_toi
        self._on_click = on_click_lop
        self._build_ui()

    def _build_ui(self):
        thu_hom_nay = _thu_hom_nay()

        # Header
        hdr = tk.Frame(self, bg=BG_APP)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text="📅  Lịch dạy trong tuần",
                 font=FONT_TITLE, fg=TEXT_MAIN, bg=BG_APP).pack(side="left")
        MutedLabel(hdr,
                   f"Hôm nay: {thu_hom_nay}  —  {_ngay_hom_nay()}",
                   bg=BG_APP).pack(side="left", padx=16, pady=(6, 0))

        if not self._lop_list:
            tk.Label(self, text="Bạn chưa được phân công lớp nào.",
                     font=FONT_NORMAL, fg=TEXT_MUTED, bg=BG_APP).pack(pady=40)
            return

        # Thống kê nhanh
        tong_buoi = sum(len(lop.lich_hoc) for lop in self._lop_list)
        tk.Label(self,
                 text=f"Tổng {len(self._lop_list)} lớp  •  {tong_buoi} buổi/tuần",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_APP).pack(anchor="w",
                                                                 pady=(0, 8))

        # Bảng tuần
        THU_LIST = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]

        thu_map: dict[str, list] = {t: [] for t in THU_LIST}
        for lop in self._lop_list:
            for buoi in lop.lich_hoc:
                thu_map[buoi.thu].append((lop, buoi))

        max_rows = max((len(v) for v in thu_map.values()), default=1)

        grid = tk.Frame(self, bg=BG_APP)
        grid.pack(fill="both", expand=True)

        # Header hàng
        for col, thu in enumerate(THU_LIST):
            is_today = thu == thu_hom_nay
            bg = PRIMARY if is_today else BG_SIDEBAR
            cell = tk.Frame(grid, bg=bg, padx=6, pady=6)
            cell.grid(row=0, column=col, sticky="ew", padx=2, pady=(0, 2))
            grid.columnconfigure(col, weight=1)
            lbl = tk.Label(cell, text=thu, font=FONT_BOLD,
                           fg=TEXT_WHITE, bg=bg)
            lbl.pack()
            if is_today:
                tk.Label(cell, text="◀ hôm nay",
                         font=FONT_SMALL, fg="#90CAF9", bg=bg).pack()

        # Các ô nội dung
        for row in range(max_rows):
            for col, thu in enumerate(THU_LIST):
                items = thu_map[thu]
                is_today = thu == thu_hom_nay
                bg_cell = PRIMARY_LITE if is_today else (
                    BG_CARD if col % 2 == 0 else BG_TABLE_ODD)

                if row < len(items):
                    lop, buoi = items[row]
                    self._make_lop_cell(grid, lop, buoi,
                                        row + 1, col, bg_cell, is_today)
                else:
                    blank = tk.Frame(grid, bg=bg_cell,
                                     highlightbackground=BORDER,
                                     highlightthickness=1)
                    blank.grid(row=row + 1, column=col,
                               sticky="nsew", padx=2, pady=2)

            grid.rowconfigure(row + 1, weight=1)

    def _make_lop_cell(self, parent, lop, buoi,
                       row, col, bg, highlight):
        cell = tk.Frame(parent, bg=bg, padx=8, pady=8,
                        highlightbackground=PRIMARY if highlight else BORDER,
                        highlightthickness=1 if highlight else 1,
                        cursor="hand2")
        cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        # Mã lớp + môn
        tk.Label(cell, text=lop.ma_lop, font=FONT_BOLD,
                 fg=PRIMARY, bg=bg).pack(anchor="w")
        tk.Label(cell, text=lop.ten_mon, font=FONT_SMALL,
                 fg=TEXT_MAIN, bg=bg, wraplength=140,
                 justify="left").pack(anchor="w")

        # Tiết + giờ
        tk.Label(cell, text=buoi.tiet, font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=bg).pack(anchor="w")
        tk.Label(cell, text=f"{buoi.gio}", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=bg).pack(anchor="w")

        # Phòng
        if buoi.phong:
            tk.Label(cell, text=f"Phòng {buoi.phong}",
                     font=FONT_SMALL, fg=TEXT_MUTED, bg=bg).pack(anchor="w")

        # Sĩ số
        tk.Label(cell, text=f"👥 {lop.si_so_hien_tai} SV",
                 font=FONT_SMALL, fg=SUCCESS, bg=bg).pack(anchor="w")

        def _click(e, ml=lop.ma_lop):
            if self._on_click:
                self._on_click(ml)

        for w in cell.winfo_children() + [cell]:
            w.bind("<Button-1>", _click)
            # Hover effect
            w.bind("<Enter>", lambda e, c=cell: c.config(
                highlightbackground=PRIMARY, highlightthickness=2))
            w.bind("<Leave>", lambda e, c=cell, h=highlight: c.config(
                highlightbackground=PRIMARY if h else BORDER,
                highlightthickness=1))
