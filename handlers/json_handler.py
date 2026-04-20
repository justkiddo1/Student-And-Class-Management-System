import json
from handlers.file_handler import FileHandler


class JSONHandler(FileHandler):
    def __init__(self, duong_dan: str):
        if not duong_dan.endswith(".json"):
            duong_dan += ".json"
        super().__init__(duong_dan)

    def doc(self) -> list[dict]:
        if not self.ton_tai():
            return []
        try:
            with open(self.duong_dan, "r", encoding="utf-8") as f:
                noi_dung = f.read().strip()
                if not noi_dung:
                    return []
                du_lieu = json.loads(noi_dung)
                if isinstance(du_lieu, list):
                    return du_lieu
                if isinstance(du_lieu, dict) and "data" in du_lieu:
                    return du_lieu["data"]
                return []
        except json.JSONDecodeError as e:
            raise ValueError(f"File JSON bị lỗi định dạng: {self.duong_dan}\n{e}")
        except OSError as e:
            raise IOError(f"Không thể đọc file: {self.duong_dan}\n{e}")

    def ghi(self, du_lieu: list[dict]) -> None:
        try:
            with open(self.duong_dan, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=4)
        except OSError as e:
            raise IOError(f"Không thể ghi file: {self.duong_dan}\n{e}")