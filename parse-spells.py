#!/usr/bin/env python

import json

page = 112
page_range = range(68, 115)

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
    print(f"-----name-----> {name}")
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
                print("ffo")
                name = extract_spell_name(text_items, i)
                current_spell.name = name
                current_item = 'source'
                spells.append(current_spell)
                current_spell = Spell()
    # print(text, end="---")
    # print(text_items[i]['fontName'])
    print(text)
    i += 1

for spell in spells:
    print(json.dumps(spell.__dict__))

