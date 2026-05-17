#!/usr/bin/env python
import os
import json
from typing import Type
from collections.abc import Callable
from pathlib import Path
from utils.args import Args
from utils.colors import colors
from lib.utils import flatten_pages, eprint
from dc_types.proto_item import DCProtoItem
from utils.parse import parse_proto_items
from dc_types.frag_list import FragList
from dc_types.serde import dc_obj_decoder, DCObjEncoder
from dc_types.item import Item
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

dc20_version: str = "0.10.5"
prefix: Path = Path("./dc-obsidian")


def main(args: Args):
    (item_type, parser) = get_type(args.type)

    if args.all:
        page_range = item_type.get_default_page_range()
        assert page_range.start < page_range.stop
        args.page_range = page_range

    if args.raw:
        items_raw: list[DCProtoItem] = load_raw(args, item_type)
        if args.unprocessed:
            # Consume all TextFrags that can be processed
            parse_proto_items(items_raw, parser)
        print(json.dumps(items_raw, cls=DCObjEncoder))
        return

    items: list[Item] = load_parsed(args, item_type, parser)
    save_file: Path = item_type.get_save_file(Path(f"{prefix}/json"), dc20_version)

    if args.print:
        if not args.markdown:
            print(json.dumps(items, cls=DCObjEncoder))
            eprint(save_file)
        else:
            for item in items:
                path: Path = item.markdown_path(prefix)
                print(
                    f"{colors.BLUE}{path.parent}{colors.ENDC}/{colors.GREEN}{path.name}{colors.ENDC}"
                )
                print(item.markdown())

    if args.write:
        if not args.markdown:
            with open(save_file, "w") as file:
                file.write(json.dumps(items, cls=DCObjEncoder, indent=2))
        else:
            for item in items:
                markdown: str = item.markdown()
                path: Path = item.markdown_path(prefix)
                os.makedirs(path.parent, exist_ok=True)
                with open(path, "w") as file:
                    file.write(markdown)
                item.save_subitems(prefix)


def load_parsed(
    args: Args, item_type: Type[Item], parser: Callable[[DCProtoItem], Item]
) -> list[Item]:
    if args.saved:
        return load_saved(args, item_type)
    else:
        items_raw: list[DCProtoItem] = load_raw(args, item_type)
        return list(map(parser, items_raw))


def load_saved(args: Args, item_type: Type[Item]) -> list[Item]:
    saved_file = args.file or item_type.get_save_file(Path(f"{prefix}/json"), dc20_version)
    eprint(f"Loading saved data from {colors.BLUE}{saved_file}{colors.ENDC}")
    with open(saved_file, "r") as file:
        return json.load(file, object_hook=dc_obj_decoder)


def load_raw(args: Args, item_type: Type[Item]) -> list[DCProtoItem]:
    page_range = args.page_range

    file_name: str = (
        args.file or rf"{prefix}/json/dc20_{dc20_version}_pdf_filtered.json"
    )
    eprint(f"Loading raw data from {colors.BLUE}{file_name}{colors.ENDC}")
    with open(file_name, "r") as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range]  # Filter pages

    frags: FragList = flatten_pages(pages)
    assert not frags.is_empty(), "Unable to load raw items, frags is empty"
    items_raw: list[DCProtoItem] = item_type.split(frags)
    assert not len(items_raw) == 0, "Unable to load raw items, split into 0 items"

    return items_raw


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


if __name__ == "__main__":
    args: Args = Args(-1)
    main(args)
