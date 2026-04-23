from models.lop_hoc import LopHoc
from services.base_services import BaseService

class LopHocService(BaseService):
    def __init__(self,duong_dan_file:str = "data/lop_hoc.json"):
        super().__init__(duong_dan_file)

    def _dict_sang_doi_tuong(self, data: dict) -> LopHoc:
        return LopHoc.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "ma_lop"


    def them_sv_vao_lop(self,ma_lop:str, mssv:str) -> tuple[bool,str]:
        lop = self.tim_theo_khoa(ma_lop)
        if not lop:
            return False, f"Không tìm thấy lớp '{ma_lop}'."
        ok ,msg = lop.them_sinh_vien(mssv)
        if ok:
            self._luu_du_lieu()
        return ok,msg

    def xoa_sv_khoi_lop(self,ma_lop:str,mssv:str) -> tuple[bool,str]:
        lop = self.tim_theo_khoa(ma_lop)
        if not lop:
            return False, f"Không tìm thấy lớp '{ma_lop}'"
        ok,msg = lop.xoa_sinh_vien(mssv)
        if ok:
            self._luu_du_lieu()
        return ok,msg

    def lay_ds_mssv(self,ma_lop:str) -> list[str]:
        lop = self.tim_theo_khoa(ma_lop)
        return lop.danh_sach_mssv if lop else []

    def tim_theo_giang_vien(self, ten_gv:str) -> list[LopHoc]:
        self._tai_du_lieu()
        ten_gv = ten_gv.strip().lower()
        return [lop for lop in self._cache if ten_gv in lop.giang_vien.lower()]

    def tim_theo_mon(self,ten_mon:str) -> list[LopHoc]:
        self._tai_du_lieu()
        ten_mon = ten_mon.strip().lower()
        return [lop for lop in self._cache if ten_mon in lop.ten_mon.lower()]

    def lay_lop_con_cho(self) -> list[LopHoc]:
        self._tai_du_lieu()
        return [lop for lop in self._cache if lop.si_so_hien_tai < lop.si_so_toi_da]

    def thong_ke_si_so(self) -> list[dict]:
        self._tai_du_lieu()
        return [
            {
                "ma_lop": lop.ma_lop,
                "ten_mon": lop.ten_mon,
                "si_so_hien_tai": lop.si_so_hien_tai,
                "si_so_toi_da": lop.si_so_toi_da,
            }
            for lop in self._cache
        ]

    def xuat_csv(self, duong_dan: str = "data/lop_hoc.csv"):
        from handlers.csv_handler import CSVHandler
        CSVHandler(duong_dan).ghi([lop.to_dict() for lop in self.lay_tat_ca()])

    def xuat_excel(self, duong_dan: str = "data/lop_hoc.xlsx"):
        from handlers.excel_handler import ExcelHandler
        ExcelHandler(duong_dan).ghi([lop.to_dict() for lop in self.lay_tat_ca()])

