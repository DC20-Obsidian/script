import re
from dc_types.weapon_property import WeaponProp
from dc_types.proto_item import DCProtoItem
from utils.fixup_text import fixup_description

def parse_weapon_prop(proto: DCProtoItem) -> WeaponProp:
    prop = WeaponProp()
    prop.page = proto.page
    
    name = re.match(r"• ?\((?P<cost>-?[0-9]+)\) ?(?P<name>[a-zA-Z-]+):", proto.name)
    assert name, f"Property {proto.name} has an invalid name"

    prop.name = name.group("name")
    prop.cost = int(name.group("cost"))

    kinds: list[str] = ["Melee", "Ranged"]
    prop.kind = kinds[proto.section - 1]

    prop.description = proto.frags.markup_rest()

    requires_regex: str = r"\(Requires: ([a-zA-Z-]+)(?: Property)\) ?"
    requires = re.match(requires_regex, prop.description)
    if requires:
        prop.description = re.sub(requires_regex, "", prop.description)
        prop.requires = [requires.group(1)]

    prop.description = fixup_description(prop.description)
    return prop
