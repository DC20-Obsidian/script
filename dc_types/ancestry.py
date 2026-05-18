import re
from functools import reduce
from pathlib import Path
from typing import Optional, Self

from utils.colors import colors
from utils.debug import eprint
from utils.split import SplitBuilder, SplitPrams, split_items_full

from .frag_list import FragList
from .item import Item
from .proto_item import DCProtoItem


class Ancestry(Item):
    _type: str = "ancestry"
    def __init__(self):
        self._type = "ancestry"
        self.name: str = ""
        self.page: int = -1
        self.description: str = ""
        self.traits: list[Trait] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        a: Ancestry = cls()
        a.name = d["name"]
        a.page = int(d["page"])
        a.traits = d["traits"]
        a.description = d["description"]
        return a

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(198 - 1, 206)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"ancestries_{version}.json"

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / "ancestries/ancestries" / f"{self.name}.md"

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams: SplitPrams = SplitBuilder(
            is_header=["f4"],
            cont_item=["beasttraits"],
        ).build()
        return split_items_full(frags, prams, "ancestry")

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "page": self.page,
            "traits": reduce(lambda s, t: s + t.markdown_embed(), self.traits, ""),
            "description": self.description,
        }
        return template.format(**args)

    def save_subitems(self, prefix: Path):
        import os
        for trait in self.traits:
            file_name: Path = trait.markdown_path(prefix)
            markdown: str = trait.markdown()
            os.makedirs(file_name.parent, exist_ok=True)
            with open(file_name, 'w') as file:
                file.write(markdown)

    def fixup(self) -> Self:
        return self


class Trait(Item):
    def __init__(self):
        self._type = "ancestry_trait"
        self.name: str = ""
        self.page: int = -1
        self.cost: int = -100
        self.dependent_on: Optional[str] = None
        self.description: str = ""
        self.default: bool = False
        self.kind: str = ""
        self.ancestry: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        t: Trait = cls()
        t.name = d["name"]
        t.page = int(d["page"])
        t.cost = int(d["cost"])
        t.dependent_on = d["dependent_on"]
        t.description = d["description"]
        t.default = d["default"]
        t.kind = d["kind"]
        t.ancestry = d["ancestry"]
        return t

    def fixup(self) -> Self:
        return self

    def fmt_args(self) -> dict[str, str]:
        args = {
            "name": self.name,
            "page": str(self.page),
            "cost": f"({str(self.cost)})",
            "cost_prop": str(self.cost),
            "requires": f"\n**Requires:** {self.dependent_on}" if self.dependent_on else "",
            "requires_prop": requires_prop(self),
            "description": self.description,
            "default": str(self.default).lower(),
            "kind": self.kind,
            "ancestry": self.ancestry,
        }
        return args

    def markdown(self) -> str:
        return trait_template.format(**self.fmt_args())

    def markdown_embed(self) -> str:
        return trait_embed_template.format(**self.fmt_args())

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        raise Exception("Not implimented")

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        (_, _) = (data_folder, version)
        raise Exception("Not implimented")

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / "ancestries/traits" / self.ancestry / f"{self.name}.md"

def requires_prop(trait: Trait) -> str:
    requres = trait.dependent_on
    if not requres:
        return "null"
    if requres[0].isupper():
        return f"\"[[ancestries/traits/{trait.ancestry}/{requres}|{requres}]]\""
    else:
        return requres

template: str = """---
name: {name}
page: {page}
---
{description}
## Traits
{traits}
"""

trait_embed_template = """#### {cost:<4} {name}{requires}
{description}
"""

trait_template: str = """---
name: {name}
page: {page}
cost: {cost_prop}
requires: {requires_prop}
default: {default}
kind: {kind}
ancestry: "[[ancestries/ancestries/{ancestry}|{ancestry}]]"
---
{description}
"""
