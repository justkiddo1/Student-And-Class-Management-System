from models.base_model import BaseModel

# Khung giờ theo loại hình
TIET_GIO_LY_THUYET = {
    "Tiết 1-3": "7h00 - 9h20",
    "Tiết 4-6": "9h45 - 11h50",
    "Tiết 7-9": "12h30 - 14h45",
    "Tiết 10-12": "15h00 - 17h20",
    "Tiết 13-15": "18h20 - 20h20",
}

TIET_GIO_THUC_HANH = {
    "Tiết 1-5": "7h00 - 10h50",
    "Tiết 2-6": "8h00 - 11h50",
    "Tiết 7-11": "12h30 - 16h20",
    "Tiết 8-12": "13h15 - 17h20",
}

TIET_GIO_ONLINE = TIET_GIO_LY_THUYET

TIET_GIO_THEO_LOAI = {
    "Lý thuyết": TIET_GIO_LY_THUYET,
    "Thực hành": TIET_GIO_THUC_HANH,
    "Online": TIET_GIO_ONLINE,
}

THU_LIST = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
THU_ORDER = {t: i for i, t in enumerate(THU_LIST)}

TRANG_THAI_LIST = ["Sắp khai giảng", "Đang học", "Đã kết thúc"]
TRANG_THAI_COLOR = {
    "Sắp khai giảng": "#F57F17",
    "Đang học": "#2E7D32",
    "Đã kết thúc": "#6B7280",
}


def lay_tiet_list(loai_hinh: str) -> list[str]:
    return list(TIET_GIO_THEO_LOAI.get(loai_hinh, TIET_GIO_LY_THUYET).keys())


def lay_gio(loai_hinh: str, tiet: str) -> str:
    return TIET_GIO_THEO_LOAI.get(loai_hinh, TIET_GIO_LY_THUYET).get(tiet, "")


