import hashlib
import re
from models.base_model import BaseModel


class NguoiDung(BaseModel):
    VAI_TRO_ADMIN = "admin"
    VAI_TRO_USER = "user"

    def __init__(self, ten_dang_nhap: str, mat_khau_hash: str, ho_ten: str, email: str, vai_tro: str = VAI_TRO_USER,
                 kich_hoat: bool = True):
        self.ten_dang_nhap = ten_dang_nhap.strip().lower()
        self.mat_khau_hash = mat_khau_hash
        self.ho_ten = ho_ten.strip()
        self.email = email.strip().lower()
        self.vai_tro = vai_tro
        self.kich_hoat = kich_hoat

    @staticmethod
    def hash_mat_khau(mat_khau: str) -> str:
        return hashlib.sha256(mat_khau.encode()).hexdigest()

    @classmethod
    def tao_tai_khoan(cls, ten_dang_nhap: str, mat_khau: str, ho_ten: str, email: str,
                      vai_tro: str = VAI_TRO_USER) -> "NguoiDung":
        return cls(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau_hash=cls.hash_mat_khau(mat_khau),
            ho_ten=ho_ten,
            email=email,
            vai_tro=vai_tro,
        )

    def kiem_tra_mat_khau(self, mat_khau: str) -> bool:
        return self.mat_khau_hash == self.hash_mat_khau(mat_khau)

    def doi_mat_khau(self, mat_khau_cu: str, mat_khau_moi: str) -> tuple[bool, str]:
        if not self.kiem_tra_mat_khau(mat_khau_cu):
            return False, "Mật khẩu cũ không đúng."
        if len(mat_khau_moi) < 6:
            return False, "Mật khẩu mới phải có ít nhất 6 ký tự."
        self.mat_khau_hash = self.hash_mat_khau(mat_khau_moi)
        return True, "Đổi mật khẩu thành công."

    @property
    def la_admin(self) -> bool:
        return self.vai_tro == self.VAI_TRO_ADMIN

    def co_quyen(self, hanh_dong: str) -> bool:
        quyen_user = {"Xem_sinh_vien", "xem_lop", "xem_diem", "nhap_diem"}
        if self.vai_tro == self.VAI_TRO_ADMIN:
            return True
        return hanh_dong in quyen_user

    # Validation
    def validate(self) -> tuple[bool, str]:
        if not self.ten_dang_nhap:
            return False, "Tên đăng nhập không được để trống."
        if not re.fullmatch(r"[a-z0-9_]{3,30}", self.ten_dang_nhap):
            return False, "Tên đăng nhập chỉ gồm chữ thường, số, dấu _ (3-30 ký tự)."
        if not self.ho_ten:
            return False, "Họ tên không được để trống."
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", self.email):
            return False, "Email không hợp lệ."
        if self.vai_tro not in (self.VAI_TRO_ADMIN, self.VAI_TRO_USER):
            return False, "Vai trò không hợp lệ."
        return True, ""

    def to_dict(self) -> dict:
        return {
            "ten_dang_nhap": self.ten_dang_nhap,
            "mat_khau_hash": self.mat_khau_hash,
            "ho_ten": self.ho_ten,
            "email": self.email,
            "vai_tro": self.vai_tro,
            "kich_hoat": self.kich_hoat,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NguoiDung":
        return cls(
            ten_dang_nhap=data.get("ten_dang_nhap", ""),
            mat_khau_hash=data.get("mat_khau_hash", ""),
            ho_ten=data.get("ho_ten", ""),
            email=data.get("email", ""),
            vai_tro=data.get("vai_tro", cls.VAI_TRO_USER),
            kich_hoat=data.get("kich_hoat", True),
        )

    def __str__(self) -> str:
        trang_thai = "✓" if self.kich_hoat else "✗"
        return f"[{trang_thai}] {self.ten_dang_nhap} ({self.vai_tro}) - {self.ho_ten}"

    def __repr__(self) -> str:
        return f"NguoiDung(ten_dang_nhap={self.ten_dang_nhap!r}, vai_tro={self.vai_tro!r})"