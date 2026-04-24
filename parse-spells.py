#!/usr/bin/env python

import json
import argparse

page = 70
page_range = range(68, 115)

parser = argparse.ArgumentParser(
    prog='parse-spells'
)
parser.add_argument('page', default=page, nargs='?')
args = parser.parse_args()
page = int(args.page)

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
    name
    source
    school
    tags
    cost
    range
    duration
    description

class EncodeJSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell,)):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)

with open('./dc20_0.10beta.json', 'r') as file:
    data = json.load(file)

tags = ["Source", "School", "Tags", "Cost", "Range", "Duration", "Spell Enhancements"]
spells = []
current_spell = Spell()
curent_item: str = "name"

text_items = data['pages'][page - 1]['textItems']
i = 0
while i < len(text_items):
    text = text_items[i]['text']

    match curent_item:
        case 'name':
            if text == "Source":
                name = extract_spell_name(text_items, i)
                current_spell.name = name
                current_item = 'source'
                spells.append(current_spell)
                current_spell = Spell()

    eprint(text)
    i += 1

# for spell in spells:
#     print(json.dumps(spell.__dict__))
print(json.dumps(spells, cls=EncodeJSON))

