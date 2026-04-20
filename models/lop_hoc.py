from models.base_model import BaseModel

class LopHoc(BaseModel):
    def __init__(self, ma_lop:str, ten_mon:str, ma_mon:str, giang_vien:str, si_so_toi_da:int = 50, phong_hoc:str="", lich_hoc:str=""):
        self.ma_lop = ma_lop.strip().upper()
        self.ten_mon = ten_mon.strip()
        self.ma_mon = ma_mon.strip().upper()
        self.giang_vien = giang_vien.strip()
        self.si_so_toi_da = int(si_so_toi_da)
        self.phong_hoc = phong_hoc.strip()
        self.lich_hoc = lich_hoc.strip()
        self.danh_sach_mssv: list[str] = []

    # Validation

    def validate(self) -> tuple[bool, str]:
        if not self.ma_lop:
            return False, "Mã lớp không được để trống."

        if not self.ten_mon:
            return False, "Tên môn không được để trống."

        if not self.giang_vien:
            return False, "Giảng viên không được để trống."

        if self.si_so_toi_da <= 0:
            return False, "Sĩ số tối đa phải lớn hơn 0."

        return True,""

    def them_sinh_vien(self,mssv:str) -> tuple[bool, str]:
        if mssv in self.danh_sach_mssv:
            return False, f"Sinh viên {mssv} đã có trong lớp."
        if len(self.danh_sach_mssv) >= self.si_so_toi_da:
            return False, "Lớp đã đầy."
        self.danh_sach_mssv.append(mssv)
        return True, "Thêm thành công."

    def xoa_sinh_vien(self,mssv:str) -> tuple[bool, str]:
        if mssv not in self.danh_sach_mssv:
            return False, f"Sinh viên {mssv} không có trong lớp."
        self.danh_sach_mssv.remove(mssv)
        return True, "Xóa thành công."

    @property
    def si_so_hien_tai(self) -> int:
        return len(self.danh_sach_mssv)

    def to_dict(self) -> dict:
        return {
            "ma_lop": self.ma_lop,
            "ten_mon": self.ten_mon,
            "ma_mon": self.ma_mon,
            "giang_vien": self.giang_vien,
            "si_so_toi_da": self.si_so_toi_da,
            "phong_hoc": self.phong_hoc,
            "lich_hoc": self.lich_hoc,
            "danh_sach_mssv": self.danh_sach_mssv,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LopHoc":
        obj = cls(
            ma_lop=data.get("ma_lop", ""),
            ten_mon=data.get("ten_mon", ""),
            ma_mon=data.get("ma_mon", ""),
            giang_vien=data.get("giang_vien", ""),
            si_so_toi_da=data.get("si_so_toi_da", 50),
            phong_hoc=data.get("phong_hoc", ""),
            lich_hoc=data.get("lich_hoc",""),
        )
        obj.danh_sach_mssv = data.get("danh_sach_mssv", [])
        return obj

    def __str__(self) -> str:
        return (f"[{self.ma_lop}] {self.ten_mon} | GV: {self.giang_vien} " 
                f"| Sĩ số: {self.si_so_hien_tai}/{self.si_so_toi_da}")

    def __repr__(self) -> str:
        return f"LopHoc(ma_lop={self.ma_lop!r}, ten_mon={self.ten_mon!r})"
