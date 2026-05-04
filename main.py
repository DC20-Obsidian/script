#!/usr/bin/env python
import os
from parsers.maneuvers import parse_maneuver
from dc_types.proto_item import DCProtoItem, parse_proto_items
from lib.utils import flatten_pages, eprint
from dc_types.frag_list import FragList
from dc_types.serde import dc_obj_decoder, DCObjEncoder
import json
from dc_types.maneuver import Maneuver
from dc_types.condition import Condition
from collections.abc import Callable
from typing import Type
from dc_types.item import Item
from dc_types.spell import Spell
from utils.args import Args
from utils.colors import colors

dc20_version: str = "0.10.5"
prefix: str = "./dc-obsidian"


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
    save_file: str = item_type.get_save_file(rf"{prefix}/json", dc20_version)

    if args.print:
        if not args.markdown:
            print(json.dumps(items, cls=DCObjEncoder))
            eprint(save_file)
        else:
            for item in items:
                (path, _, name) = item.markdown_path(prefix).rpartition("/")
                print(f"{colors.BLUE}{path}{colors.ENDC}/{colors.GREEN}{name}{colors.ENDC}")
                print(item.markdown())

    if args.write:
        if not args.markdown:
            with open(save_file, "w") as file:
                file.write(json.dumps(items, cls=DCObjEncoder))
        else:
            for item in items:
                markdown: str = item.markdown()
                path: str = item.markdown_path(prefix)
                (dir, _, name) = path.rpartition("/")
                os.makedirs(dir, exist_ok=True)
                with open(path, "w") as file:
                    file.write(markdown)



def load_parsed(args: Args, item_type: Type[Item], parser: Callable[[DCProtoItem], Item]) -> list[Item]:
    if args.saved:
        return load_saved(args, item_type)
    else:
        items_raw: list[DCProtoItem] = load_raw(args, item_type)
        return list(map(parser, items_raw))


def load_saved(args: Args, item_type: Type[Item]) -> list[Item]:
    saved_file = args.file or item_type.get_save_file(
        rf"{prefix}/json", dc20_version
    )
    with open(saved_file, "r") as file:
        return json.load(file, object_hook=dc_obj_decoder)


def load_raw(args: Args, item_type: Type[Item]) -> list[DCProtoItem]:
    page_range = args.page_range

    file_name: str = (
        args.file or rf"{prefix}/json/dc20_{dc20_version}_pdf_filtered.json"
    )
    with open(file_name, "r") as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range]  # Filter pages

    frags: FragList = flatten_pages(pages)
    items_raw: list[DCProtoItem] = item_type.split(frags)

    return items_raw


def get_type(s: str) -> tuple[Type[Item], Callable[[DCProtoItem], Item]]:
    match s:
        # case "spells":
        #     return Spell
        # case "conditions":
        #     return Condition
        case "maneuvers":
            return (Maneuver, parse_maneuver)
        case _:
            raise


if __name__ == "__main__":
    args: Args = Args(-1)
    main(args)
