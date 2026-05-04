#!/usr/bin/env python

from dc_types.enhancement import Enhancement
from typing import Optional
import json
from lib.markup import MarkupStyle, markup, assert_font
from lib.utils import get_file_paths, eprint, save_file, flatten_pages
from utils.colors import colors
from utils.args import Args
from utils.split import split_items_default, split_items
from lib.fixup_text import fixup_name, fixup_description
from dc_types.frag_list import FragList
from dc_types.serde import DCObjEncoder
from dc_types.proto_item import DCProtoItem, parse_proto_items
from dc_types.text_frag import TextFrag
from dc_types.maneuver import Maneuver


# pages 173-174
def main(args: Args) -> list[Maneuver] | list[DCProtoItem]:
    if args.all:
        # 52-59
        page_range = slice(52 - 1, 59)
    else:
        page_range = args.page_range

    # Open file
    file = args.file or get_file_paths()["input"]
    with open(file, "r") as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range]  # Filter pages

    frags: FragList = flatten_pages(pages)
    maneuvers_raw: list[DCProtoItem] = split_items_default(frags)

    if args.raw:
        if args.unprocessed:
            # Consume all TextFrags that can be processed
            parse_proto_items(maneuvers_raw, parse_maneuver)
        return maneuvers_raw
    else:
        maneuvers: list[Maneuver] = parse_proto_items(maneuvers_raw, parse_maneuver)
        return maneuvers


def parse_maneuver(proto_maneuver: DCProtoItem) -> Maneuver:
    two_line_ranges: list[str] = [
        "Piercing Shot",
        "Parry",
    ]  # .range extends over two lines
    sections: list[str] = ["attack", "defense", "grapple", "utility"]
    maneuver: Maneuver = Maneuver()
    maneuver.name = proto_maneuver.name
    maneuver.page = proto_maneuver.frags.next_get_page()
    maneuver.kind = sections[proto_maneuver.section]
    frags: FragList = proto_maneuver.frags

    def plain_text(frag: TextFrag) -> bool:
        return frag.font == "f5"

    if (
        maneuver.name != "Heroic Pass Through"
    ):  # "Heroic Pass Through" does not have a cost or range listed
        if frags.match_next(lambda frag: frag.font == "f5"):
            maneuver.summary = frags.markup_while(plain_text).strip()

        frags.discard_until(plain_text)

        maneuver.cost = frags.cat_while(lambda frag, _: frag.font == "f5")

        frags.discard_until(plain_text)

        range: TextFrag = frags.next()
        assert_font(range, ["f5"])
        maneuver.range = range.text
        if maneuver.name in two_line_ranges:
            range: TextFrag = frags.next()
            assert_font(range, ["f5"])
            maneuver.range += f" {range.text}"
    else:
        maneuver.cost = "Pass Through Action (1 AP)"
        maneuver.range = "Self"

    maneuver.description = frags.markup_while(lambda frag: frag.font != "f27").strip()
    frags.discard_with_font(["f27"])

    enhancements: list[DCProtoItem] = split_items(frags, ["f21", "f7"], [], 15, [], [])

    maneuver.enhancements = list(map(parse_enhancement, enhancements))

    return maneuver.fixup()


def parse_enhancement(proto_enhancement: DCProtoItem) -> Enhancement:
    enhancement: Enhancement = Enhancement()
    enhancement.name = proto_enhancement.name
    frags: FragList = proto_enhancement.frags

    (cost, _, desc) = frags.cat_while(lambda _, s: ")" not in s).partition(")")
    enhancement.cost = cost.lstrip(": (")
    enhancement.description = f"{desc} {frags.markup_while(lambda _: True)}".strip()

    return enhancement.fixup()


if __name__ == "__main__":
    import os

    args = Args(default_page=173)

    if args.type != "maneuvers" and args.type:
        raise Exception("Parsing conditions, but type is not conditions")

    maneuvers: list = main(args)

    if args.print and not args.write:
        print(json.dumps(maneuvers, cls=DCObjEncoder))

    if args.write and not args.raw:
        out_folder = get_file_paths()["output"]
        out_folder += "conditions/"

        try:
            os.makedirs(out_folder)
        except FileExistsError:
            eprint(f"{colors.YELLOW}folder already exists{colors.ENDC}")

        for maneuver in maneuvers:
            assert isinstance(maneuver, Maneuver)
            name = maneuver.name
            markdown = maneuver.markdown()
            if args.print:
                eprint(f"{out_folder}{name}.md")
                print(markdown)
            else:
                save_file(out_folder, name, markdown)
