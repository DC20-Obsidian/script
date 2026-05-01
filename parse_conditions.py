#!/usr/bin/env python

import json
from lib.markup import MarkupStyle, markup
from lib.utils import get_file_paths, eprint, save_file, flatten_pages
from utils.colors import colors
from utils.args import Args
from utils.split import split_items_default
from lib.fixup_text import fixup_name, fixup_description
from dc_types.serde import DCObjEncoder
from dc_types.proto_item import DCProtoItem, parse_proto_items
from dc_types.text_frag import TextFrag
from dc_types.condition import Condition
from dc_types.frag_list import FragList


# pages 173-174
def main(args: Args) -> list[Condition] | list[DCProtoItem]:
    if args.all:
        # 173-174
        page_range = slice(173 - 1, 174)
    else:
        page_range = args.page_range

    # Open file
    file = args.file or get_file_paths()["input"]
    with open(file, "r") as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range]  # Filter pages

    frags: FragList = flatten_pages(pages)

    conditions_raw: list[DCProtoItem] = split_items_default(frags)

    if args.raw:
        if args.unprocessed:
            # Consume all TextFrags that can be processed
            parse_proto_items(conditions_raw, parse_condition)
            pass
        return conditions_raw
    else:
        conditions: list[Condition] = parse_proto_items(conditions_raw, parse_condition)
        return conditions


def parse_condition(proto_cond: DCProtoItem) -> Condition:
    cond = Condition()
    cond.name = fixup_name(proto_cond.name.replace(" ", ""))
    if cond.name.endswith("X"):
        cond.stacking = True
        cond.name = cond.name.rstrip(" X")
    cond.page = proto_cond.frags.next_get_page()
    frags: FragList = proto_cond.frags
    desc = ""
    prev_frag = None

    for frag in frags:
        desc += markup(frag, prev_frag, MarkupStyle.MARKDOWN)
        prev_frag = frag

    cond.description = fixup_description(desc)
    return cond


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
        out_folder = get_file_paths()["output"]
        out_folder += "conditions/"

        try:
            os.makedirs(out_folder)
        except FileExistsError:
            eprint(f"{colors.YELLOW}folder already exists{colors.ENDC}")

        for cond in conditions:
            assert isinstance(cond, Condition)
            name = cond.name
            markdown = gen_markdown(cond)
            if args.print:
                eprint(f"{out_folder}{name}.md")
                print(markdown)
            else:
                save_file(out_folder, name, markdown)
