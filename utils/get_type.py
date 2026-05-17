from typing import Type
from collections.abc import Callable
from dc_types.item import Item
from dc_types.proto_item import DCProtoItem
from dc_types.spell import Spell
from parsers.spells import parse_spell
from dc_types.maneuver import Maneuver
from parsers.maneuvers import parse_maneuver
from dc_types.condition import Condition
from parsers.conditions import parse_condition
from dc_types.ancestry import Ancestry
from parsers.ancestries import parse_ancestry
from dc_types.talent import Talent
from parsers.talents import parse_talent
from dc_types.skill import Skill
from parsers.skills import parse_skill
from dc_types.trade import Trade
from parsers.trades import parse_trade


def get_type(s: str) -> tuple[Type[Item], Callable[[DCProtoItem], Item]]:
    match s:
        case "spells":
            return (Spell, parse_spell)
        case "conditions":
            return (Condition, parse_condition)
        case "maneuvers":
            return (Maneuver, parse_maneuver)
        case "ancestries":
            return (Ancestry, parse_ancestry)
        case "talents":
            return (Talent, parse_talent)
        case "skills":
            return (Skill, parse_skill)
        case "trades":
            return (Trade, parse_trade)
        case _:
            raise Exception(f"type {s} not supported")
