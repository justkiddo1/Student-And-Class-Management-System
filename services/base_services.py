from abc import ABC, abstractmethod
from handlers.json_handler import JSONHandler


class BaseService(ABC):
    def __init__(self, duong_dan_file: str):
        self._handler = JSONHandler(duong_dan_file)
        self._cache: list = []
        self._da_tai = False

    @abstractmethod
    def _dict_sang_doi_tuong(self, data: dict):
        pass

    @abstractmethod
    def _khoa_chinh(self) -> str:
        pass

    def _tai_du_lieu(self, force: bool = False):
        if not self._da_tai or force:
            danh_sach_dict = self._handler.doc()
            self._cache = [self._dict_sang_doi_tuong(d) for d in danh_sach_dict]
            self._da_tai = True

    def _luu_du_lieu(self):
        self._handler.ghi([obj.to_dict() for obj in self._cache])

    def lam_moi(self):
        self._tai_du_lieu(force=True)

    def lay_tat_ca(self) -> list:
        self._tai_du_lieu()
        return list(self._cache)

    def tim_theo_khoa(self, gia_tri: str):
        self._tai_du_lieu()
        khoa = self._khoa_chinh()
        for obj in self._cache:
            if str(getattr(obj, khoa, "")).upper() == str(gia_tri).upper():
                return obj
        return None

    def them(self, doi_tuong) -> tuple[bool, str]:
        self._tai_du_lieu()
        ok, msg = doi_tuong.validate()
        if not ok:
            return False, msg

        khoa = self._khoa_chinh()
        gia_tri_khoa = getattr(doi_tuong, khoa)
        if self.tim_theo_khoa(gia_tri_khoa):
            return False, f"{khoa.upper()} '{gia_tri_khoa}' đã tồn tại."

        self._cache.append(doi_tuong)
        self._luu_du_lieu()
        return True, f"Thêm thành công."

    def cap_nhat(self, doi_tuong) -> tuple[bool, str]:
        self._tai_du_lieu()
        ok, msg = doi_tuong.validate()
        if not ok:
            return False, msg

        khoa = self._khoa_chinh()
        gia_tri_khoa = getattr(doi_tuong, khoa)
        for i, obj in enumerate(self._cache):
            if str(getattr(obj, khoa, "")).upper() == str(gia_tri_khoa).upper():
                self._cache[i] = doi_tuong
                self._luu_du_lieu()
                return True, "Cập nhật thành công."
        return False, f"Không tìm thấy '{gia_tri_khoa}'."

    def xoa(self, gia_tri_khoa: str) -> tuple[bool, str]:
        self._tai_du_lieu()
        khoa = self._khoa_chinh()
        truoc = len(self._cache)
        self._cache = [obj for obj in self._cache
                       if str(getattr(obj, khoa, "")).upper() != str(gia_tri_khoa).upper()]
        if len(self._cache) == truoc:
            return False, f"Không tìm thấy '{gia_tri_khoa}'."
        self._luu_du_lieu()
        return True, "Xóa thành công."

    def dem(self) -> int:
        self._tai_du_lieu()
        return len(self._cache)