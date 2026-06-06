import re
from datetime import datetime, date
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

        if not re.fullmatch(r"SV\d+",self.mssv):
            return False, ("Mã số sinh viên không hợp lệ.\n" "Định dạng bắt đầu bằng 'SV' và theo sau là chữ số (VD: SV001, SV002).")

        if not self.ho_ten:
            return False, "Họ tên không được để trống."
        if re.search(r"[0-9]", self.ho_ten):
            return False, "Họ và tên không được chứa chữ số."
        if re.search(r"[^\w\s\-]", self.ho_ten, flags=re.UNICODE):
            return False, "Họ và tên không được chứa ký tự đặc biệt."
        if re.search(r"[_]", self.ho_ten):
            return False, "Họ và tên không được chứa ký tự đặc biệt."
        if len(self.ho_ten.strip()) < 2:
            return False, "Họ và tên phải có ít nhất 2 ký tự."

        if not self.ngay_sinh:
            return False, "Ngày sinh không được để trống."
        if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", self.ngay_sinh):
            return False, "Ngày sinh phải có định dạng DD/MM/YYYY (VD: 15/08/2003)."

        try:
            ngay_sinh_dt = datetime.strptime(self.ngay_sinh, "%d/%m/%Y").date()
        except ValueError:
            return False, "Ngày sinh không hợp lệ (ngày/tháng không tồn tại)."

        hom_nay = date.today()
        if ngay_sinh_dt > hom_nay:
            return False, "Ngày sinh không được lớn hơn ngày hiện tại."

        tuoi = (hom_nay.year - ngay_sinh_dt.year
                - ((hom_nay.month, hom_nay.day) < (ngay_sinh_dt.month, ngay_sinh_dt.day)))
        if tuoi < 18:
            return False, (
                f"Sinh viên phải đủ 18 tuổi trở lên.\n"
                f"Ngày sinh {self.ngay_sinh} cho tuổi hiện tại là {tuoi}."
            )

        if not self.email:
            return False, "Email không được để trống."
        if not re.fullmatch(
                r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
                self.email
        ):
            return False, (
                "Email không hợp lệ.\n"
                "Định dạng đúng: tenmail@domain.com (VD: sinhvien@gmail.com)."
            )

        if not self.so_dien_thoai:
            return False, "Số điện thoại không được để trống."
        if not re.fullmatch(r"0\d{9}", self.so_dien_thoai):
            return False, (
                "Số điện thoại không hợp lệ.\n"
                "Yêu cầu: đúng 10 chữ số, bắt đầu bằng 0 (VD: 0901234567)."
            )

        if not self.ma_lop:
            return False, "Vui lòng chọn lớp học."
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
            ngay = datetime.strptime(self.ngay_sinh, "%d/%m/%Y").date()
            hom_nay = date.today()
            return (hom_nay.year - ngay.year
                    - ((hom_nay.month, hom_nay.day) < (ngay.month, ngay.day)))
        except ValueError:
            return 0

    def __str__(self) -> str:
        return f"[{self.mssv}] {self.ho_ten} - Lớp: {self.ma_lop}"

    def __repr__(self) -> str:
        return f"SinhVien(mssv={self.mssv!r}, ho_ten={self.ho_ten!r})"
