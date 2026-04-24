from typing import Optional
from models.nguoi_dung import NguoiDung
from services.base_services import BaseService


class NguoiDungService(BaseService):

    def __init__(self, duong_dan_file: str = "data/nguoi_dung.json"):
        super().__init__(duong_dan_file)
        self._nguoi_dung_hien_tai: Optional[NguoiDung] = None
        self._khoi_tao_admin_mac_dinh()

    def _dict_sang_doi_tuong(self, data: dict) -> NguoiDung:
        return NguoiDung.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "ten_dang_nhap"

    def _khoi_tao_admin_mac_dinh(self):
        if self.dem() == 0:
            admin = NguoiDung.tao_tai_khoan(
                ten_dang_nhap="admin",
                mat_khau="admin123",
                ho_ten="Quản Trị Viên",
                email="admin@school.edu",
                vai_tro=NguoiDung.VAI_TRO_ADMIN,
            )
            self._cache.append(admin)
            self._luu_du_lieu()

    def dang_nhap(self, ten_dang_nhap: str, mat_khau: str) -> tuple[bool, str]:
        nguoi_dung = self.tim_theo_khoa(ten_dang_nhap)
        if not nguoi_dung:
            return False, "Tên đăng nhập không tồn tại."
        if not nguoi_dung.kich_hoat:
            return False, "Tài khoản đã bị khóa."
        if not nguoi_dung.kiem_tra_mat_khau(mat_khau):
            return False, "Mật khẩu không đúng."
        self._nguoi_dung_hien_tai = nguoi_dung
        return True, f"Xin chào, {nguoi_dung.ho_ten}!"

    def dang_xuat(self):
        self._nguoi_dung_hien_tai = None

    @property
    def dang_nhap_roi(self) -> bool:
        return self._nguoi_dung_hien_tai is not None

    @property
    def nguoi_dung_hien_tai(self) -> Optional[NguoiDung]:
        return self._nguoi_dung_hien_tai

    def kiem_tra_quyen(self, hanh_dong: str) -> bool:
        if not self._nguoi_dung_hien_tai:
            return False
        return self._nguoi_dung_hien_tai.co_quyen(hanh_dong)

    def doi_mat_khau(self, ten_dang_nhap: str,
                     mat_khau_cu: str, mat_khau_moi: str) -> tuple[bool, str]:
        nd = self.tim_theo_khoa(ten_dang_nhap)
        if not nd:
            return False, "Tài khoản không tồn tại."
        ok, msg = nd.doi_mat_khau(mat_khau_cu, mat_khau_moi)
        if ok:
            self.cap_nhat(nd)
        return ok, msg

    def khoa_tai_khoan(self, ten_dang_nhap: str) -> tuple[bool, str]:
        nd = self.tim_theo_khoa(ten_dang_nhap)
        if not nd:
            return False, "Tài khoản không tồn tại."
        if nd.vai_tro == NguoiDung.VAI_TRO_ADMIN:
            return False, "Không thể khóa tài khoản admin."
        nd.kich_hoat = False
        self.cap_nhat(nd)
        return True, f"Đã khóa tài khoản '{ten_dang_nhap}'."

    def mo_khoa_tai_khoan(self, ten_dang_nhap: str) -> tuple[bool, str]:
        nd = self.tim_theo_khoa(ten_dang_nhap)
        if not nd:
            return False, "Tài khoản không tồn tại."
        nd.kich_hoat = True
        self.cap_nhat(nd)
        return True, f"Đã mở khóa tài khoản '{ten_dang_nhap}'."

    def lay_danh_sach_user(self) -> list[NguoiDung]:
        return [nd for nd in self.lay_tat_ca()
                if nd.vai_tro == NguoiDung.VAI_TRO_USER]