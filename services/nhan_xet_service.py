from models.nhan_xet import NhanXet
from services.base_services import BaseService
from datetime import datetime


class NhanXetService(BaseService):
    def __init__(self, duong_dan_file: str = "data/nhan_xet.json"):
        super().__init__(duong_dan_file)

    def _dict_sang_doi_tuong(self, data: dict) -> NhanXet:
        return NhanXet.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "ma_lop"

    def lay_nhan_xet(self, ma_lop: str) -> NhanXet | None:
        self._tai_du_lieu()
        for nx in self._cache:
            if nx.ma_lop == ma_lop.upper():
                return nx
        return None

    def luu_nhan_xet(self, ma_lop: str, ten_dang_nhap_gv: str,
                     noi_dung: str) -> tuple[bool, str]:
        self._tai_du_lieu()
        cap_nhat_luc = datetime.now().strftime("%H:%M %d/%m/%Y")
        nx = NhanXet(
            ma_lop=ma_lop,
            ten_dang_nhap_gv=ten_dang_nhap_gv,
            noi_dung=noi_dung,
            cap_nhat_luc=cap_nhat_luc,
        )
        for i, item in enumerate(self._cache):
            if item.ma_lop == ma_lop.upper():
                self._cache[i] = nx
                self._luu_du_lieu()
                return True, "Đã cập nhật nhận xét."
        self._cache.append(nx)
        self._luu_du_lieu()
        return True, "Đã lưu nhận xét."