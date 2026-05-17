import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

from services.sinh_vien_service import SinhVienService
from services.lop_hoc_service import LopHocService
from services.diem_so_service import DiemSoService
from services.nguoi_dung_service import NguoiDungService
from services.diem_danh_service import DiemDanhService
from services.nhan_xet_service import NhanXetService
from views.login_view import LoginView


def khoi_chay():
    services = {
        "sv":   SinhVienService("data/sinh_vien.json"),
        "lop":  LopHocService("data/lop_hoc.json"),
        "diem": DiemSoService("data/diem_so.json"),
        "nd":   NguoiDungService("data/nguoi_dung.json"),
        "dd":   DiemDanhService("data/diem_danh.json"),
        "nx":   NhanXetService("data/nhan_xet.json"),
    }

    root = tk.Tk()
    root.withdraw()

    def on_dang_nhap_thanh_cong():
        root.destroy()
        nd = services["nd"].nguoi_dung_hien_tai

        if nd and nd.la_admin:
            # Admin → giao diện quản trị đầy đủ
            from views.main_view import MainView
            app = MainView(services)
        else:
            # Giáo viên → giao diện riêng
            from views.giao_vien_main_view import GiaoVienMainView
            app = GiaoVienMainView(services, nd)

        app.mainloop()

    login = LoginView(services["nd"], on_success=on_dang_nhap_thanh_cong)
    login.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()


if __name__ == "__main__":
    khoi_chay()