#!/usr/bin/env python

import json

from lib.utils import eprint, get_file_paths, flatten_pages
from utils.colors import colors
from utils.args import Args
from lib.markup import markup, assert_font, MarkupStyle
from lib.fixup_text import fixup_name, fixup_description
from dc_types import DCObjEncoder
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from dc_types.spell import Spell
from dc_types.enhancement import Enhancement
from dc_types.frag_list import FragList

def main(args: Args) -> list[Spell] | list[DCProtoItem]:
    if args.all:
        page_range = slice(70, 145)
    else:
        page_range = args.page_range

    # Open file
    file = args.file or get_file_paths()['input']
    with open(file, 'r') as file:
        pages: list[dict] = json.load(file)
        pages: list[dict] = pages[page_range] # Filter pages

    frags: FragList = flatten_pages(pages)
    # Split spells
    spells_raw: list[DCProtoItem] = split_spells(frags)

    if args.raw:
        if args.unprocessed:
            # Consume all TextFrags that can be processed
            parse_spells(spells_raw)
        return spells_raw
    else:
        spells: list[Spell] = parse_spells(spells_raw)
        return spells

def split_spells(frags: FragList) -> list[DCProtoItem]:
    spells: list[DCProtoItem] = []
    current_spell: DCProtoItem = DCProtoItem()
    false_positives = ["summontraits"]
    # f2: page numbers, f9, f1: footers
    discard_fonts: list[str] = ["f2", "f9", "f1"]
    spell_has_name: bool = False

    for frag in frags:
        # f3: heading font
        if frag.font == "f3":
            if spell_has_name:
                # New Spell; commit and initialise a new one
                if current_spell.name.strip() != "" and not any(fp in current_spell.name.lower() for fp in false_positives):
                    current_spell.name = fixup_name(current_spell.name.lower()).title()
                    spells.append(current_spell)
                current_spell = DCProtoItem()
                spell_has_name = False
            current_spell.name += frag.text
        else:
            spell_has_name = True
            if frag.font not in discard_fonts:
                current_spell.frags.append(frag)

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
    frags: list[TextFrag] = proto_spell.frags

    # Pop: 'Source:':f11:2, 'Source':f7:155, 'Spell List':f7:3
    frag = frags.pop(0)
    spell.page = frag.page
    assert_font(frag, ["f7", "f11"])
    # return spell

    # Spell Source
    frag: TextFrag = frags.pop(0)
    assert_font(frag, ["f5"])
    while frag.font == "f5":
        spell.source.extend(re.findall(r'[a-zA-Z]+', frag.text))
        frag = frags.pop(0)
    # return spell

    # Pop: 'School':f7:148, 'School:':f14:1 'Spell School':f7:11
    assert_font(frag, ["f7", "f14"])

    # Spell School
    frag: TextFrag = frags.pop(0)
    assert_font(frag, ["f5"])
    school: list[str] = re.findall(r'^:? ?([a-zA-Z ]+)', frag.text)
    assert len(school) == 1
    spell.school = school[0].strip()
    # return spell

    # Pop: 'Tags':f21: 158, 'Tags:':f11:1 'Spell Tags':f21:1
    assert_font(frags.pop(0), ["f21", "f11"])
    # return spell

    # Spell Tags
    frag: TextFrag = frags.pop(0)
    assert_font(frag, ["f5"])
    while frag.font == "f5":
        spell.tags.extend(re.findall(r'[a-zA-Z]+', frag.text))
        frag = frags.pop(0)
    # return spell

    # Pop: 'Cost':f7: 159, 'Cost':f11:1
    assert_font(frag, ["f7", "f11"])

    # Spell Cost
    frag: TextFrag = frags.pop(0)
    assert_font(frag, ["f5"])
    while frag.font == "f5":
        spell.cost += frag.text.lstrip(':').strip()
        frag = frags.pop(0)
    # return spell

    # Pop: 'Range':f21: 160
    assert_font(frag, ["f21"])

    # Spell Range
    frag: TextFrag = frags.pop(0)
    assert_font(frag, ["f5"])
    spell.range = frag.text.lstrip(':').strip()
    # No loop here because "Dispel Magic" has no listed duration
    # return spell

    frag: TextFrag = frags[0]
    if re.match('^Duration', frag.text) is not None:
        # Spell is not "Dispel Magic"
        frags.pop(0)
        assert_font(frag, ["f21"])

        frag: TextFrag = frags.pop(0)
        assert_font(frag, ["f5"])
        spell.duration = frag.text.lstrip(':').strip()
    else:
        # Spell is "Dispel Magic". Filling in Duration
        spell.duration = "Instantaneous"
    # return spell

    spell.description = parse_description(frags)

    enhancements = split_enhancements(frags)
    # spell.enhancements = split_enhancements(frags) # Debug

    spell.enhancements = list(map(parse_enhancement, enhancements))

    # return spell
    return spell.fixup()

def split_enhancements(frags: list[TextFrag]) -> list[DCProtoItem]:
    enhancements: list[DCProtoItem] = []
    current_enhancement = DCProtoItem()
    prev_frag: TextFrag = frags[0]
    has_name = False
    for frag in frags:
        if frag.font == "f27": # This is for Call Famillar and other spells that have multiple sections
            break
        if frag.font in ["f21", "f7"]:
            if "•" in prev_frag.text: # false positive: skip
                prev_frag = frag
                continue

            if has_name and current_enhancement.name != "":
                current_enhancement.name = current_enhancement.name.strip()
                enhancements.append(current_enhancement)
                current_enhancement = DCProtoItem()

            current_enhancement.name += f'{frag.text.strip(':').lstrip()} '
            has_name = False
        else:
            current_enhancement.frags.append(frag)
            has_name = True

        prev_frag = frag

    current_enhancement.name = current_enhancement.name.strip()
    enhancements.append(current_enhancement)
    return enhancements

def parse_enhancement(proto: DCProtoItem) -> Enhancement:
    enhancement = Enhancement()
    enhancement.name = proto.name
    cost: str = ""

    while ')' not in cost:
        cost += ' ' + proto.frags.pop(0).text
    (cost, _, desc) = cost.partition(')')

    enhancement.description = fixup_description(desc.strip() + ' ' + parse_description(proto.frags))
    enhancement.cost = cost.lstrip(': (')

    return enhancement.fixup()

def parse_description(frags: list[TextFrag]) -> str:
    if len(frags) == 0:
        return ""

    desc: str = ""
    frag: TextFrag = frags.pop(0)
    prev_frag = frag

    # f27: Spell Enhancements
    while frag.font != 'f27' or not frag.text.startswith("Spell Enhancement"):
        desc += markup(frag, prev_frag, MarkupStyle.MARKDOWN)
        prev_frag = frag
        if len(frags) != 0:
            frag = frags.pop(0)
        else:
            break

    # desc += f'\n\033[38;2;25;25;25mx{colors.ENDC}'
    return fixup_description(desc.strip())

def parse_spells(spells_raw: list[DCProtoItem]) -> list[Spell]:
    spells: list[Spell] = []
    for raw_spell in spells_raw:
        page_number = raw_spell.frags[0].page
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

