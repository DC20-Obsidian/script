import json
import re
from fixup_text import fixup_name

class Spell:
    def __init__(self):
        self.name: str = ""
        self.page_number: int = -1
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

    def fixup(self) -> Spell:
        ap = re.search(r'([0-9]+) ?AP', self.cost)
        ap = ap.group(1) if ap else 0
        self.ap_cost = int(ap)
        mp = re.search(r'([0-9]+) ?MP|minimum of ([0-9]+)', self.cost)
        mp = mp.groups() if mp else (0, 0)
        mp = mp[0] if mp[0] else mp[1]
        self.mp_cost = int(mp)
        if "Sustained" in self.duration:
            self.sustained = True
            self.duration = re.sub(r' ?\(?Sustained\)?', '', self.duration)
        return self

class Enhancement:
    def __init__(self):
        self.name: str = ""
        self.cost: str = ""
        self.description: str = ""
        # description
    def finish(self):
        (prefix, _, self.description) = self.description.partition(')')
        # self.description = fixup(self.description.strip())
        (self.name, _, self.cost) = prefix.partition('(')

class DCObjEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell, Enhancement, TextItem, DCProtoItem)):
            d = o.__dict__
            # if isinstance(o, Spell):
            #     d.pop("_current_enhmt")
            return d
        else:
            return json.JSONEncoder.default(self, o)

class TextItem:
    def __init__(self, item: dict, page: int):
        self.page: int = page
        self.text: str = item['text']
        self.font: str = item['fontName']
        self.font_size = item['fontSize']

class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.items: list[TextItem] = []
