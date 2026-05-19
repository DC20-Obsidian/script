import json
from pathlib import Path
from typing import Self, Optional

from dc_types.frag_list import FragList
from utils.frontmatter import list_to_yaml
from utils.split import SplitBuilder, split_items_full

from .item import Item
from .proto_item import DCProtoItem
from .text_frag import TextFrag


class WeaponProp(Item):
    _type: str = "weapon_prop"

    def __init__(self):
        self._type: str = "weapon_prop"
        self.page: int = -1
        self.name: str = ""
        self.cost: Optional[int] = None
        self.requires: list[str] = []
        self.description: str = ""
        self.kind: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        prop = cls()
        prop.page = int(d["page"])
        prop.name = d["name"]
        prop.cost = d["cost"]
        prop.requires = d["requires"]
        prop.description = d["description"]
        prop.kind = d["kind"]
        return prop

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"weapon_properties_{version}.json"

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(168 - 1, 168)

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams = SplitBuilder(
            is_header=_is_header,
            discard_from_frag=["f4", "f3"],
            is_section=["f3"],
        ).build()
        return split_items_full(frags, prams, "weapon_prop")

    @classmethod
    def extra_items(cls, prefix: Path) -> tuple[list[Item], Optional[Path]]:
        # with open(extra_file, "r") as file:
        #     return json.load(file, object_hook=dc_obj_decoder)

        ammo = cls()
        ammo.name = "Ammo"
        ammo.page = 165
        ammo.cost = 100
        ammo.description = "This Weapon requires ammunition to make Attacks. You can load a Weapon as part of an Attack made with it."
        ammo.kind = "Ranged"
        return ([], prefix / "weapon_properties.json")

    def markdown(self) -> str:
        args: dict = {
            "page": self.page,
            "name": self.name,
            "cost": self.cost or "null",
            "requires": list_to_yaml(self.requires),
            "description": self.description,
            "kind": self.kind,
        }
        return template.format(**args)

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / f"Equipment/Weapons/Properties/{self.kind}/{self.name}.md"


template: str = """---
name: {name}
page: {page}
cost: {cost}
requires:
{requires}
kind: {kind}
---
{description}
"""


def _is_header(name: str, frag: TextFrag):
    return (name.startswith("•") and frag.font in ["f11", "f14"]) or frag.text == "•"
