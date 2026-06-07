from models.base_model import BaseModel


class DiemSo(BaseModel):
    HE_SO_CHUYEN_CAN = 0.1
    HE_SO_KT1 = 0.1
    HE_SO_KT2 = 0.1
    HE_SO_TIEU_LUAN = 0.1
    HE_SO_CUOI_KY = 0.6

    def __init__(self, mssv: str, ma_lop: str,
                 diem_chuyen_can: float = None,
                 diem_kt1: float = None,
                 diem_kt2: float = None,
                 diem_tieu_luan: float = None,
                 diem_cuoi_ky: float = None):
        self.mssv = mssv.strip().upper()
        self.ma_lop = ma_lop.strip().upper()
        self.diem_chuyen_can = diem_chuyen_can
        self.diem_kt1 = diem_kt1
        self.diem_kt2 = diem_kt2
        self.diem_tieu_luan = diem_tieu_luan
        self.diem_cuoi_ky = diem_cuoi_ky

    @property
    def diem_giua_ky(self) -> float | None:
        parts = [self.diem_kt1, self.diem_kt2, self.diem_tieu_luan]
        co = [d for d in parts if d is not None]
        if not co:
            return None
        return round(sum(co) / len(co), 2)

    @property
    def diem_tong_ket(self) -> float | None:
        gk = self.diem_giua_ky
        if any(d is None for d in [self.diem_chuyen_can, gk, self.diem_cuoi_ky]):
            return None
        return round(
            self.diem_chuyen_can * self.HE_SO_CHUYEN_CAN
            + gk * (self.HE_SO_KT1 + self.HE_SO_KT2 + self.HE_SO_TIEU_LUAN)
            + self.diem_cuoi_ky * self.HE_SO_CUOI_KY,
            2
        )

    @property
    def xep_loai(self) -> str:
        dtk = self.diem_tong_ket
        if dtk is None:
            return "Chưa có điểm"
        if dtk >= 9.0:  return "Xuất sắc"
        if dtk >= 8.0:  return "Giỏi"
        if dtk >= 7.0:  return "Khá"
        if dtk >= 5.0:  return "Trung bình"
        return "Yếu"

    @property
    def dau_hay_rot(self) -> str:
        dtk = self.diem_tong_ket
        if dtk is None:
            return "Chưa xác định"
        return "Đạt" if dtk >= 5.0 else "Không đạt"

    # Validation
    def validate(self) -> tuple[bool, str]:
        if not self.mssv:
            return False, "MSSV không được để trống."
        if not self.ma_lop:
            return False, "Mã lớp không được để trống."
        for ten, val in [
            ("Chuyên cần", self.diem_chuyen_can),
            ("Kiểm tra 1", self.diem_kt1),
            ("Kiểm tra 2", self.diem_kt2),
            ("Tiểu luận", self.diem_tieu_luan),
            ("Cuối kỳ", self.diem_cuoi_ky),
        ]:
            if val is not None:
                if val < 0:
                    return False, f"Điểm {ten} không được âm."
                if val > 10:
                    return False, f"Điểm {ten} không được vượt quá 10."
        return True, ""

    # Serialization
    def to_dict(self) -> dict:
        return {
            "mssv": self.mssv,
            "ma_lop": self.ma_lop,
            "diem_chuyen_can": self.diem_chuyen_can,
            "diem_kt1": self.diem_kt1,
            "diem_kt2": self.diem_kt2,
            "diem_tieu_luan": self.diem_tieu_luan,
            "diem_cuoi_ky": self.diem_cuoi_ky,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiemSo":
        diem_gk_cu = data.get("diem_giua_ky")
        return cls(
            mssv=data.get("mssv", ""),
            ma_lop=data.get("ma_lop", ""),
            diem_chuyen_can=data.get("diem_chuyen_can"),
            diem_kt1=data.get("diem_kt1", diem_gk_cu),
            diem_kt2=data.get("diem_kt2"),
            diem_tieu_luan=data.get("diem_tieu_luan"),
            diem_cuoi_ky=data.get("diem_cuoi_ky"),
        )

    def __str__(self) -> str:
        dtk = self.diem_tong_ket
        return (f"[{self.mssv}|{self.ma_lop}] "
                f"CC:{self.diem_chuyen_can} "
                f"KT1:{self.diem_kt1} KT2:{self.diem_kt2} TL:{self.diem_tieu_luan} "
                f"CK:{self.diem_cuoi_ky} "
                f"→ GK:{self.diem_giua_ky} TK:{f'{dtk:.2f}' if dtk else 'N/A'} "
                f"({self.xep_loai})")

    def __repr__(self) -> str:
        return f"DiemSo(mssv={self.mssv!r}, ma_lop={self.ma_lop!r})"
