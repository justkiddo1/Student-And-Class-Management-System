from models.diem_danh import DiemDanh
from services.base_services import BaseService
from datetime import date


class DiemDanhService(BaseService):
    def __init__(self, duong_dan_file: str = "data/diem_danh.json"):
        super().__init__(duong_dan_file)

    def _dict_sang_doi_tuong(self, data: dict) -> DiemDanh:
        return DiemDanh.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "khoa_chinh"   

    # Tìm kiếm
    def tim_buoi(self, ma_lop: str, ngay: str, tiet: str) -> DiemDanh | None:
        self._tai_du_lieu()
        for dd in self._cache:
            if dd.ma_lop == ma_lop.upper() and dd.ngay == ngay and dd.tiet == tiet:
                return dd
        return None

    def lay_theo_lop(self, ma_lop: str) -> list[DiemDanh]:
        self._tai_du_lieu()
        return [dd for dd in self._cache
                if dd.ma_lop == ma_lop.upper()]

    def lay_theo_lop_va_thang(self, ma_lop: str,
                               thang: int, nam: int) -> list[DiemDanh]:
        self._tai_du_lieu()
        ket_qua = []
        for dd in self._cache:
            if dd.ma_lop != ma_lop.upper():
                continue
            try:
                parts = dd.ngay.split("/")
                if int(parts[1]) == thang and int(parts[2]) == nam:
                    ket_qua.append(dd)
            except Exception:
                pass
        return sorted(ket_qua, key=lambda d: (
            d.ngay.split("/")[2],
            d.ngay.split("/")[1],
            d.ngay.split("/")[0],
        ))

    # Lưu điểm danh
    def luu_buoi(self, dd: DiemDanh) -> tuple[bool, str]:
        """Thêm mới hoặc cập nhật buổi điểm danh."""
        self._tai_du_lieu()
        for i, item in enumerate(self._cache):
            if (item.ma_lop == dd.ma_lop
                    and item.ngay == dd.ngay
                    and item.tiet == dd.tiet):
                self._cache[i] = dd
                self._luu_du_lieu()
                return True, "Cập nhật điểm danh thành công."
        self._cache.append(dd)
        self._luu_du_lieu()
        return True, "Lưu điểm danh thành công."

    def xoa_buoi(self, ma_lop: str, ngay: str, tiet: str) -> tuple[bool, str]:
        self._tai_du_lieu()
        truoc = len(self._cache)
        self._cache = [dd for dd in self._cache
                       if not (dd.ma_lop == ma_lop.upper()
                               and dd.ngay == ngay
                               and dd.tiet == tiet)]
        if len(self._cache) == truoc:
            return False, "Không tìm thấy buổi điểm danh."
        self._luu_du_lieu()
        return True, "Đã xóa buổi điểm danh."

    # Thống kê vắng mặt sinh viên
    def thong_ke_vang_theo_sv(self, ma_lop: str) -> dict[str, dict]:
        """
        Trả về {mssv: {"co_mat": n, "vang": n, "phep": n, "tre": n}}
        """
        ds = self.lay_theo_lop(ma_lop)
        result: dict[str, dict] = {}
        for dd in ds:
            for mssv, tt in dd.ds_trang_thai.items():
                if mssv not in result:
                    result[mssv] = {"Có mặt": 0, "Vắng": 0,
                                    "Vắng có phép": 0, "Trễ": 0}
                if tt in result[mssv]:
                    result[mssv][tt] += 1
        return result