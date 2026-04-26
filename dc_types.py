import json
from fixup_text import fixup

class Spell:
    def __init__(self):
        self.name: str = "<none>"
        self.source: list[str] = []
        self.school: str = "<none>"
        self.tags: list[str] = []
        self.cost: str = "<none>"
        self.range: str = "<none>"
        self.duration: str = "<none>"
        self.description: str = ""
        self.enhancements: dict[str, Enhancement] = {}

class Enhancement:
    def __init__(self):
        self.name: str = "<none>"
        self.cost: str = "<none>"
        self.description: str = ""
        # description
    def finish(self):
        (prefix, _, self.description) = self.description.partition(')')
        self.description = fixup(self.description.strip())
        (self.name, _, self.cost) = prefix.partition('(')

class EncodeJSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell, Enhancement)):
            d = o.__dict__
            # if isinstance(o, Spell):
            #     d.pop("_current_enhmt")
            return d
        else:
            return json.JSONEncoder.default(self, o)
