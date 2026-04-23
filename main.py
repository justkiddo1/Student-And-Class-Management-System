import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

from services import (sinh_vien_service, lop_hoc_service,
                      diem_so_service, nguoi_dung_service)
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