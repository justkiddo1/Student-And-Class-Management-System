from typing import Optional
from models.diem_so import DiemSo
from services.base_services import BaseService


class DiemSoService(BaseService):
    def __init__(self, duong_dan_file: str = "data/diem_so.json"):
        super().__init__(duong_dan_file)

    def _dict_sang_doi_tuong(self, data: dict) -> DiemSo:
        return DiemSo.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "_khoa_to_hop"

    def tim_diem(self, mssv: str, ma_lop: str) -> Optional[DiemSo]:
        self._tai_du_lieu()
        for ds in self._cache:
            if ds.mssv == mssv.upper() and ds.ma_lop == ma_lop.upper():
                return ds
        return None

    def them(self, doi_tuong: DiemSo) -> tuple[bool, str]:
        self._tai_du_lieu()
        ok, msg = doi_tuong.validate()
        if not ok:
            return False, msg
        if self.tim_diem(doi_tuong.mssv, doi_tuong.ma_lop):
            return False, f"Điểm của {doi_tuong.mssv} trong lớp {doi_tuong.ma_lop} đã tồn tại"
        self._cache.append(doi_tuong)
        self._luu_du_lieu()
        return True, "Thêm điểm thành công."

    def cap_nhat(self, doi_tuong: DiemSo) -> tuple[bool, str]:
        self._tai_du_lieu()
        ok, msg = doi_tuong.validate()
        if not ok:
            return False, msg
        for i, ds in enumerate(self._cache):
            if ds.mssv == doi_tuong.mssv and ds.ma_lop == doi_tuong.ma_lop:
                self._cache[i] = doi_tuong
                self._luu_du_lieu()
                return True, "Cập nhật điểm thành công."
        return False, "Không tìm thấy bản ghi điểm."

    def xoa(self, mssv: str, ma_lop: str = None) -> tuple[bool, str]:
        self._tai_du_lieu()
        truoc = len(self._cache)
        if ma_lop:
            self._cache = [ds for ds in self._cache
                           if not (ds.mssv == mssv.upper() and ds.ma_lop == ma_lop.upper())]
        else:
            self._cache = [ds for ds in self._cache if ds.mssv != mssv.upper()]
        if len(self._cache) == truoc:
            return False, "Không tìm thấy bản ghi điểm."
        self._luu_du_lieu()
        return True, "Xóa thành công."

    def lay_diem_theo_sv(self, mssv: str) -> list[DiemSo]:
        self._tai_du_lieu()
        return [ds for ds in self._cache if ds.mssv == mssv.upper()]

    def lay_diem_theo_lop(self, ma_lop: str) -> list[DiemSo]:
        self._tai_du_lieu()
        return [ds for ds in self._cache if ds.ma_lop == ma_lop.upper()]

    def thong_ke_lop(self, ma_lop: str) -> dict:
        danh_sach = self.lay_diem_theo_lop(ma_lop)
        co_diem = [ds for ds in danh_sach if ds.diem_tong_ket is not None]

        if not co_diem:
            return {"ma_lop": ma_lop, "so_luong": 0}

        cac_dtk = [ds.diem_tong_ket for ds in co_diem]
        xep_loai = {}
        for ds in co_diem:
            xl = ds.xep_loai
            xep_loai[xl] = xep_loai.get(xl, 0) + 1

        dau = sum(1 for ds in co_diem if ds.diem_tong_ket >= 5.0)

        return {
            "ma_lop": ma_lop,
            "so_luong": len(co_diem),
            "diem_tb": round(sum(cac_dtk) / len(cac_dtk), 2),
            "diem_cao_nhat": max(cac_dtk),
            "diem_thap_nhat": min(cac_dtk),
            "xep_loai": xep_loai,
            "ti_le_dau": round(dau / len(co_diem) * 100, 1),
            "ti_le_rot": round((len(co_diem) - dau) / len(co_diem) * 100, 1),
        }

    def bang_diem_lop(self, ma_lop: str) -> list[dict]:
        danh_sach = self.lay_diem_theo_lop(ma_lop)
        ket_qua = []
        for ds in danh_sach:
            dtk = ds.diem_tong_ket
            ket_qua.append({
                "MSSV": ds.mssv,
                "Chuyên cần": ds.diem_chuyen_can,
                "Giữa kỳ": ds.diem_giua_ky,
                "Cuối kỳ": ds.diem_cuoi_ky,
                "Tổng kết": dtk,
                "Xếp loại": ds.xep_loai,
                "Kết quả": ds.dau_hay_rot,
            })
        return sorted(ket_qua, key=lambda x: (x["Tổng kết"] or 0), reverse=True)

    def xuat_bang_diem_excel(self, ma_lop: str,
                             duong_dan: str = None) -> str:
        from handlers.excel_handler import ExcelHandler
        duong_dan = duong_dan or f"data/bang_diem_{ma_lop}.xlsx"
        ExcelHandler(duong_dan).ghi(self.bang_diem_lop(ma_lop))
        return duong_dan
