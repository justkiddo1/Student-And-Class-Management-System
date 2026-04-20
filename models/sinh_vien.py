import re
from datetime import datetime
from models.base_model import BaseModel


class SinhVien(BaseModel):
    def __init__(self, mssv: str, ho_ten: str, ngay_sinh: str, gioi_tinh: str, email: str, so_dien_thoai: str,
                 ma_lop: str, dia_chi: str = ""):
        self.mssv = mssv.strip().upper()
        self.ho_ten = ho_ten.strip()
        self.ngay_sinh = ngay_sinh
        self.gioi_tinh = gioi_tinh
        self.email = email.strip().lower()
        self.so_dien_thoai = so_dien_thoai.strip()
        self.ma_lop = ma_lop.strip().upper()
        self.dia_chi = dia_chi.strip()

    # Validation

    def validate(self) -> tuple[bool, str]:
        if not self.mssv:
            return False, "Mã số sinh viên không được để trống."

        if not self.ho_ten:
            return False, "Họ tên không được để trống."

        if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", self.ngay_sinh):
            return False, "Ngày sinh phải có định dạng DD/MM/YYYY."

        try:
            datetime.strptime(self.ngay_sinh, "%d/%m/%Y")
        except ValueError:
            return False, "Ngày sinh không hợp lệ."
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", self.email):
            return False, "Email không hợp lệ."
        if not re.fullmatch(r"0\d{9}", self.so_dien_thoai):
            return False, "Số điện thoại phải bắt đầu bằng 0 và có 10 chữ số."
        if not self.ma_lop:
            return False, "Mã lớp không được để trống."
        return True, ""

    def to_dict(self) -> dict:
        return {
            "mssv": self.mssv,
            "ho_ten": self.ho_ten,
            "ngay_sinh": self.ngay_sinh,
            "gioi_tinh": self.gioi_tinh,
            "email": self.email,
            "so_dien_thoai": self.so_dien_thoai,
            "ma_lop": self.ma_lop,
            "dia_chi": self.dia_chi,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SinhVien":
        return cls(
            mssv=data.get("mssv", ""),
            ho_ten=data.get("ho_ten", ""),
            ngay_sinh=data.get("ngay_sinh", ""),
            gioi_tinh=data.get("gioi_tinh", "Nam"),
            email=data.get("email", ""),
            so_dien_thoai=data.get("so_dien_thoai", ""),
            ma_lop=data.get("ma_lop", ""),
            dia_chi=data.get("dia_chi", ""),
        )

    def tuoi(self) -> int:
        try:
            ngay = datetime.strptime(self.ngay_sinh, "%d/%m/%Y")
            return datetime.now().year - ngay.year
        except ValueError:
            return 0

    def __str__(self) -> str:
        return f"[{self.mssv}] {self.ho_ten} - Lớp: {self.ma_lop}"

    def __repr__(self) -> str:
        return f"SinhVien(mssv={self.mssv!r}, ho_ten={self.ho_ten!r})"
