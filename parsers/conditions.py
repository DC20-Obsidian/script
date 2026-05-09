# from lib.utils import eprint
# from utils.colors import colors
from lib.fixup_text import fixup_name, fixup_description
from dc_types.proto_item import DCProtoItem
from dc_types.condition import Condition
from dc_types.frag_list import FragList


def parse_condition(proto_cond: DCProtoItem) -> Condition:
    cond = Condition()
    cond.name = proto_cond.name.replace(" ", "")
    if cond.name.endswith("X"):
        cond.stacking = True
        cond.name = cond.name.rstrip(" X")
    cond.page = proto_cond.frags.next_get_page()
    frags: FragList = proto_cond.frags

    desc: str = frags.markup_while(lambda _: True)

    cond.description = fixup_description(desc)
    return cond
