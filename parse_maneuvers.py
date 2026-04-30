#!/usr/bin/env python

from typing import Optional
import json
from lib.markup import MarkupStyle, markup
from lib.utils import get_file_paths, Args, colors, eprint, save_file, flatten_pages
from lib.fixup_text import fixup_name, fixup_description
from dc_types.item_list import ItemList
from dc_types import DCObjEncoder, DCProtoItem, TextItem
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

    items: ItemList = flatten_pages(pages)
    maneuvers_raw: list[DCProtoItem] = split_maneuvers(items)

    if args.raw:
        if args.unprocessed:
            # Consume all TextItems that can be processed
            parse_maneuvers(maneuvers_raw)
            pass
        return maneuvers_raw
    else:
        maneuvers: list[Maneuver] = parse_maneuvers(maneuvers_raw)
        return maneuvers


def split_maneuvers(items: ItemList) -> list[DCProtoItem]:
    sections: list[str] = ["attack", "defense", "grapple", "utility"]
    # section: str = sections.pop(0)
    section: str = "<NONE>"
    maneuvers: list[DCProtoItem] = []
    current_maneuver: DCProtoItem = DCProtoItem()
    current_maneuver.section = "attack"
    false_positives = []
    # f2: page numbers, f9, f1: footers
    discard_fonts: list[str] = ["f2", "f9", "f1"]
    spell_has_name: bool = False
    prev_font: str = ""

    for item in items:
        if prev_font == "f4" and item.font != "f4":
            # End of section header
            section = sections.pop(0)
            prev_font = item.font
            continue
        if item.font == "f4":
            # Section header
            # commit and initilise a new maneuver
            if current_maneuver.name.strip() != "" and not any(fp in current_maneuver.name.lower() for fp in false_positives):
                current_maneuver.name = fixup_name(current_maneuver.name.lower()).title()
                maneuvers.append(current_maneuver)
            current_maneuver = DCProtoItem()
            current_maneuver.section = section
            spell_has_name = False

        # f3: heading font
        if item.font == "f3" and item.font_size < 15:
            # eprint(f"{item.text}, {item.font_size}")
            if spell_has_name:
                # New Maneuver; commit and initialise a new one
                if current_maneuver.name.strip() != "" and not any(fp in current_maneuver.name.lower() for fp in false_positives):
                    current_maneuver.name = fixup_name(current_maneuver.name.lower()).title()
                    maneuvers.append(current_maneuver)
                current_maneuver = DCProtoItem()
                current_maneuver.section = section
                spell_has_name = False
            current_maneuver.name += item.text
        else:
            spell_has_name = True
            if item.font not in discard_fonts:
                current_maneuver.items.append(item)
        prev_font = item.font

    current_maneuver.name = fixup_name(current_maneuver.name.lower()).title()
    maneuvers.append(current_maneuver)
    return maneuvers

def parse_maneuver(proto_maneuver: DCProtoItem) -> Maneuver:
    maneuver: Maneuver = Maneuver()
    maneuver.name = proto_maneuver.name
    maneuver.page = proto_maneuver.items[0].page
    maneuver.kind = proto_maneuver.section
    items: list[TextItem] = proto_maneuver.items
    desc: str = ""
    prev_item: Optional[TextItem] = None
    item: TextItem = items.pop(0)

    while item.font == "f5":
        maneuver.summary += markup(item, prev_item, MarkupStyle.MARKDOWN)
        prev_item = item
        item = items.pop(0)
    maneuver.summary = maneuver.summary.strip()

    while item.font != "f5":
        prev_item = item
        item = items.pop(0)

    while item.font == "f5":
        maneuver.cost += item.text
        prev_item = item
        item = items.pop(0)

    while item.font != "f21":
        item = items.pop(0)
    # for item in items:
    #     desc += markup(item, prev_item, MarkupStyle.MARKDOWN)
    #     prev_item = item

    maneuver.description = fixup_description(desc)
    return maneuver

def parse_maneuvers(conds_raw: list[DCProtoItem]) -> list[Maneuver]:
    conds: list[Maneuver] = []
    for raw_cond in conds_raw:
        try:
            page_number = raw_cond.items[0].page
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
