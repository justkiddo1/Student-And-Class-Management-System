from abc import ABC, abstractmethod
from pathlib import Path

class FileHandler(ABC):
    def __init__(self, duong_dan:str):
        self.duong_dan = Path(duong_dan)
        self._dam_bao_thu_muc()

    def _dam_bao_thu_muc(self):
        self.duong_dan.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def doc(self) -> list[dict]:
        pass

    @abstractmethod
    def ghi(self,du_lieu: list[dict]) -> None:
        pass

    def them(self,ban_ghi:dict) -> None:
        du_lieu = self.doc()
        du_lieu.append(ban_ghi)
        self.ghi(du_lieu)

    def cap_nhat(self,khoa:str, gia_tri_khoa:str, ban_ghi_moi:dict) -> bool:
        du_lieu = self.doc()
        for i,item in enumerate(du_lieu):
            if str(item.get(khoa)) == str(gia_tri_khoa):
                du_lieu[i] = ban_ghi_moi
                self.ghi(du_lieu)
                return True
        return False

    def xoa(self,khoa:str, gia_tri_khoa:str) -> bool:
        du_lieu = self.doc()
        du_lieu_moi = [item for item in du_lieu if str(item.get(khoa)) != str(gia_tri_khoa)]
        if len(du_lieu_moi) == len(du_lieu):
            return False
        self.ghi(du_lieu_moi)
        return True

    def tim_mot(self,khoa:str,gia_tri:str) -> dict | None:
        for item in self.doc():
            if str(item.get(khoa)) == str(gia_tri):
                return item
        return None

    def tim_nhieu(self,khoa:str, gia_tri:str) -> list[dict]:
        return [item for item in self.doc() if str(item.get(khoa)) == str(gia_tri)]

    def ton_tai(self) -> bool:
        return self.duong_dan.exists()

    def xoa_file(self) -> None:
        if self.ton_tai():
            self.duong_dan.unlink()

    def chuyen_doi(self,handler_dich: "FileHandler") -> None:
        du_lieu = self.doc()
        handler_dich.ghi(du_lieu)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.duong_dan}')"