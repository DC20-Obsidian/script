import re
from .enhancement import Enhancement

class Spell:
    def __init__(self):
        self.type = 'spell'
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

    @staticmethod
    def from_json(d: dict) -> Spell:
        s = Spell()
        s.name = d['name']
        s.page = int(d['page'])
        s.source = d['source']
        s.school = d['source']
        s.tags = d['tags']
        s.cost = d['cost']
        s.ap_cost = int(d['ap_cost'])
        s.mp_cost = int(d['mp_cost'])
        s.sustained = d['sustained']
        s.range = d['range']
        s.duration = d['duration']
        s.description = d['description']
        s.enhancements = d['enhancements']
        return s

    def fixup(self) -> Spell:
        ap = re.search(r'([0-9]+) ?AP', self.cost)
        self.ap_cost = int(ap.group(1) if ap else 0)

        mp = re.search(r'([0-9]+) ?MP|minimum of ([0-9]+)', self.cost)
        mp = mp.groups() if mp else (0, 0)
        self.mp_cost = int(mp[0] or mp[1])

        if "Sustained" in self.duration:
            self.sustained = True
            self.duration = re.sub(r' ?\(?Sustained\)?', '', self.duration)
        return self
