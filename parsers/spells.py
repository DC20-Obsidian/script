# from lib.utils import eprint
# from utils.colors import colors
from lib.markup import assert_font
from lib.fixup_text import fixup_description
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from dc_types.spell import Spell
from dc_types.enhancement import Enhancement
from dc_types.frag_list import FragList


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
    spell = Spell()
    spell.name = proto_spell.name
    frags: FragList = proto_spell.frags

    # Pop: 'Source:':f11:2, 'Source':f7:155, 'Spell List':f7:3
    spell.page = frags.next_get_page()
    frags.discard_with_font(["f7", "f11"])
    # return spell

    # Spell Source
    sources: list[str] = frags.find_words_while_font(["f5"])
    spell.source = sources
    # return spell

    # Pop: 'School':f7:148, 'School:':f14:1 'Spell School':f7:11
    frags.discard_with_font(["f7", "f14"])

    # Spell School
    school: list[str] = frags.find_words_while_font(["f5"])
    assert len(school) == 1
    spell.school = school[0].strip()
    # return spell

    # Pop: 'Tags':f21: 158, 'Tags:':f11:1 'Spell Tags':f21:1
    frags.discard_with_font(["f21", "f11"])
    # return spell

    # Spell Tags
    tags: list[str] = frags.find_words_while_font(["f5"])
    assert 0 < len(tags) < 10
    spell.tags = tags
    # return spell

    # Pop: 'Cost':f7: 159, 'Cost':f11:1
    frags.discard_with_font(["f7", "f11"])

    # Spell Cost
    cost: str = frags.cat_while(
        lambda frag, _: frag.font in ["f5"], lambda s: s.lstrip(":").strip()
    )
    spell.cost = cost
    # return spell

    # Pop: 'Range':f21: 160
    frags.discard_with_font(["f21"])

    # Spell Range
    frag: TextFrag = frags.next()
    assert_font(frag, ["f5"])
    spell.range = frag.text.lstrip(":").strip()
    # No loop here because "Dispel Magic" has no listed duration
    # return spell

    if frags.match_next_regex("^Duration"):
        # Spell is not "Dispel Magic"
        frags.discard_with_font(["f21"])

        frag: TextFrag = frags.next()
        assert_font(frag, ["f5"])
        spell.duration = frag.text.lstrip(":").strip()
    else:
        # Spell is "Dispel Magic". Filling in Duration
        spell.duration = "Instantaneous"
    # return spell

    spell.description = fixup_description(parse_description(frags))
    frags.discard_with_font(["f27"])

    enhancements = split_enhancements(frags)
    # spell.enhancements = split_enhancements(frags) # Debug
    # return spell

    spell.enhancements = list(map(parse_enhancement, enhancements))

    # return spell
    return spell.fixup()


def split_enhancements(frags: FragList) -> list[DCProtoItem]:  # TODO use split_items()
    enhancements: list[DCProtoItem] = []
    current_enhancement = DCProtoItem()
    prev_frag: TextFrag = frags._frags[0]
    has_name = False
    for frag in frags:
        if (
            frag.font == "f27"
        ):  # This is for Call Famillar and other spells that have multiple sections
            break
        if frag.font in ["f21", "f7"]:
            if "•" in prev_frag.text:  # false positive: skip
                prev_frag = frag
                continue

            if has_name and current_enhancement.name != "":
                current_enhancement.name = current_enhancement.name.strip()
                enhancements.append(current_enhancement)
                current_enhancement = DCProtoItem()

            current_enhancement.name += f"{frag.text.strip(':').lstrip()} "
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
    cost: str = proto.frags.cat_while(lambda _, s: ")" not in s, lambda s: f" {s}")
    (cost, _, desc) = cost.partition(")")

    enhancement.description = fixup_description(
        desc.strip() + " " + parse_description(proto.frags)
    )
    enhancement.cost = cost.lstrip(": (")

    return enhancement.fixup()


def parse_description(frags: FragList) -> str:
    # f27: Spell Enhancements
    desc: str = frags.markup_while(
        lambda frag: frag.font != "f27" or not frag.text.startswith("Spell Enhancement")
    )
    # desc += f'\n\033[38;2;25;25;25mx{colors.ENDC}'
    return desc.strip()
