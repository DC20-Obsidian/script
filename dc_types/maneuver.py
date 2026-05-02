from typing import Self
import re
from .enhancement import Enhancement


class Maneuver:
    def __init__(self):
        self.type: str = "maneuver"
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

    @staticmethod
    def from_json(d: dict):
        m = Maneuver()
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
            "enhancemnets": enhancements(self.enhancements),
            "cost": self.cost,
            "range": self.range,
            "kind": self.kind,
            "page": self.page,
            "desc": self.description,
        }

        return template.format(**args)


template = """---
name: {name}
stacking: {stacking}
cost: {cost}
ap: {AP}
sp: {SP}
range: {range}
page: {page}
kind: {kind}
---
{summary}
{cost}
{desc}

## Maneuver Enhancements
{enhancements}
"""


def list_to_yaml(li: list[str]) -> str:
    a = " - "
    a += "\n - ".join(map(lambda s: f'"{s}"', li))
    return a


def enhancements(enhancements: list[Enhancement]) -> str:
    s: str = ""
    for enh in enhancements:
        s += enh.markdown()
    return s
