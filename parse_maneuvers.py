#!/usr/bin/env python

from typing import Optional
import json
from lib.markup import MarkupStyle, markup
from lib.utils import get_file_paths, eprint, save_file, flatten_pages
from utils.colors import colors
from utils.args import Args
from utils.split import split_items_default
from lib.fixup_text import fixup_name, fixup_description
from dc_types.frag_list import FragList
from dc_types.serde import DCObjEncoder
from dc_types.proto_item import DCProtoItem
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
    file = args.file or get_file_paths()['input']
    with open(file, 'r') as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range] # Filter pages

    frags: FragList = flatten_pages(pages)
    maneuvers_raw: list[DCProtoItem] = split_items_default(frags)

    if args.raw:
        if args.unprocessed:
            # Consume all TextFrags that can be processed
            parse_maneuvers(maneuvers_raw)
            pass
        return maneuvers_raw
    else:
        maneuvers: list[Maneuver] = parse_maneuvers(maneuvers_raw)
        return maneuvers

def parse_maneuver(proto_maneuver: DCProtoItem) -> Maneuver:
    sections: list[str] = ["attack", "defense", "grapple", "utility"]
    maneuver: Maneuver = Maneuver()
    maneuver.name = proto_maneuver.name
    maneuver.page = proto_maneuver.frags.next_get_page()
    maneuver.kind = sections[proto_maneuver.section]
    frags: FragList = proto_maneuver.frags
    desc: str = ""
    prev_frag: Optional[TextFrag] = None
    frag: TextFrag = frags.next()

    while frag.font == "f5":
        maneuver.summary += markup(frag, prev_frag, MarkupStyle.MARKDOWN)
        prev_frag = frag
        frag = frags.next()
    maneuver.summary = maneuver.summary.strip()

    while frag.font != "f5":
        prev_frag = frag
        frag = frags.next()

    while frag.font == "f5":
        maneuver.cost += frag.text
        prev_frag = frag
        frag = frags.next()

    while frag.font != "f21" and not frags.is_empty():
        frag = frags.next()
    # for frag in frags:
    #     desc += markup(frag, prev_frag, MarkupStyle.MARKDOWN)
    #     prev_frag = frag

    maneuver.description = fixup_description(desc)
    return maneuver

def parse_maneuvers(conds_raw: list[DCProtoItem]) -> list[Maneuver]:
    conds: list[Maneuver] = []
    for raw_cond in conds_raw:
        try:
            page_number = raw_cond.frags.next_get_page()
        except:
            eprint(raw_cond.__dict__)
            raise
        try:
            conds.append(parse_maneuver(raw_cond))
        except Exception as e:
            eprint(f"{colors.RED}Error{colors.ENDC} with condition {colors.GREEN}{raw_cond.name}{colors.ENDC}, starts on page: {colors.BLUE}{page_number}{colors.ENDC}")
            raise e

            continue
    return conds

if __name__ == "__main__":
    import os
    args = Args(default_page=173)

    if args.type != "conditions" and args.type:
        raise Exception("Parsing conditions, but type is not conditions")

    maneuvers: list = main(args)

    if args.print and not args.write:
        print(json.dumps(maneuvers, cls=DCObjEncoder))

    if args.write and not args.raw:
        out_folder = get_file_paths()['output']
        out_folder += 'conditions/'

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
