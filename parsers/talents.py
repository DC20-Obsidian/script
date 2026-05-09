from typing import Optional
from lib.fixup_text import fixup_description
import re
from lib.utils import eprint
from utils.colors import colors
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from dc_types.text_frag import TextFrag
from dc_types.talent import Talent


def parse_talent(proto: DCProtoItem) -> Talent:
    talent: Talent = Talent()
    talent.name = proto.name
    talent.page = proto.page
    frags: FragList = proto.frags

    classes: list[Optional[str]] = [
        "general",
        "Barbarian",
        "Bard",
        "Champion",
        "Cleric",
        "Commander",
        "Druid",
        "Hunter",
        "Monk",
        "Rogue",
        "Sorcerer",
        "Spellblade",
        "Warlock",
        "Wizard",
        "multicalss",
    ]
    section: int = max(proto.section - 2, 0)
    talent.class_name = classes[section]

    metadata: str = frags.cat_while(lambda frag, _: frag.font in ["f26"])
    parse_metadata(talent, metadata)

    talent.description = fixup_description(frags.markup_while(lambda _: True).strip())
    return talent


def parse_metadata(talent: Talent, metadata: str):

    metadata = re.sub("Multiclass Talent", "", metadata)

    repeatable_regex: str = "You can only gain this Talent once.?"
    if re.search(repeatable_regex, metadata):
        metadata = re.sub(repeatable_regex, "", metadata)
        talent.repeatable = False

    repeatable_regex: str = "You can take this Talent multiple times.?"
    if re.search(repeatable_regex, metadata):
        metadata = re.sub(repeatable_regex, "", metadata)
        talent.repeatable = True

    require_regex: str = r"Requirements?: ?"
    level_regex: str = r",? ?Level ?([0-9])+"
    if re.search(require_regex, metadata):
        metadata = re.sub(require_regex, "", metadata)
        # Extract level before processing other requirements
        if re.search(level_regex, metadata):
            level = re.search(level_regex, metadata)
            metadata = re.sub(level_regex, "", metadata)
            assert level
            talent.level = int(level.group(1))
        talent.requires = list(map(lambda s: s.removesuffix("Feature").strip(), metadata.split(",")))
        if not talent.requires[0]:
            talent.requires.pop()

    if talent.name == "Internal Damage":
        talent.requires = []

