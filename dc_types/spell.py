import re
from pathlib import Path
from typing import Self

from utils.frontmatter import fmt_bool, list_to_yaml

from .enhancement import Enhancement
from .item import Item


class Spell(Item):
    _type: str = "spell"

    def __init__(self):
        self._type = "spell"
        self.name: str = ""
        self.page: int = -1
        self.source: list[str] = []
        self.school: str = ""
        self.tags: list[str] = []
        self.cost: str = ""
        self.ap_cost: int = -1
        self.mp_cost: int = -1
        self.sustained: bool = False
        self.range: str = ""
        self.duration: str = ""
        self.description: str = ""
        self.enhancements: list[Enhancement] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        s = cls()
        s.name = d["name"]
        s.page = int(d["page"])
        s.source = d["source"]
        s.school = d["source"]
        s.tags = d["tags"]
        s.cost = d["cost"]
        s.ap_cost = int(d["ap_cost"])
        s.mp_cost = int(d["mp_cost"])
        s.sustained = d["sustained"]
        s.range = d["range"]
        s.duration = d["duration"]
        s.description = d["description"]
        s.enhancements = d["enhancements"]
        return s

    def fixup(self) -> Self:
        ap = re.search(r"([0-9]+) ?AP", self.cost)
        self.ap_cost = int(ap.group(1) if ap else 0)

        mp = re.search(r"([0-9]+) ?MP|minimum of ([0-9]+)", self.cost)
        mp = mp.groups() if mp else (0, 0)
        self.mp_cost = int(mp[0] or mp[1])

        if "Sustained" in self.duration:
            self.sustained = True
            self.duration = re.sub(r" ?\(?Sustained\)?", "", self.duration)
        return self

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "source": list_to_yaml(self.source, "Spells/Sources"),
            "school": self.school.title(),
            "tags": list_to_yaml(self.tags, "Spells/Tags"),
            "cost": self.cost,
            "range": self.range,
            "duration": self.duration,
            "AP": self.ap_cost,
            "MP": self.mp_cost,
            "sustained": fmt_bool(self.sustained),
            "page": self.page,
            "description": self.description,
            "enhancements": enhancements(self.enhancements),
        }
        return template.format(**args)

    @classmethod
    def get_default_page_range(cls) -> slice[int, int]:
        return slice(71 - 1, 145)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"spells_{version}.json"

    def markdown_path(self, prefix: Path = Path("")) -> Path:
        return prefix / "Spells/Spells" / f"{self.name}.md"


template = """---
name: {name}
source:
{source}
school: "[[Spells/Schools/{school}|{school}]]"
spell_tags:
{tags}
ap: {AP}
mp: {MP}
cost: {cost}
range: {range}
duration: {duration}
sustained: {sustained}
page: {page}
---
{description}

## Spell Enhancements
{enhancements}
"""


def enhancements(enhancements: list[Enhancement]) -> str:
    s: str = ""
    for enh in enhancements:
        s += enh.markdown()
    return s
