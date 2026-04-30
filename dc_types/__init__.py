import json
from .spell import Spell
from .enhancement import Enhancement
from .condition import Condition
from .maneuver import Maneuver
from .text_item import TextItem
from .proto_item import DCProtoItem


class DCObjEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell, Enhancement, TextItem, DCProtoItem, Condition, Maneuver)):
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
        case 'maneuver':
            return Maneuver.from_json(d)
    return d
