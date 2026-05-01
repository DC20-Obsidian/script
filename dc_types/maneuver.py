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
        m.description = d["describution"]
        m.enhancements = d["enhancements"]

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "summary": self.summary,
            "AP": self.ap_cost,
            "SP": self.sp_cost,
            "enhancemnets": enhancements(self.enhancements),
            "cost": self.cost,
            "kind": self.kind,
            "page": self.page,
            "desc": self.description,
        }

        return template.format(**args)


template = """---
name: {name}
stacking: {stacking}
ap: {AP}
sp: {SP}
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
