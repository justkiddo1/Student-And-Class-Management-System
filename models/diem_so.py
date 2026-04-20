from models.base_model import BaseModel


class DiemSo(BaseModel):
    HE_SO_CHUYEN_CAN = 0.1
    HE_SO_GIUA_KY = 0.3
    HE_SO_CUOI_KY = 0.6

    def __init__(self, mssv: str, ma_lop: str,
                 diem_chuyen_can: float = None,
                 diem_giua_ky: float = None,
                 diem_cuoi_ky: float = None):
        self.mssv = mssv.strip().upper()
        self.ma_lop = ma_lop.strip().upper()
        self.diem_chuyen_can = diem_chuyen_can  # 0 - 10
        self.diem_giua_ky = diem_giua_ky  # 0 - 10
        self.diem_cuoi_ky = diem_cuoi_ky  # 0 - 10

    # Validation
    def validate(self) -> tuple[bool, str]:
        if not self.mssv:
            return False, "MSSV không được để trống."
        if not self.ma_lop:
            return False, "Mã lớp không được để trống."
        for ten, gia_tri in [
            ("Chuyên cần", self.diem_chuyen_can),
            ("Giữa kỳ", self.diem_giua_ky),
            ("Cuối kỳ", self.diem_cuoi_ky),
        ]:
            if gia_tri is not None and not (0 <= gia_tri <= 10):
                return False, f"Điểm {ten} phải từ 0 đến 10."
        return True, ""

    @property
    def diem_tong_ket(self) -> float | None:
        if any(d is None for d in [self.diem_chuyen_can,
                                   self.diem_giua_ky,
                                   self.diem_cuoi_ky]):
            return None
        tong = (self.diem_chuyen_can * self.HE_SO_CHUYEN_CAN
                + self.diem_giua_ky * self.HE_SO_GIUA_KY
                + self.diem_cuoi_ky * self.HE_SO_CUOI_KY)
        return round(tong, 2)

    @property
    def xep_loai(self) -> str:
        dtk = self.diem_tong_ket
        if dtk is None:
            return "Chưa có điểm"
        if dtk >= 8.5:
            return "Giỏi"
        if dtk >= 7.0:
            return "Khá"
        if dtk >= 5.0:
            return "Trung bình"
        return "Yếu"

    @property
    def dau_hay_rot(self) -> str:
        dtk = self.diem_tong_ket
        if dtk is None:
            return "Chưa xác định"
        return "Đạt" if dtk >= 5.0 else "Không đạt"

    def to_dict(self) -> dict:
        return {
            "mssv": self.mssv,
            "ma_lop": self.ma_lop,
            "diem_chuyen_can": self.diem_chuyen_can,
            "diem_giua_ky": self.diem_giua_ky,
            "diem_cuoi_ky": self.diem_cuoi_ky,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiemSo":
        return cls(
            mssv=data.get("mssv", ""),
            ma_lop=data.get("ma_lop", ""),
            diem_chuyen_can=data.get("diem_chuyen_can"),
            diem_giua_ky=data.get("diem_giua_ky"),
            diem_cuoi_ky=data.get("diem_cuoi_ky"),
        )

    def __str__(self) -> str:
        dtk = self.diem_tong_ket
        dtk_str = f"{dtk:.2f}" if dtk is not None else "N/A"
        return (f"[{self.mssv} | {self.ma_lop}] "
                f"CC:{self.diem_chuyen_can} GK:{self.diem_giua_ky} "
                f"CK:{self.diem_cuoi_ky} → TK:{dtk_str} ({self.xep_loai})")

    def __repr__(self) -> str:
        return f"DiemSo(mssv={self.mssv!r}, ma_lop={self.ma_lop!r})"
