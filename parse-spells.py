#!/usr/bin/env python

import json

from utils import colors, eprint, Args, assert_font
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
    spells_raw: list[DCProtoItem] = split_spells(pages)

    spells: list[Spell] = parse_spells(spells_raw)

    if args.raw:
        print(json.dumps(spells_raw, cls=DCObjEncoder))
    else:
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

def parse_spell(proto_spell: DCProtoItem):
    """
        Pop Format: '<string or regex>':<font>:count
        Fonts:
            f5:  normat text
            f21, f7: bold, italic
            f11, f14: bold
            f3: headings
            f27: subheading
    """
    import re
    spell = Spell()
    spell.name = proto_spell.name
    items: list[TextItem] = proto_spell.items

    # Pop: 'Source:':f11:2, 'Source':f7:155, 'Spell List':f7:3
    item = items.pop(0)
    spell.page_number = item.page
    assert_font(item, ["g_d0_f7", "g_d0_f11"])

    # Spell Source
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.source.extend(re.findall(r'[a-zA-Z]+', item.text))
        item = items.pop(0)

    # Pop: 'School':f7:148, 'School:':f14:1 'Spell School':f7:11
    assert_font(item, ["g_d0_f7", "g_d0_f14"])

    # Spell School
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    school: list[str] = re.findall(r'^:? ?([a-zA-Z ]+)', item.text)
    assert len(school) == 1
    spell.school = school[0].strip()

    # Pop: 'Tags':f21: 158, 'Tags:':f11:1 'Spell Tags':f21:1
    assert_font(items.pop(0), ["g_d0_f21", "g_d0_f11"])

    # Spell Tags
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.tags.extend(re.findall(r'[a-zA-Z]+', item.text))
        item = items.pop(0)

    # Pop: 'Cost':f7: 159, 'Cost':f11:1
    assert_font(item, ["g_d0_f7", "g_d0_f11"])

    # Spell Cost
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.cost += item.text.lstrip(':').strip()
        item = items.pop(0)

    # Pop: 'Range':f21: 160
    assert_font(item, ["g_d0_f21"])

    # Spell Range
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    spell.range = item.text.lstrip(':').strip()
    # No loop here because "Dispel Magic" has no listed duration

    item: TextItem = items.pop(0)
    if re.match('^Duration', item.text) is not None:
        # Spell is not "Dispel Magic"
        assert_font(item, ["g_d0_f21"])

        item: TextItem = items.pop(0)
        assert_font(item, ["g_d0_f5"])
        spell.duration = item.text.lstrip(':').strip()
    else:
        # Spell is "Dispel Magic". Filling in Duration
        spell.duration = "Instantaneous"
        items.insert(0, item)

    return spell

def parse_spells(spells_raw):
    spells: list[Spell] = []
    for raw_spell in spells_raw:
        page_number = raw_spell.items[0].page
        try:
            spells.append(parse_spell(raw_spell))
        except Exception as e:
            eprint(f"{colors.RED}Error{colors.ENDC} with spell {raw_spell.name}, starts on page: {page_number}")
            eprint(e)
            break
    return spells

if __name__ == "__main__":
    main()

