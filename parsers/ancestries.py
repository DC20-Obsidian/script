# from lib.utils import eprint
# from utils.colors import colors
from lib.markup import assert_font
from lib.fixup_text import fixup_description
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from dc_types.frag_list import FragList
from dc_types.ancestry import Ancestry, Trait


def parse_ancestry(proto: DCProtoItem) -> Ancestry:
    ancestry = Ancestry()
    ancestry.name = proto.name
    frags: FragList = proto.frags
    ancestry.page = proto.page

    traits = split_traits(frags)

    ancestry.traits = list(map(parse_enhancement, traits))

    return ancestry.fixup()


def split_traits(frags: FragList) -> list[DCProtoItem]:  # TODO use split_items()
    traits: list[DCProtoItem] = []
    return traits


def parse_enhancement(proto: DCProtoItem) -> Trait:
    trait: Trait = Trait()
    trait.name = proto.name
    trait.page = proto.page

    return trait.fixup()

