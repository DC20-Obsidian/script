from pathlib import Path
from typing import Self

from utils.split import SplitBuilder, split_items_full

from .frag_list import FragList
from .item import Item
from .proto_item import DCProtoItem


class Skill(Item):
    _type: str = "skill"

    def __init__(self):
        self._type = "skill"
        self.name: str = ""
        self.page: int = -1
        self.attribute: str = ""
        self.description: str = ""
        self.uses: list[str] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        skill = cls()
        skill.name = d["name"]
        skill.page = int(d["page"])
        skill.attribute = d["attribute"]
        skill.description = d["description"]
        skill.uses = d["uses"]
        return skill

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / f"Attributes/Skills/{self.name}.md"

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"skills_{version}.json"

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(13 - 1, 14)

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams = SplitBuilder(
            is_header=["f3"],
            is_section=["f4"],
            discard_from_frag=["f4"],
        ).build()
        return split_items_full(frags, prams, "skills")

    def markdown(self) -> str:
        args: dict = {
            "name": self.name,
            "page": self.page,
            "attribute": self.attribute,
            "description": self.description,
            "uses": self.uses,
        }
        return template.format(**args)


template: str = """---
name: {name}
page: {page}
attribute: "[[Attributes/Attributes/{attribute}|{attribute}]]"
---
{description}
"""
