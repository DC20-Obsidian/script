#!/usr/bin/env python

import json

from lib.utils import colors, eprint, Args, get_file_path
from lib.dc_types import Spell, Enhancement, DCObjEncoder, TextItem, DCProtoItem, markup, assert_font, MarkupStyle
from lib.fixup_text import fixup_name

def main(args: Args) -> list[Spell] | list[DCProtoItem]:
    if args.all:
        page_range = slice(70, 145)
    else:
        page_range = args.page_range

    # Open file
    file = get_file_path()[1]
    file = args.file or f'{file}/json/dc20_0.10.5_pdf_filtered.json'
    with open(file, 'r') as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range] # Filter pages

    # Split spells
    spells_raw: list[DCProtoItem] = split_spells(pages)

    if args.raw:
        if args.unprocessed:
            # Consume all TextItems that can be processed
            spells: list[Spell] = parse_spells(spells_raw)
        return spells_raw
    else:
        spells: list[Spell] = parse_spells(spells_raw)
        return spells

def split_spells(pages: list[dict]) -> list[DCProtoItem]:
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
                    # New Spell; commit and initialise a new one
                    if current_spell.name.strip() != "" and not any(fp in current_spell.name.lower() for fp in false_positives):
                        current_spell.name = fixup_name(current_spell.name.lower()).title()
                        spells.append(current_spell)
                    current_spell = DCProtoItem()
                    spell_has_name = False
                current_spell.name += item.text
            else:
                spell_has_name = True
                if item.font not in discard_fonts:
                    current_spell.items.append(item)

    current_spell.name = fixup_name(current_spell.name.lower()).title()
    spells.append(current_spell)
    return spells

def parse_spell(proto_spell: DCProtoItem) -> Spell:
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
    # return spell

    # Spell Source
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.source.extend(re.findall(r'[a-zA-Z]+', item.text))
        item = items.pop(0)
    # return spell

    # Pop: 'School':f7:148, 'School:':f14:1 'Spell School':f7:11
    assert_font(item, ["g_d0_f7", "g_d0_f14"])

    # Spell School
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    school: list[str] = re.findall(r'^:? ?([a-zA-Z ]+)', item.text)
    assert len(school) == 1
    spell.school = school[0].strip()
    # return spell

    # Pop: 'Tags':f21: 158, 'Tags:':f11:1 'Spell Tags':f21:1
    assert_font(items.pop(0), ["g_d0_f21", "g_d0_f11"])
    # return spell

    # Spell Tags
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.tags.extend(re.findall(r'[a-zA-Z]+', item.text))
        item = items.pop(0)
    # return spell

    # Pop: 'Cost':f7: 159, 'Cost':f11:1
    assert_font(item, ["g_d0_f7", "g_d0_f11"])

    # Spell Cost
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    while item.font == "g_d0_f5":
        spell.cost += item.text.lstrip(':').strip()
        item = items.pop(0)
    # return spell

    # Pop: 'Range':f21: 160
    assert_font(item, ["g_d0_f21"])

    # Spell Range
    item: TextItem = items.pop(0)
    assert_font(item, ["g_d0_f5"])
    spell.range = item.text.lstrip(':').strip()
    # No loop here because "Dispel Magic" has no listed duration
    # return spell

    item: TextItem = items[0]
    if re.match('^Duration', item.text) is not None:
        # Spell is not "Dispel Magic"
        items.pop(0)
        assert_font(item, ["g_d0_f21"])

        item: TextItem = items.pop(0)
        assert_font(item, ["g_d0_f5"])
        spell.duration = item.text.lstrip(':').strip()
    else:
        # Spell is "Dispel Magic". Filling in Duration
        spell.duration = "Instantaneous"
    # return spell

    spell.description = parse_description(items)

    enhancements = split_enhancements(items)
    # spell.enhancements = split_enhancements(items) # Debug

    spell.enhancements = list(map(parse_enhancement, enhancements))

    # return spell
    return spell.fixup()

def split_enhancements(items: list[TextItem]) -> list[DCProtoItem]:
    enhancements: list[DCProtoItem] = []
    current_enhancement = DCProtoItem()
    prev_item: TextItem = items[0]
    has_name = False
    for item in items:
        if item.font == "g_d0_f27": # This is for Call Famillar and other spells that have multiple sections
            break
        if item.font in ["g_d0_f21", "g_d0_f7"]:
            if "•" in prev_item.text: # false positive: skip
                prev_item = item
                continue

            if has_name and current_enhancement.name != "":
                current_enhancement.name = current_enhancement.name.strip()
                enhancements.append(current_enhancement)
                current_enhancement = DCProtoItem()

            current_enhancement.name += f'{item.text.strip(':').lstrip()} '
            has_name = False
        else:
            current_enhancement.items.append(item)
            has_name = True

        prev_item = item

    current_enhancement.name = current_enhancement.name.strip()
    enhancements.append(current_enhancement)
    return enhancements

def parse_enhancement(proto: DCProtoItem) -> Enhancement:
    enhancement = Enhancement()
    enhancement.name = proto.name
    cost: str = ""

    while ')' not in cost:
        cost += ' ' + proto.items.pop(0).text
    (cost, _, desc) = cost.partition(')')

    enhancement.description = desc.strip() + ' ' + parse_description(proto.items)
    enhancement.cost = cost.lstrip(': (')

    return enhancement.fixup()

def parse_description(items: list[TextItem]) -> str:
    if len(items) == 0:
        return ""

    desc: str = ""
    item: TextItem = items.pop(0)
    prev_item = item

    # f27: Spell Enhancements
    while item.font != 'g_d0_f27' or not item.text.startswith("Spell Enhancement"):
        desc += markup(item, prev_item, MarkupStyle.MARKDOWN)
        prev_item = item
        if len(items) != 0:
            item = items.pop(0)
        else:
            break

    # desc += f'\n\033[38;2;25;25;25mx{colors.ENDC}'
    return desc.strip()

def parse_spells(spells_raw) -> list[Spell]:
    spells: list[Spell] = []
    for raw_spell in spells_raw:
        page_number = raw_spell.items[0].page
        try:
            spells.append(parse_spell(raw_spell))
        except Exception as e:
            eprint(f"{colors.RED}Error{colors.ENDC} with spell {colors.GREEN}{raw_spell.name}{colors.ENDC}, starts on page: {colors.BLUE}{page_number}{colors.ENDC}")
            raise e

            continue
    return spells

if __name__ == "__main__":
    args = Args(default_page=71)

    if args.type != "spells" and args.type:
        raise Exception("Parsing spells, but type is not spells")

    if args.write:
        raise Exception("args.write is set, but this function doesn't support that. Use a different one.")

    spells: list = main(args)

    if args.print:
        print(json.dumps(spells, cls=DCObjEncoder))
    else:
        eprint(f"{colors.YELLOW}Warning{colors.ENDC}: parse_spells called, but args.print is not set. Skipping")

