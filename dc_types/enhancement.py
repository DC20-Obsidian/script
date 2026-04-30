import re

class Enhancement:
    def __init__(self):
        from typing import Optional
        self.type = 'enhancement'
        self.name: str = ""
        self.cost: str = ""
        self.repeatable: bool = False
        self.sustained: bool = False
        self.dependent_on: Optional[str] = None
        # ap/mp_cost is a string because "X" is a valid value
        self.ap_cost: str = ""
        self.mp_cost: str = ""
        self.description: str = ""

    @staticmethod
    def from_json(d: dict) -> 'Enhancement':
        e = Enhancement()
        e.name = d['name']
        e.cost = d['cost']
        e.repeatable = d['repeatable']
        e.sustained = d['sustained']
        e.dependent_on = d['dependent_on']
        e.ap_cost = d['ap_cost']
        e.mp_cost = d['mp_cost']
        e.description = d['description']
        return e

    def fixup(self):
        if "Repeatable" in self.cost:
            self.repeatable = True
            self.cost = re.sub(r',? ?Repeatable', '', self.cost)

        if "Sustained" in self.cost:
            self.sustained = True
            self.cost = re.sub(r',? ?Sustained', '', self.cost)

        # doesn't use full "Requires" because of a spelling error in "Luminous Burst" (page 129)
        if "Requi" in self.cost:
            regex = re.compile(r',? ?Requir?es ([a-zA-Z ]+)')
            m = regex.search(self.cost)
            assert m is not None
            self.dependent_on = m.group(1)
            self.cost = regex.sub('', self.cost)

        ap = re.search(r'([0-9X]+) ?AP', self.cost)
        self.ap_cost = (ap.group(1) if ap else "0")

        mp = re.search(r'([0-9X]+) ?MP', self.cost)
        self.mp_cost = (mp.group(1) if mp else "0")

        return self

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "cost": self.cost,
            "repeatable": ", *Repeatable*" if self.repeatable else "",
            "sustained": ", *Sustained*" if self.sustained else "",
            "dependent_on": f", Requires: {self.dependent_on}" if self.dependent_on else "",
            "ap_cost": self.ap_cost,
            "mp_cost": self.mp_cost,
            "description": self.description,
        }
        return template.format(**args)


template = """
### {name} (**{cost}**{repeatable}{sustained}{dependent_on})
{description}
"""
