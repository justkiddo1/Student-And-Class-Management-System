import tkinter as tk
from views.diem_so_view import DiemSoView


class NhapDiemView(tk.Frame):

    def __init__(self, parent, services: dict,
                 lop_cua_toi: list, statusbar, **kw):
        super().__init__(parent, bg="white", **kw)

        # Tạo DiemSoView với lọc lớp của GV
        self._view = DiemSoView(
            self,
            services=services,
            statusbar=statusbar,
            lop_filter=[lop.ma_lop for lop in lop_cua_toi],
        )
        self._view.pack(fill="both", expand=True)