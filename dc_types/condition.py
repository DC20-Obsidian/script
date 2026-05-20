from pathlib import Path
from typing import Self

from utils.frontmatter import fmt_bool

from .item import Item


class Condition(Item):
    _type: str = "condition"

    def __init__(self):
        self._type: str = "condition"
        self.page: int = -1
        self.name: str = ""
        self.description: str = ""
        self.stacking: bool = False

    @classmethod
    def from_json(cls, d: dict) -> Self:
        c = cls()
        c.page = int(d["page"])
        c.name = d["name"]
        c.description = d["describution"]
        c.stacking = d["stacking"]
        return c

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "desc": self.description,
            "stacking": fmt_bool(self.stacking),
        }

        return template.format(**args)

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(173 - 1, 174)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"conditions_{version}.json"

    def markdown_path(self, prefix: Path = Path("")) -> Path:
        return prefix / f"Conditions/Conditions/{self.name}.md"


template = """---
name: {name}
stacking: {stacking}
---
{desc}
"""
