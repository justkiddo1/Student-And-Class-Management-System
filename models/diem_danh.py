from models.base_model import BaseModel
from datetime import date

TRANG_THAI_LIST = ["Có mặt", "Vắng", "Vắng có phép", "Trễ"]
TRANG_THAI_ICON = {
    "Có mặt": "✓",
    "Vắng": "✗",
    "Vắng có phép": "P",
    "Trễ": "~",
}
TRANG_THAI_COLOR = {
    "Có mặt": "#2E7D32",
    "Vắng": "#C62828",
    "Vắng có phép": "#F57F17",
    "Trễ": "#0277BD",
}


class DiemDanh(BaseModel):

    def __init__(self, ma_lop: str, ngay: str, thu: str, tiet: str,
                 ds_trang_thai: dict = None, ghi_chu: str = ""):
        self.ma_lop = ma_lop.strip().upper()
        self.ngay = ngay
        self.thu = thu
        self.tiet = tiet
        self.ds_trang_thai = ds_trang_thai or {}
        self.ghi_chu = ghi_chu

    # Helpers
    def set_trang_thai(self, mssv: str, trang_thai: str):
        if trang_thai not in TRANG_THAI_LIST:
            raise ValueError(f"Trạng thái không hợp lệ: {trang_thai}")
        self.ds_trang_thai[mssv] = trang_thai

    def lay_trang_thai(self, mssv: str) -> str:
        return self.ds_trang_thai.get(mssv, "Có mặt")

    def thong_ke(self) -> dict:
        from collections import Counter
        c = Counter(self.ds_trang_thai.values())
        return {tt: c.get(tt, 0) for tt in TRANG_THAI_LIST}

    @property
    def khoa_chinh(self) -> str:
        return f"{self.ma_lop}|{self.ngay}|{self.tiet}"

    # Serialization
    def to_dict(self) -> dict:
        return {
            "ma_lop": self.ma_lop,
            "ngay": self.ngay,
            "thu": self.thu,
            "tiet": self.tiet,
            "ds_trang_thai": self.ds_trang_thai,
            "ghi_chu": self.ghi_chu,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiemDanh":
        return cls(
            ma_lop=data.get("ma_lop", ""),
            ngay=data.get("ngay", ""),
            thu=data.get("thu", ""),
            tiet=data.get("tiet", ""),
            ds_trang_thai=data.get("ds_trang_thai", {}),
            ghi_chu=data.get("ghi_chu", ""),
        )

    def validate(self) -> tuple[bool, str]:
        if not self.ma_lop:
            return False, "Mã lớp không được trống."
        if not self.ngay:
            return False, "Ngày không được trống."
        return True, ""

    def __str__(self) -> str:
        tk = self.thong_ke()
        return (f"[{self.ma_lop}] {self.thu} {self.ngay} {self.tiet} "
                f"| Có mặt: {tk['Có mặt']} Vắng: {tk['Vắng']}")

    def __repr__(self) -> str:
        return f"DiemDanh(ma_lop={self.ma_lop!r}, ngay={self.ngay!r})"
