import csv
import io
from handlers.file_handler import FileHandler


class CSVHandler(FileHandler):
    def __init__(self, duong_dan: str):
        if not duong_dan.endswith(".csv"):
            duong_dan += ".csv"
        super().__init__(duong_dan)

    def doc(self) -> list[dict]:
        if not self.ton_tai():
            return []
        try:
            with open(self.duong_dan, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                du_lieu = []
                for row in reader:
                    ban_ghi = {}
                    for k, v in row.items():
                        if v in ("None", ""):
                            ban_ghi[k] = None
                        else:
                            # Thử parse số thực
                            try:
                                ban_ghi[k] = float(v) if "." in v else int(v)
                            except (ValueError, TypeError):
                                ban_ghi[k] = v
                    du_lieu.append(ban_ghi)
                return du_lieu
        except OSError as e:
            raise IOError(f"Không thể đọc file: {self.duong_dan}\n{e}")

    def ghi(self, du_lieu: list[dict]) -> None:
        if not du_lieu:
            # Ghi file rỗng (chỉ có header nếu có)
            open(self.duong_dan, "w").close()
            return
        try:
            fieldnames = list(du_lieu[0].keys())
            with open(self.duong_dan, "w", encoding="utf-8-sig",
                      newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(du_lieu)
        except OSError as e:
            raise IOError(f"Không thể ghi file: {self.duong_dan}\n{e}")

    def doc_thanh_chuoi(self, du_lieu: list[dict]) -> str:
        if not du_lieu:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(du_lieu[0].keys()))
        writer.writeheader()
        writer.writerows(du_lieu)
        return output.getvalue()
