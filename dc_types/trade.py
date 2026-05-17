from typing import Self, Optional
from pathlib import Path
from utils.split import split_items_full, SplitBuilder
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from dc_types.item import Item
from lib.utils import list_to_yaml


class Trade(Item):
    _type: str = "_trade"

    def __init__(self):
        self._type = "trade"
        self.name: str = ""
        self.page: int = -1
        self.attributes: list[str] = []
        self.tool: Optional[str] = None
        self.type: str = "<none>"
        self.categories: list[str] = []
        self.description: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        trade = cls()
        trade.name = d["name"]
        trade.page = int(d["page"])
        trade.attributes = d["attributes"]
        trade.tool = d["tool"]
        trade.type = d["type"]
        trade.categories = d["categories"]
        trade.description = d["description"]
        return trade

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"trades_{version}.json"

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / f"attributes/trades/{self.name}.md"

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(15 - 1, 18)

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams = SplitBuilder(
            is_header=["f3"],
            is_section=["f4"],
            discard_from_frag=["f4"],
        ).build()
        items = split_items_full(frags, prams, "trades")
        while items[0].name.startswith("Trade"):
            items.pop(0)
        return items

    def markdown(self) -> str:
        args: dict = {
            "name": self.name,
            "page": self.page,
            "attributes": list_to_yaml(self.attributes, "attributes/attributes"),
            "tool": self.tool,
            "type": self.type,
            "categories": self.categories,
            "description": self.description,
        }

        return template.format(**args)


template: str = """---
name: {name}
page: {page}
attributes:
{attributes}
tool: {tool}
type: {type}
---
{description}
"""
