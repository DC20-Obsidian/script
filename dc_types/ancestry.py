import re
from functools import reduce
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from utils.split import split_items
from .item import Item
from typing import Self, Optional


class Ancestry(Item):
    def __init__(self):
        self._type = "ancestry"
        self.name: str = ""
        self.page: int = -1
        self.traits: list[Trait] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        a: Ancestry = cls()
        a.name = d["name"]
        a.page = int(d["page"])
        a.traits = d["traits"]
        return a

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(198 - 1, 206)

    @classmethod
    def get_save_file(cls, data_folder: str, version: str) -> str:
        return f"{data_folder}/ancestries_{version}.json"

    def markdown_path(self, prefix: str) -> str:
        return f"{prefix}/ancestries/ancestires/{self.name}.md"

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        return split_items(frags, ["f4"], ["f3"], 16.5, ["f2", "f9", "f1"], [], [])

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "page": self.page,
            "traits": reduce(lambda s, t: s + t.markdown(), self.traits, ""),
        }
        raise Exception("Not yet implimented")
        return template.format(**args)

    def fixup(self) -> Self:
        return self


class Trait(Item):
    def __init__(self):
        self._type = "ancestry_trait"
        self.name: str = ""
        self.page: int = -1
        self.cost: int = -1
        self.dependent_on: Optional[str] = None
        self.description: str = "1"
        self.default: bool = False
        self.kind: str = ""

        @classmethod
        def from_json(cls, d: dict) -> Self:
            t: Trait = cls()
            t.name = d["name"]
            t.page = d["page"]
            t.cost = int(d["cost"])
            t.dependent_on = d["dependent_on"]
            t.description = d["description"]
            t.default = d["default"]
            t.kind = d["kind"]
            return t

        def fixup(self) -> Self:
            return self

        def markdown(self) -> str:
            args = {
                "name": self.name,
                "page": self.page,
                "cost": self.cost,
                "dependent_on": self.dependent_on,
                "description": self.description,
                "default": self.default,
                "kind": self.kind,
            }
            return trait_template.format(**args)


template: str = """ TODO
"""

trait_template: str = """ TODO
"""
