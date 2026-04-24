import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

from services.sinh_vien_service import SinhVienService as sinh_vien_service
from services.lop_hoc_service import LopHocService as lop_hoc_service
from services.diem_so_service import DiemSoService as diem_so_service
from services.nguoi_dung_service import NguoiDungService as nguoi_dung_service
from views.login_view import LoginView
from views.main_view import MainView


def khoi_chay():
    services = {
        "sv":   sinh_vien_service("data/sinh_vien.json"),
        "lop":  lop_hoc_service("data/lop_hoc.json"),
        "diem": diem_so_service("data/diem_so.json"),
        "nd":   nguoi_dung_service("data/nguoi_dung.json"),
    }

    root = tk.Tk()
    root.withdraw()

    def on_dang_nhap_thanh_cong():
        root.destroy()
        app = MainView(services)
        app.mainloop()

    login = LoginView(services["nd"], on_success=on_dang_nhap_thanh_cong)
    login.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()


if __name__ == "__main__":
    khoi_chay()