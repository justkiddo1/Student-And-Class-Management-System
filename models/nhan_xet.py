from models.base_model import BaseModel


class NhanXet(BaseModel):
    def __init__(self, ma_lop: str, ten_dang_nhap_gv: str,
                 noi_dung: str = "", cap_nhat_luc: str = ""):
        self.ma_lop = ma_lop.strip().upper()
        self.ten_dang_nhap_gv = ten_dang_nhap_gv.strip().lower()
        self.noi_dung = noi_dung.strip()
        self.cap_nhat_luc = cap_nhat_luc

    def to_dict(self) -> dict:
        return {
            "ma_lop": self.ma_lop,
            "ten_dang_nhap_gv": self.ten_dang_nhap_gv,
            "noi_dung": self.noi_dung,
            "cap_nhat_luc": self.cap_nhat_luc,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NhanXet":
        return cls(
            ma_lop=data.get("ma_lop", ""),
            ten_dang_nhap_gv=data.get("ten_dang_nhap_gv", ""),
            noi_dung=data.get("noi_dung", ""),
            cap_nhat_luc=data.get("cap_nhat_luc", ""),
        )

    def validate(self) -> tuple[bool, str]:
        if not self.ma_lop:
            return False, "Mã lớp không được trống."
        return True, ""

    def __str__(self) -> str:
        return f"[{self.ma_lop}] {self.ten_dang_nhap_gv}: {self.noi_dung[:50]}"

    def __repr__(self) -> str:
        return f"NhanXet(ma_lop={self.ma_lop!r})"
