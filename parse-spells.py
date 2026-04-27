#!/usr/bin/env python

import json

from utils import colors, eprint, Args
from dc_types import Spell, Enhancement, DCObjEncoder, TextItem, DCProtoItem

def main():
    # Parse args
    args = Args(default_page=71)
    if args.all:
        page_range = slice(70, 145)
    else:
        page_range = args.page_range

    # Open file
    with open('./dc20_0.10.5beta.json', 'r') as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range] # Filter pages

    # Split spells
    spells: list[DCProtoItem] = split_spells(pages)

    print(json.dumps(spells, cls=DCObjEncoder))

def split_spells(pages: list[dict]):
    spells: list[DCProtoItem] = []
    current_spell: DCProtoItem = DCProtoItem()
    false_positives = ["summontraits"]
    # f2: page numbers, f9, f1: footers
    discard_fonts: list[str] = ["g_d0_f2", "g_d0_f9", "g_d0_f1"]
    spell_has_name: bool = False

    for page in pages:
        page_number: int = page['page']
        for text_item in page['textItems']:
            item: TextItem = TextItem(text_item, page_number)

            # f3: heading font
            if item.font == "g_d0_f3":
                if spell_has_name:
                    # New Spell; commit and initilise a new one
                    if current_spell.name.strip() != "" and not any(fp in current_spell.name.lower() for fp in false_positives):
                        spells.append(current_spell)
                    current_spell = DCProtoItem()
                    spell_has_name = False
                current_spell.name += item.text
            else:
                spell_has_name = True
                if item.font not in discard_fonts:
                    current_spell.items.append(item)

    spells.append(current_spell)
    return spells

def extract_spell_name(text_items: dict, i: int):
    i_init = i
    # Just hit "Source", backtrack to name start
    i -= 1
    while i > 0 and text_items[i]['fontName'] == 'g_d0_f3':
        i -= 1
    if i != 0:
        i += 1
    name = ""
    # TODO fix spaces and cace
    for i in range(i, i_init):
        text = text_items[i]['text']
        name += text
    # Semi-fix caseing
    name = ' '.join([ s.capitalize() for s in name.split(' ') ])
    eprint(f"{colors.GREEN}-----name-----> {name}{colors.ENDC}")
    return name

def process_page(page_text, spells, page_number):
    current_spell = Spell()
    current_item = 'name'
    current_enhancement = ""
    for i, text_item in enumerate(page_text):
        prev_text: str = page_text[i-1]['text'] if i != 0 else " "
        next_text: str = page_text[i+1]['text'] if i + 1 < len(page_text) else " "
        prev_colon: bool = prev_text[-1:] == ':'
        text: str = text_item['text']
        font: str = text_item['fontName']
        push_spell = False

        # eprint(f"{current_item=}")
        match current_item:
            case 'name':
                if text[:6] == "Source" or text[:10] == "Spell List":
                    current_spell.name = extract_spell_name(page_text, i)
                    current_item = 'source'
            case 'source':
                if text[0] == ':' or prev_colon :
                    current_spell.source = text.strip(': ').split(', ')
                    current_item = 'school'
            case 'school':
                if text[0] == ':' or prev_colon :
                    current_spell.school = text.strip(': ')
                    current_item = 'tags'
            case 'tags':
                if text[0] == ':' or prev_colon :
                    current_spell.tags = text.strip(': ').split(', ')
                    current_item = 'cost'
            case 'cost':
                if text[0] == ':' or prev_colon :
                    current_spell.cost = text.strip(': ')
                    current_item = 'range'
            case 'range':
                if text[0] == ':' or prev_colon :
                    current_spell.range = text.strip(': ')
                    current_item = 'duration'
            case 'duration':
                if text[0] == ':' or prev_colon :
                    current_spell.duration = text.strip(': ')
                    current_item = 'desc'
            case 'desc':
                if text.rstrip('s') != 'Spell Enhancement':
                    current_spell.description += text
                else:
                    current_item = 'enhancements'
            case 'enhancements':
                # Check if line is a spell name, school heading, footer, or page number
                if any(f == font for f in ['g_d0_f3', 'g_d0_f4']) or 'THE DUNGEON COACH' in text or (text.isdigit() and font == "g_d0_f2"):
                    push_spell = True
                    current_item = 'name'
                else:
                    # Find colons that belong to enhancement titles
                    # examples:
                    # Foo:
                    # Foo\n:Bar
                    # Foo\n:\nBar
                    # Watch out for: 'Success:', 'Failure:', 'Hit:', 'Success (5):'
                    false_positives = ["check success", "save success", "success", "failure", "save failure", "hit", ")", "dc tip", "example"]
                    text_p = text.lstrip(':').lower().strip()
                    if ((text.endswith(':') and len(text_p) > 0) or next_text.startswith(':')) and not (
                        any(text_p.startswith(prefix) for prefix in false_positives)
                        ):
                        if current_enhancement != "":
                            current_spell.enhancements[current_enhancement].finish()
                        current_enhancement = text.rstrip(':')
                    if current_enhancement != "":
                        current_spell.enhancements.setdefault(current_enhancement, Enhancement())
                        current_spell.enhancements[current_enhancement].description += text.lstrip(': ')
            # TODO add table parsing and fix spaces

        if push_spell:
            current_spell.page_number = page_number
            current_spell.enhancements[current_enhancement].finish()
            current_spell.finish()
            spells.append(current_spell)
            current_spell = Spell()
            current_enhancement = ""

        # if current_item == 'enhancements':
        #     eprint(f'{current_enhancement=}')
        highlight_list = ["Spell Enhancements", "Cost", "Duration", "Spell Tags", "School", "Source"]
        if any(s in text for s in highlight_list):
            eprint(f"{colors.CYAN}{text}{colors.ENDC}")
        else:
            # eprint(text)
            eprint(f"{text:-<50}      {colors.GREEN}{text_item['fontName']}{colors.ENDC}")

if __name__ == "__main__":
    main()

# print(json.dumps(spells, cls=DCObjEncoder))

