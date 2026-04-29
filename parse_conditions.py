#!/usr/bin/env python

import json
import re
from lib.dc_types import DCObjEncoder, DCProtoItem, TextItem, assert_font, MarkupStyle, markup, Condition
from lib.utils import get_file_paths, Args, colors, eprint, save_file
from lib.fixup_text import fixup_name, fixup_description

# pages 173-174
def main(args: Args) -> list[Condition] | list[DCProtoItem]:
    if args.all:
        # 173-174
        page_range = slice(173 - 1, 174)
    else:
        page_range = args.page_range

    # Open file
    file = args.file or get_file_paths()['input']
    with open(file, 'r') as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range] # Filter pages

    conditions_raw: list[DCProtoItem] = split_conditions(pages)

    if args.raw:
        if args.unprocessed:
            # Consume all TextItems that can be processed
            conditions: list[Condition] = parse_conditions(conditions_raw)
            pass
        return conditions_raw
    else:
        conditions: list[Condition] = parse_conditions(conditions_raw)
        return conditions


def split_conditions(pages: list[dict]) -> list[DCProtoItem]:
    conditions: list[DCProtoItem] = []
    current_condition: DCProtoItem = DCProtoItem()
    false_positives = []
    # f2: page numbers, f9, f1: footers
    discard_fonts: list[str] = ["g_d0_f2", "g_d0_f9", "g_d0_f1"]
    spell_has_name: bool = False

    for page in pages:
        page_number: int = page['page']
        for text_item in page['textItems']:
            item: TextItem = TextItem(text_item, page_number)

            # f3: heading font
            if item.font == "g_d0_f3" and item.font_size < 15:
                if spell_has_name:
                    # New Spell; commit and initialise a new one
                    if current_condition.name.strip() != "" and not any(fp in current_condition.name.lower() for fp in false_positives):
                        current_condition.name = fixup_name(current_condition.name.lower()).title()
                        conditions.append(current_condition)
                    current_condition = DCProtoItem()
                    spell_has_name = False
                current_condition.name += item.text
            else:
                spell_has_name = True
                if item.font not in discard_fonts:
                    current_condition.items.append(item)

    current_condition.name = fixup_name(current_condition.name.lower()).title()
    conditions.append(current_condition)
    return conditions

def parse_condition(proto_cond: DCProtoItem) -> Condition:
    cond = Condition()
    cond.name = fixup_name(proto_cond.name.replace(' ', ''))
    if cond.name.endswith('X'):
        cond.stacking = True
        cond.name = cond.name.rstrip(' X')
    cond.page = proto_cond.items[0].page
    items: list[TextItem] = proto_cond.items
    desc = ""
    prev_item = None

    for item in items:
        desc += markup(item, prev_item, MarkupStyle.MARKDOWN)
        prev_item = item

    cond.description = fixup_description(desc)
    return cond

def parse_conditions(conds_raw: list[DCProtoItem]) -> list[Spell]:
    conds: list[Spell] = []
    for raw_cond in conds_raw:
        page_number = raw_cond.items[0].page
        try:
            conds.append(parse_condition(raw_cond))
        except Exception as e:
            eprint(f"{colors.RED}Error{colors.ENDC} with condition {colors.GREEN}{raw_cond.name}{colors.ENDC}, starts on page: {colors.BLUE}{page_number}{colors.ENDC}")
            raise e

            continue
    return conds

cond_template = """---
name: {name}
stacking: {stacking}
---
{desc}
"""

def gen_markdown(cond: Condition) -> str:
    args = {
        "name": cond.name,
        "desc": cond.description,
        "stacking": cond.stacking,
    }

    return cond_template.format(**args)


if __name__ == "__main__":
    import os
    args = Args(default_page=173)

    if args.type != "conditions" and args.type:
        raise Exception("Parsing conditions, but type is not conditions")

    conditions: list = main(args)

    if args.print and not args.write:
        print(json.dumps(conditions, cls=DCObjEncoder))

    if args.write and not args.raw:
        out_folder = get_file_paths()['output']
        out_folder += 'conditions/'

        try:
            os.makedirs(out_folder)
        except FileExistsError:
            eprint(f"{colors.YELLOW}folder already exists{colors.ENDC}")

        for cond in conditions:
            name = cond.name
            markdown = gen_markdown(cond)
            if args.print:
                eprint(f"{out_folder}{name}.md")
                print(markdown)
            else:
                save_file(out_folder, name, markdown)
