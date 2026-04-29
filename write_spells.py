#!/usr/bin/env python
import os
import json

import parse_spells
from lib.dc_types import Spell, DCObjEncoder, Enhancement, dc_obj_decoder
from lib.utils import eprint, Args, get_file_paths

def main(args: Args):
    out_folder = get_file_paths()['output']
    if args.saved:
        in_file = out_folder + 'json/spells_0.10.5.json'
        with open(in_file, 'r') as file:
            spells = json.load(file, object_hook=dc_obj_decoder)
    else:
        spells: list = parse_spells.main(args)
    out_folder += 'spells/'

    if args.raw:
        exit(0)

    if not args.write and not args.print:
        eprint(f"{colors.YELLOW}Warning{colors.ENDC}: write_spells called, but args.write is not set. Skipping")
        exit(0)

    try:
        os.makedirs(out_folder)
    except FileExistsError:
        eprint("folder already exists")

    for spell in spells:
        name = spell.name
        markdown = gen_markdown(spell)
        if args.print:
            print(markdown)
        else:
            save_file(out_folder, name, markdown)

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

## Spell Enhancements
{enhancements}
"""

def list_to_yaml(li: list[str]) -> str:
    a = " - "
    a += f'\n - '.join(map( lambda s: f'"{s}"', li))
    return a

def enhancements(enhancements: list[Enhancement]) -> str:
    s: str = ""
    for enh in enhancements:
        s += markdown_enhancement(enh)
    return s

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
        "page": spell.page,
        "description": spell.description,
        "enhancements": enhancements(spell.enhancements)
    }
    return template.format(**args)

enhancement_template = """
### {name} (**{cost}**{repeatable}{sustained}{dependent_on})
{description}
"""

def markdown_enhancement(enh: Enhancement) -> str:
    args = {
        "name": enh.name,
        "cost": enh.cost,
        "repeatable": ", *Repeatable*" if enh.repeatable else "",
        "sustained": ", *Sustained*" if enh.sustained else "",
        "dependent_on": f", Requires: {enh.dependent_on}" if enh.dependent_on else "",
        "ap_cost": enh.ap_cost,
        "mp_cost": enh.mp_cost,
        "description": enh.description,
    }
    return enhancement_template.format(**args)

def save_file(path: str, name: str, s: str):
    name = f'{path}{name}.md'
    with open(name, 'w') as file:
        file.write(s)

if __name__ == "__main__":
    args = Args(default_page=71)
    if args.type != "spells" and args.type:
        raise Exception("Parsing spells, but type is not spells")
    main(args)
