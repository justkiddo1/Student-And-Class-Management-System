from handlers.file_handler import FileHandler


class TXTHandler(FileHandler):
    PHAN_CACH = "---"

    def __init__(self, duong_dan: str):
        if not duong_dan.endswith(".txt"):
            duong_dan += ".txt"
        super().__init__(duong_dan)

    def doc(self) -> list[dict]:
        if not self.ton_tai():
            return []
        try:
            with open(self.duong_dan, "r", encoding="utf-8") as f:
                noi_dung = f.read()

            du_lieu = []
            for block in noi_dung.split(self.PHAN_CACH):
                block = block.strip()
                if not block:
                    continue
                ban_ghi = {}
                for dong in block.splitlines():
                    dong = dong.strip()
                    if "=" not in dong:
                        continue
                    khoa, _, gia_tri = dong.partition("=")
                    khoa = khoa.strip()
                    gia_tri = gia_tri.strip()
                    # Parse kiểu dữ liệu
                    if gia_tri == "None":
                        ban_ghi[khoa] = None
                    elif gia_tri == "True":
                        ban_ghi[khoa] = True
                    elif gia_tri == "False":
                        ban_ghi[khoa] = False
                    else:
                        try:
                            ban_ghi[khoa] = float(gia_tri) if "." in gia_tri else int(gia_tri)
                        except ValueError:
                            if gia_tri.startswith("[") and gia_tri.endswith("]"):
                                noi = gia_tri[1:-1].strip()
                                ban_ghi[khoa] = [x.strip() for x in noi.split(",")] if noi else []
                            else:
                                ban_ghi[khoa] = gia_tri
                if ban_ghi:
                    du_lieu.append(ban_ghi)
            return du_lieu

        except OSError as e:
            raise IOError(f"Không thể đọc file: {self.duong_dan}\n{e}")

    def ghi(self, du_lieu: list[dict]) -> None:
        try:
            with open(self.duong_dan, "w", encoding="utf-8") as f:
                for ban_ghi in du_lieu:
                    for khoa, gia_tri in ban_ghi.items():
                        if isinstance(gia_tri, list):
                            gia_tri_str = "[" + ", ".join(str(x) for x in gia_tri) + "]"
                        else:
                            gia_tri_str = str(gia_tri) if gia_tri is not None else "None"
                        f.write(f"{khoa}={gia_tri_str}\n")
                    f.write(f"{self.PHAN_CACH}\n")
        except OSError as e:
            raise IOError(f"Không thể ghi file: {self.duong_dan}\n{e}")