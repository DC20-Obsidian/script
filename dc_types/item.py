from pathlib import Path
from abc import ABC, abstractmethod
from typing import Self
from dc_types.frag_list import FragList
from dc_types.proto_item import DCProtoItem
from utils.split import split_items_default


class Item(ABC):
    def __init__(self):
        self._type: str = "<none>"
        self.name: str = ""
        self.page: int = -1

    @classmethod
    @abstractmethod
    def get_default_page_range(cls) -> slice[int, int]:
        raise Exception("Abstract method")

    @classmethod
    @abstractmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        (_, _) = (data_folder, version)
        raise Exception("Abstract method")

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        return split_items_default(frags)

    @classmethod
    @abstractmethod
    def from_json(cls, d: dict) -> Self:
        _ = d
        raise Exception("Abstract method")

    @abstractmethod
    def markdown(self) -> str:
        raise Exception("Abstract method")

    @abstractmethod
    def markdown_path(self, prefix: Path) -> Path:
        _ = prefix
        raise Exception("Abstract method")
