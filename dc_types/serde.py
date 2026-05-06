import json
from dc_types.item import Item
from dc_types.frag_list import FragList
from dc_types.spell import Spell
from dc_types.enhancement import Enhancement
from dc_types.condition import Condition
from dc_types.maneuver import Maneuver
from dc_types.text_frag import TextFrag
from dc_types.proto_item import DCProtoItem


class DCObjEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FragList):
            return o._frags
        if isinstance(o, (Item, Enhancement, TextFrag, DCProtoItem)):
            d = o.__dict__
            # if isinstance(o, Spell):
            #     d.pop("_current_enhmt")
            return d
        else:
            return json.JSONEncoder.default(self, o)


def dc_obj_decoder(d: dict):
    if "_type" not in d:
        return d
    match d["_type"]:
        case "spell":
            return Spell.from_json(d)
        case "enhancement":
            return Enhancement.from_json(d)
        case "condition":
            return Condition.from_json(d)
        case "maneuver":
            return Maneuver.from_json(d)
        case _:
            raise Exception(
                f"Unable to decode type: {d['_type']}. Please add it to dc_obj_decoder"
            )
