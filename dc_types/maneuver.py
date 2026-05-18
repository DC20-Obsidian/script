import re
from typing import Self
from pathlib import Path
from dc_types.item import Item
from .enhancement import Enhancement


class Maneuver(Item):
    _type: str = "maneuver"
    def __init__(self):
        self._type: str = "maneuver"
        self.page: int = -1
        self.name: str = ""
        self.summary: str = ""
        self.kind: str = ""
        self.cost: str = ""
        self.ap_cost: int = -1
        self.sp_cost: int = -1
        self.range: str = ""
        self.description: str = ""
        self.enhancements: list[Enhancement] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        m = cls()
        m.page = int(d["page"])
        m.name = d["name"]
        m.summary = d["summary"]
        m.kind = d["kind"]
        m.cost = d["cost"]
        m.ap_cost = int(d["ap_cost"])
        m.sp_cost = int(d["sp_cost"])
        m.range = d["range"]
        m.description = d["describution"]
        m.enhancements = d["enhancements"]
        return m

    def fixup(self) -> Self:
        ap = re.search(r"([0-9]+) ?AP", self.cost)
        self.ap_cost = int(ap.group(1) if ap else 0)

        sp = re.search(r"([0-9]+) ?SP", self.cost)
        self.sp_cost = int(sp.group(1) if sp else 0)

        return self

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "summary": self.summary,
            "AP": self.ap_cost,
            "SP": self.sp_cost,
            "enhancements": enhancements(self.enhancements),
            "cost": self.cost,
            "range": self.range,
            "kind": self.kind.title(),
            "page": self.page,
            "desc": self.description,
        }

        return template.format(**args)

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(52 - 1, 59)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"maneuvers_{version}.json"

    def markdown_path(self, prefix: Path) -> Path:
        return prefix / "Maneuvers/Maneuvers" / f"{self.name}.md"


template = """---
name: {name}
cost: {cost}
ap: {AP}
sp: {SP}
range: {range}
page: {page}
kind: "[[Maneuvers/Types/{kind}|{kind}]]"
---
{summary}
{cost}
{desc}

## Maneuver Enhancements
{enhancements}
"""


def enhancements(enhancements: list[Enhancement]) -> str:
    s: str = ""
    for enh in enhancements:
        s += enh.markdown()
    return s
