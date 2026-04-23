from models.sinh_vien import SinhVien
from services.base_services import BaseService


class SinhVienService(BaseService):
    def __init__(self, duong_dan_file:str = "data/sinh_vien.json"):
        super.__init__(duong_dan_file)

    def _dict_sang_doi_tuong(self, data: dict) -> "SinhVien":
        return SinhVien.from_dict(data)

    def _khoa_chinh(self) -> str:
        return "mssv"

    def tim_theo_ten(self,tu_khoa:str) -> list[SinhVien]:
        self._tai_du_lieu()
        tu_khoa = tu_khoa.strip().lower()
        return [sv for sv in self._cache if tu_khoa in sv.ho_ten.lower()]

    def tim_theo_lop(self, ma_lop:str) -> list[SinhVien]:
        self._tai_du_lieu()
        return [sv for sv in self._cache if sv.ma_lop.upper() == ma_lop.upper()]

    def tim_theo_email(self, email:str) -> "SinhVien" | None:
        self._tai_du_lieu()
        for sv in self._cache:
            if sv.email == email.lower():
                return sv
        return None

    def tim_nang_cao(self,tu_khoa:str = "", ma_lop:str = "", gioi_tinh:str = "") -> list[SinhVien]:
        self._tai_du_lieu()
        ket_qua = self._cache
        if tu_khoa:
            tu_khoa = tu_khoa.strip().lower()
            ket_qua = [sv for sv in ket_qua if tu_khoa in sv.ho_ten.lower() or tu_khoa in sv.mssv.lower()]

        if ma_lop:
            ket_qua = [sv for sv in ket_qua if sv.ma_lop.upper() == ma_lop.upper()]

        if gioi_tinh:
            ket_qua = [sv for sv in ket_qua if sv.gioi_tinh == gioi_tinh]

        return ket_qua

    def xuat_csv(self, duong_dan:str = "data/sinh_vien.csv"):
        from handlers.csv_handler import CSVHandler
        CSVHandler(duong_dan).ghi([sv.to_dict() for sv in self.lay_tat_ca()])

    def xuat_txt(self, duong_dan: str = "data/sinh_vien.txt"):
        from handlers.txt_handler import TXTHandler
        TXTHandler(duong_dan).ghi([sv.to_dict() for sv in self.lay_tat_ca()])

    def xuat_excel(self, duong_dan: str = "data/sinh_vien.xlsx"):
        from handlers.excel_handler import ExcelHandler
        ExcelHandler(duong_dan).ghi([sv.to_dict() for sv in self.lay_tat_ca()])

    def nhap_tu_csv(self, duong_dan: str) -> tuple[int, int, list[str]]:
        from handlers.csv_handler import CSVHandler
        du_lieu = CSVHandler(duong_dan).doc()
        thanh_cong, that_bai, loi = 0, 0, []
        for d in du_lieu:
            sv = SinhVien.from_dict(d)
            ok, msg = self.them(sv)
            if ok:
                thanh_cong += 1
            else:
                that_bai += 1
                loi.append(f"{d.get('mssv', '?')}: {msg}")
        return thanh_cong, that_bai, loi

    def thong_ke_theo_lop(self) -> dict[str, int]:
        self._tai_du_lieu()
        thong_ke = {}
        for sv in self._cache:
            thong_ke[sv.ma_lop] = thong_ke.get(sv.ma_lop, 0) + 1
        return thong_ke

    def thong_ke_gioi_tinh(self) -> dict[str, int]:
        self._tai_du_lieu()
        thong_ke = {}
        for sv in self._cache:
            thong_ke[sv.gioi_tinh] = thong_ke.get(sv.gioi_tinh, 0) + 1
        return thong_ke