class Condition:
    def __init__(self):
        self.type: str = "condition"
        self.page: int = -1
        self.name: str = ""
        self.description: str = ""
        self.stacking: bool = False

    @staticmethod
    def from_json(d: dict):
        c = Condition()
        c.page = int(d["page"])
        c.name = d["name"]
        c.description = d["describution"]
        c.stacking = d["stacking"]

    def markdown(self) -> str:
        args = {
            "name": self.name,
            "desc": self.description,
            "stacking": self.stacking,
        }

        return template.format(**args)

template = """---
name: {name}
stacking: {stacking}
---
{desc}
"""
