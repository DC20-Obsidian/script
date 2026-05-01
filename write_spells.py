#!/usr/bin/env python
import os
import json

import parse_spells
from lib.utils import eprint, get_file_paths
from utils.colors import colors
from utils.args import Args
from dc_types import dc_obj_decoder
from dc_types.spell import Spell
from dc_types.enhancement import Enhancement

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
        assert isinstance(spell, Spell)
        name = spell.name
        markdown = spell.markdown()
        if args.print:
            print(markdown)
        else:
            save_file(out_folder, name, markdown)

def save_file(path: str, name: str, s: str):
    name = f'{path}{name}.md'
    with open(name, 'w') as file:
        file.write(s)

if __name__ == "__main__":
    args = Args(default_page=71)
    if args.type != "spells" and args.type:
        raise Exception("Parsing spells, but type is not spells")
    main(args)
