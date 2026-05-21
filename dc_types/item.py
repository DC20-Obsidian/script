from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self, Optional

from utils.split import split_items_default

from .frag_list import FragList
from .proto_item import DCProtoItem


class Item(ABC):
    _type: str = "<none>"

    def __init__(self):
        self._type: str = Item._type
        self.name: str = ""
        self.page: int = -1

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        raise Exception("Abstract method")

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        (_, _) = (data_folder, version)
        raise Exception("Abstract method")

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        return split_items_default(frags, cls._type)

    @classmethod
    @abstractmethod
    def from_json(cls, d: dict) -> Self:
        _ = d
        raise Exception("Abstract method")

    @abstractmethod
    def markdown(self) -> str:
        raise Exception("Abstract method")

    @abstractmethod
    def markdown_path(self, prefix: Path = Path("")) -> Path:
        _ = prefix
        raise Exception("Abstract method")

    def save_subitems(self, prefix: Path):
        _ = prefix
        return

    @classmethod
    def extra_items(cls, prefix: Path) -> tuple[list[Self], Optional[Path]]:
        return ([], None)

    def fixup(self) -> Self:
        return self

    def save_self(self, prefix: Path):
        import os

        file_name: Path = self.markdown_path(prefix)
        markdown: str = self.markdown()
        os.makedirs(file_name.parent, exist_ok=True)
        with open(file_name, "w") as file:
            file.write(markdown)
