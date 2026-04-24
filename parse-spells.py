#!/usr/bin/env python

import json
import argparse

page = 70
# spell range: 68-114

parser = argparse.ArgumentParser(
    prog='parse-spells'
)
parser.add_argument('page', default=page, nargs='?')
parser.add_argument('last_page', nargs='?')
args = parser.parse_args()

page = int(args.page)
last_page = int(args.last_page if args.last_page else page)
page_range = slice(page - 1, last_page)

def eprint(*args, **kw):
    import sys
    print(*args, file=sys.stderr, **kw)

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
        # if len(text) >= 3:
        name += "-"
    eprint(f"-----name-----> {name}")
    return name
    

class Spell:
    name: str = "<none>"
    source: str = "<none>"
    school: str = "<none>"
    tags: str = "<none>"
    cost: str = "<none>"
    range: str = "<none>"
    duration: str = "<none>"
    description: str = ""

class EncodeJSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell,)):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)

with open('./dc20_0.10beta.json', 'r') as file:
    data = json.load(file)

spells = []
text_items = data['pages'][page_range]

def process_page(page_text, spells):
    current_spell = Spell()
    current_item = 'name'
    for i, text_item in enumerate(page_text):
        text = text_item['text']
        push_spell = False

        match current_item:
            case 'name':
                if text == "Source":
                    current_spell.name = extract_spell_name(page_text, i)
                    current_item = 'source'
            case 'source':
                if text[0] == ':':
                    current_spell.source = text[2:]
                    current_item = 'school'
            case 'school':
                if text[0] == ':':
                    current_spell.school = text[2:]
                    current_item = 'tags'
            case 'tags':
                if text[0] == ':':
                    current_spell.tags = text[2:]
                    current_item = 'cost'
            case 'cost':
                if text[0] == ':':
                    current_spell.cost = text[2:]
                    current_item = 'range'
            case 'range':
                if text[0] == ':':
                    current_spell.range = text[2:]
                    current_item = 'duration'
            case 'duration':
                if text[0] == ':':
                    current_spell.duration = text[2:]
                    current_item = 'desc'
                    push_spell = False
            case 'desc':
                if text != 'Spell Enhancements':
                    current_spell.description += text
                else:
                    current_item = 'name'
                    push_spell = True
            # TODO add table parsing and fix spaces

        if push_spell:
            spells.append(current_spell)
            current_spell = Spell()

        eprint(text)

for page in text_items:
    process_page(page['textItems'], spells)

# for spell in spells:
#     print(json.dumps(spell.__dict__))
print(json.dumps(spells, cls=EncodeJSON))

