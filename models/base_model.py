from abc import ABC, abstractmethod


class BaseModel(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def validate(self) -> tuple[bool, str]:
        return True, ""
