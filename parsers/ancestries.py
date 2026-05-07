import re
from lib.utils import eprint
from utils.colors import colors
from lib.markup import assert_font
from lib.fixup_text import fixup_description
from utils.split import split_items_full, SplitPrams, SplitBuilder
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from dc_types.frag_list import FragList
from dc_types.ancestry import Ancestry, Trait


def parse_ancestry(proto: DCProtoItem) -> Ancestry:
    ancestry = Ancestry()
    ancestry.name = proto.name
    frags: FragList = proto.frags
    ancestry.page = proto.page

    eprint(proto.name)

    def is_header(frag: TextFrag) -> bool:
        return frag.font in ["f3", "<cont item>"]

    desc: str = frags.markup_until(is_header, min_one=False)
    frags.discard_while(is_header)
    frags.discard_until(lambda f: f.font in ["f14", "f11", "f3"])

    ancestry.description = desc

    traits = split_traits(frags)

    # ancestry.traits = traits

    ancestry.traits = list(map(lambda t: parse_trait(t, ancestry.name), traits))

    return ancestry.fixup()


def split_traits(frags: FragList) -> list[DCProtoItem]:
    prams: SplitPrams = SplitBuilder(
        is_header=match_trait_header,
        is_section=["f3"],
        discard_from_frag=["f3"],
    ).build()
    traits: list[DCProtoItem] = split_items_full(frags, prams)
    return traits


def match_trait_header(name: str, frag: TextFrag) -> bool:
    is_font = frag.font in ["f14", "f11"]
    is_name: bool = frag.text.startswith("(") or name.startswith("(")
    # if is_font or name:
    #     pass
    #     eprint(f"\"{colors.BLUE}{name}{colors.ENDC}\" - \"{colors.GREEN}{frag.font}{colors.ENDC}\" - \"{colors.CYAN}{frag.text}{colors.ENDC}\"")
    return is_font and is_name


def parse_trait(proto: DCProtoItem, ancestry_name: str) -> Trait:
    trait: Trait = Trait()
    (cost, _, name) = proto.name.partition(")")
    (name, _, depends) = name.partition("(")
    trait.name = name.rstrip(":").strip()
    trait.cost = int(cost.lstrip("("))
    trait.page = proto.page
    trait.ancestry = ancestry_name

    depends_regex: str = r"\([rR]equires ([a-zA-Z -]+)\)"
    if proto.frags.match_next_regex(depends_regex):
        frag: TextFrag = proto.frags.next()
        depends = re.match(depends_regex, frag.text)
        depends = depends.group(1) if depends else "<ERROR>"
        trait.description += re.sub(depends_regex, "", frag.text).strip()
        trait.description += " "

    trait.dependent_on = depends.rstrip("):") or None

    sections_normal: list[str] = ["default", "extended"]
    sections_beast_born: list[str] = [
        "Senses",
        "Mobility",
        "Jumping",
        "Flying",
        "Body",
        "Natral Weapons",
        "Miscellaneous",
    ]

    if ancestry_name == "Beastborn":
        trait.kind = sections_beast_born[proto.section]
        if proto.section == 5:
            trait.dependent_on = "Natral Weapon"
    else:
        trait.kind = sections_normal[proto.section + 1]
        trait.default = proto.section == -1
    trait.description += fixup_description(proto.frags.markup_while(lambda _: True))

    return trait.fixup()
