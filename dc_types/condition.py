from typing import Self
from dc_types.item import Item


class Condition(Item):
    def __init__(self):
        self.type: str = "condition"
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
            "stacking": self.stacking,
        }

        return template.format(**args)

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(173 - 1, 174)

    @classmethod
    def get_save_file(cls, data_folder: str, version: str) -> str:
        return rf"{data_folder}/conditions_{version}.json"

    def markdown_path(self, prefix) -> str:
        return rf"{prefix}/conditions/{self.name}.md"


template = """---
name: {name}
stacking: {stacking}
---
{desc}
"""
