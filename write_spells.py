#!/usr/bin/env python
import os
import json

import parse_spells
from lib.dc_types import Spell, DCObjEncoder
from lib.utils import eprint, Args

def main(args: Args):
    spells: list = parse_spells.main(args)

    if args.raw:
        exit(0)

    if not args.write and not args.print:
        eprint(f"{colors.YELLOW}Warning{colors.ENDC}: write_spells called, but args.write is not set. Skipping")
        exit(0)

    try:
        os.makedirs('./dc-obsidian/spells/')
    except FileExistsError:
        eprint("folder already exists")

    for spell in spells:
        name = spell.name
        markdown = gen_markdown(spell)
        if args.print:
            print(markdown)
        else:
            save_file(name, markdown)

template = """---
name: {name}
source:
{source}
school: {school}
spell_tags:
{tags}
ap: {AP}
mp: {MP}
cost: {cost}
range: {range}
duration: {duration}
sustained: {sustained}
page: {page}
---
{description}
"""

def list_to_yaml(li: list[str]) -> str:
    a = " - "
    a += f'\n - '.join(map( lambda s: f'"{s}"', li))
    return a

def gen_markdown(spell: Spell) -> str:
    args= {
       "name": spell.name,
        "source": list_to_yaml(spell.source),
        "school": spell.school,
        "tags": list_to_yaml(spell.tags),
        "cost": spell.cost,
        "range": spell.range,
        "duration": spell.duration,
        "AP": spell.ap_cost,
        "MP": spell.mp_cost,
        "sustained": spell.sustained,
        "page": spell.page_number,
        "description": spell.description
    }
    return template.format(**args)

def save_file(name: str, s: str):
    name = f'./dc-obsidian/spells/{name}.md'
    with open(name, 'w') as file:
        file.write(s)

if __name__ == "__main__":
    args = Args(default_page=71)
    if args.type != "spells" and args.type:
        raise Exception("Parsing spells, but type is not spells")
    main(args)
