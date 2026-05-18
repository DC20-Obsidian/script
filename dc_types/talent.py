from lib.utils import fmt_bool
from dc_types.text_frag import TextFrag
from typing import Self, Optional
from pathlib import Path
from dc_types.item import Item
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from utils.split import SplitBuilder, SplitPrams, split_items_full

class Talent(Item):
    _type: str = "talent"
    def __init__(self):
        self._type: str = "talent"
        self.name: str = ""
        self.page: int = -1
        self.level: int = 0
        self.requires: list[str] = []
        self.repeatable: bool = True
        self.class_name: Optional[str] = None
        self.description: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        t = cls()
        t.name = d["name"]
        t.page = int(d["page"])
        t.level = int(d["level"])
        t.requires = d["requires"]
        t.repeatable = d["repeatable"]
        t.class_name = d["class_name"]
        t.description = d["description"]
        return t

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(186 - 1, 191)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"talents_{version}.json"

    def markdown_path(self, prefix: Path) -> Path:
        class_name: str = f"{self.class_name}/" if self.class_name else ""
        return prefix / "talents" / f"{class_name}{self.name}.md"

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        def is_section(frag: TextFrag) -> bool:
            if frag.font == "f4":
                return True
            if frag.font == "f3":
                return frag.font_size >= 16
            return False
        split_prams: SplitPrams = SplitBuilder(
            is_header=(["f3"], 15),
            is_section=is_section,
            discard_from_frag=["f4", "f3"],
        ).build()
        return split_items_full(frags, split_prams, "talent")

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "page": self.page,
            "level": self.level or "null",
            "requires": self.requires,
            "repeatable": fmt_bool(self.repeatable),
            "class_name": self.class_name or "null",
            "description": self.description,
        }
        return template.format(**args)


template = """---
name: {name}
page: {page}
level: {level}
requires: {requires}
class: {class_name}
repeatable: {repeatable}
---
{description}
"""
