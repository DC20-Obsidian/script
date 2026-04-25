#!/usr/bin/env python

import json
import argparse

from utils import colors, eprint
from dc_types import Spell, Enhancement, EncodeJSON

first_page = 70
# spell range: 68-114

parser = argparse.ArgumentParser(
    prog='parse-spells'
)
parser.add_argument('page', default=first_page, nargs='?')
parser.add_argument('last_page', nargs='?')
args = parser.parse_args()

first_page = int(args.page)
last_page = int(args.last_page if args.last_page else first_page)
page_range = slice(first_page - 1, last_page)

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
    eprint(f"{colors.OKGREEN}-----name-----> {name}{colors.ENDC}")
    return name

def process_page(page_text, spells):
    current_spell = Spell()
    current_item = 'name'
    current_enhancement = ""
    for i, text_item in enumerate(page_text):
        prev_text: str = page_text[i-1]['text'] if i != 0 else " "
        next_text: str = page_text[i+1]['text'] if i + 1 < len(page_text) else " "
        prev_colon: bool = prev_text[-1:] == ':'
        text: str = text_item['text']
        push_spell = False
        debug_line = True

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
                # Check if line is a page number
                if text_item['fontName'] == 'g_d0_f3' or 'THE DUNGEON COACH' in text or text.isdigit():
                    push_spell = True
                    current_item = 'name'
                else:
                    text_p = text.rstrip(':').lower()
                    if (text.endswith(':') or next_text.startswith(':')) and (
                        not text_p.endswith('success') and not text_p.endswith('failure')):
                        if current_enhancement != "":
                            current_spell.enhancements[current_enhancement].finish()
                        current_enhancement = text.rstrip(':')
                    if current_enhancement != "":
                        current_spell.enhancements.setdefault(current_enhancement, Enhancement())
                        current_spell.enhancements[current_enhancement].description += text.lstrip(': ')
            # TODO add table parsing and fix spaces

        if push_spell:
            current_spell.enhancements[current_enhancement].finish()
            spells.append(current_spell)
            current_spell = Spell()
            current_enhancement = ""

        if debug_line:
            eprint(text)
            # eprint(f"{text}     - {text_item['fontName']}")
            # eprint(text_item['fontName'])

with open('./dc20_0.10beta.json', 'r') as file:
    data = json.load(file)

spells = []
text_items = data['pages'][page_range]

for i, page in enumerate(text_items):
    eprint(f"{colors.HEADER}==========> processing page: {i + first_page}{colors.ENDC}")
    process_page(page['textItems'], spells)

# for spell in spells:
#     print(json.dumps(spell.__dict__))
print(json.dumps(spells, cls=EncodeJSON))

