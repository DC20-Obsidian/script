import json
from .spell import Spell
from .enhancement import Enhancement
from .condition import Condition

class TextItem:
    def __init__(self, item: dict, page: int):
        self.page: int = page
        self.text: str = str(item['text'])
        self.font: str = str(item['fontName']).removeprefix('g_d0_')
        self.font_size = int(item['fontSize'])

class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.items: list[TextItem] = []

class DCObjEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell, Enhancement, TextItem, DCProtoItem, Condition)):
            d = o.__dict__
            # if isinstance(o, Spell):
            #     d.pop("_current_enhmt")
            return d
        else:
            return json.JSONEncoder.default(self, o)

def dc_obj_decoder(d: dict):
    if 'type' not in d:
        return d
    match d['type']:
        case 'spell':
            return Spell.from_json(d)
        case 'enhancement':
            return Enhancement.from_json(d)
        case 'condition':
            return Condition.from_json(d)
    return d
