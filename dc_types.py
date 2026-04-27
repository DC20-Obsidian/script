import json
from fixup_text import fixup_name

class Spell:
    def __init__(self):
        self.name: str = ""
        self.page_number: int = -1
        self.source: list[str] = []
        self.school: str = ""
        self.tags: list[str] = []
        self.cost: str = ""
        self.range: str = ""
        self.duration: str = ""
        self.description: str = ""
        self.enhancements: dict[str, Enhancement] = {}

    def finish(self):
        self.name = fixup_name(self.name).title()
        # self.description = fixup(self.description)

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