# BuoiHoc
class BuoiHoc:

    def __init__(self, thu: str, tiet: str, gio: str = "", phong: str = ""):
        self.thu = thu
        self.tiet = tiet
        self.gio = gio
        self.phong = phong.strip()

    def to_dict(self) -> dict:
        return {
            "thu": self.thu,
            "tiet": self.tiet,
            "gio": self.gio,
            "phong": self.phong,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BuoiHoc":
        return cls(
            thu=data.get("thu", ""),
            tiet=data.get("tiet", ""),
            gio=data.get("gio", ""),
            phong=data.get("phong", ""),
        )

    def validate(self, loai_hinh: str = "") -> tuple[bool, str]:
        if self.thu not in THU_LIST:
            return False, f"Thứ không hợp lệ: {self.thu}"
        valid_tiet = lay_tiet_list(loai_hinh) if loai_hinh else (
                list(TIET_GIO_LY_THUYET) + list(TIET_GIO_THUC_HANH)
        )
        if self.tiet not in valid_tiet:
            return False, f"Tiết '{self.tiet}' không hợp lệ với loại hình '{loai_hinh}'."
        return True, ""

    def __str__(self) -> str:
        phong_str = f" - Phòng {self.phong}" if self.phong else ""
        return f"{self.thu} | {self.tiet} ({self.gio}){phong_str}"


# LopHoc
class LopHoc(BaseModel):
    LOAI_HINH_LIST = ["Lý thuyết", "Thực hành", "Online"]

    def __init__(self, ma_lop: str, ten_mon: str, ma_mon: str, giang_vien: str,
                 si_so_toi_da: int = 50, loai_hinh: str = "Lý thuyết",
                 hoc_ky: str = "1", nam_hoc: str = "2024-2025",
                 so_tin_chi: int = 3,
                 ngay_bat_dau: str = "", ngay_ket_thuc: str = "",
                 trang_thai: str = "Đang học"):
        self.ma_lop = ma_lop.strip().upper()
        self.ten_mon = ten_mon.strip()
        self.ma_mon = ma_mon.strip().upper()
        self.giang_vien = giang_vien.strip()
        self.si_so_toi_da = int(si_so_toi_da)
        self.loai_hinh = loai_hinh.strip()
        self.hoc_ky = str(hoc_ky).strip()
        self.nam_hoc = nam_hoc.strip()
        self.so_tin_chi = int(so_tin_chi) if so_tin_chi else 3
        self.ngay_bat_dau = ngay_bat_dau.strip()
        self.ngay_ket_thuc = ngay_ket_thuc.strip()
        self.trang_thai = trang_thai.strip() if trang_thai in TRANG_THAI_LIST else "Đang học"
        self.danh_sach_mssv: list[str] = []
        self.lich_hoc: list[BuoiHoc] = []

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
        if self.loai_hinh not in self.LOAI_HINH_LIST:
            return False, "Loại hình không hợp lệ."
        if not self.lich_hoc:
            return False, "Lớp học phải có ít nhất một buổi học."
        seen = set()
        for buoi in self.lich_hoc:
            ok, msg = buoi.validate(self.loai_hinh)
            if not ok:
                return False, msg
            key = (buoi.thu, buoi.tiet)
            if key in seen:
                return False, f"Trùng lịch: {buoi.thu} {buoi.tiet}."
            seen.add(key)
        return True, ""

    # Lịch học
    def them_buoi(self, buoi: BuoiHoc) -> tuple[bool, str]:
        ok, msg = buoi.validate(self.loai_hinh)
        if not ok:
            return False, msg
        for b in self.lich_hoc:
            if b.thu == buoi.thu and b.tiet == buoi.tiet:
                return False, f"Đã có buổi {buoi.thu} {buoi.tiet}."
        self.lich_hoc.append(buoi)
        self._sap_xep_lich()
        return True, "Thêm buổi thành công."

    def xoa_buoi(self, thu: str, tiet: str) -> tuple[bool, str]:
        truoc = len(self.lich_hoc)
        self.lich_hoc = [b for b in self.lich_hoc
                         if not (b.thu == thu and b.tiet == tiet)]
        if len(self.lich_hoc) == truoc:
            return False, "Không tìm thấy buổi học."
        return True, "Xóa buổi thành công."

    def _sap_xep_lich(self):
        tiet_order = {t: i for i, t in enumerate(lay_tiet_list(self.loai_hinh))}
        self.lich_hoc.sort(key=lambda b: (
            THU_ORDER.get(b.thu, 99),
            tiet_order.get(b.tiet, 99),
        ))

    @property
    def lich_hoc_str(self) -> str:
        if not self.lich_hoc:
            return "Chưa có lịch"
        nhom: dict[str, list[str]] = {}
        for b in self.lich_hoc:
            ten_thu = b.thu.replace("Thứ ", "T").replace("Chủ nhật", "CN")
            nhom.setdefault(b.tiet, []).append(ten_thu)
        return " | ".join("+".join(thus) + " " + tiet
                          for tiet, thus in nhom.items())

    @property
    def lich_hoc_day_du(self) -> str:
        if not self.lich_hoc:
            return "Chưa có lịch"
        lines = []
        for b in self.lich_hoc:
            phong = f" - Phòng {b.phong}" if b.phong else ""
            lines.append(f"{b.thu}: {b.tiet} ({b.gio}){phong}")
        return "\n".join(lines)

    # Sinh viên
    def them_sinh_vien(self, mssv: str) -> tuple[bool, str]:
        if mssv in self.danh_sach_mssv:
            return False, f"Sinh viên {mssv} đã có trong lớp."
        if len(self.danh_sach_mssv) >= self.si_so_toi_da:
            return False, "Lớp đã đầy."
        self.danh_sach_mssv.append(mssv)
        return True, "Thêm thành công."

    def xoa_sinh_vien(self, mssv: str) -> tuple[bool, str]:
        if mssv not in self.danh_sach_mssv:
            return False, f"Sinh viên {mssv} không có trong lớp."
        self.danh_sach_mssv.remove(mssv)
        return True, "Xóa thành công."

    @property
    def si_so_hien_tai(self) -> int:
        return len(self.danh_sach_mssv)

    @property
    def ty_le_si_so(self) -> float:
        if self.si_so_toi_da == 0:
            return 0.0
        return round(self.si_so_hien_tai / self.si_so_toi_da * 100, 1)

    @property
    def con_cho(self) -> int:
        return max(0, self.si_so_toi_da - self.si_so_hien_tai)

    # Serialization
    def to_dict(self) -> dict:
        return {
            "ma_lop": self.ma_lop,
            "ten_mon": self.ten_mon,
            "ma_mon": self.ma_mon,
            "giang_vien": self.giang_vien,
            "si_so_toi_da": self.si_so_toi_da,
            "loai_hinh": self.loai_hinh,
            "hoc_ky": self.hoc_ky,
            "nam_hoc": self.nam_hoc,
            "so_tin_chi": self.so_tin_chi,
            "ngay_bat_dau": self.ngay_bat_dau,
            "ngay_ket_thuc": self.ngay_ket_thuc,
            "trang_thai": self.trang_thai,
            "lich_hoc": [b.to_dict() for b in self.lich_hoc],
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
            loai_hinh=data.get("loai_hinh", "Lý thuyết"),
            hoc_ky=data.get("hoc_ky", "1"),
            nam_hoc=data.get("nam_hoc", "2024-2025"),
            so_tin_chi=data.get("so_tin_chi", 3),
            ngay_bat_dau=data.get("ngay_bat_dau", ""),
            ngay_ket_thuc=data.get("ngay_ket_thuc", ""),
            trang_thai=data.get("trang_thai", "Đang học"),
        )
        obj.danh_sach_mssv = data.get("danh_sach_mssv", [])

        lich_raw = data.get("lich_hoc", [])
        if isinstance(lich_raw, str):
            if lich_raw:
                tiet_default = lay_tiet_list(obj.loai_hinh)[0]
                obj.lich_hoc = [BuoiHoc(thu="Thứ 2", tiet=tiet_default,
                                        gio=lay_gio(obj.loai_hinh, tiet_default), phong="")]
        elif isinstance(lich_raw, list):
            obj.lich_hoc = [BuoiHoc.from_dict(b) for b in lich_raw]

        obj._sap_xep_lich()
        return obj

    def __str__(self) -> str:
        return (f"[{self.ma_lop}] {self.ten_mon} | GV: {self.giang_vien} "
                f"| {self.si_so_hien_tai}/{self.si_so_toi_da} "
                f"| {self.loai_hinh} | {self.lich_hoc_str} | {self.trang_thai}")

    def __repr__(self) -> str:
        return f"LopHoc(ma_lop={self.ma_lop!r}, ten_mon={self.ten_mon!r})"