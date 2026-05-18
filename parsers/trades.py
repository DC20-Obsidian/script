import re

from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from dc_types.trade import Trade
from utils.fixup_text import fixup_description


def parse_trade(proto: DCProtoItem) -> Trade:
    trade = Trade()
    trade.name = proto.name
    trade.page = proto.page
    frags = proto.frags

    sections = ["Artistry", "Crafting", "Knowledge", "Services", "Subterfuge"]
    trade.type = sections[max(0, proto.section)]

    tool_regex: str = "^Tool: |^Requires: "
    if frags.match_next_regex(r"^Tool:|Requires:"):
        tool = frags.next()
        trade.tool = re.sub(tool_regex, "", tool.text)
        if trade.tool.lower() == "none":
            trade.tool = None

    attr_regex: str = "Attribute: "
    assert frags.match_next_regex(attr_regex)
    attr: list[str] = re.sub(
        r",? or |, ?", "\n", re.sub(attr_regex, "", frags.next().text)
    ).splitlines()

    trade.attributes = attr

    category_fonts: list[str] = ["f7", "f21"]

    def frag_text(frag: TextFrag) -> str:
        return frag.text

    categories: list[str] = list(
        map(frag_text, filter(lambda f: f.font in category_fonts, frags._frags))
    )
    trade.categories = categories

    description = fixup_description(frags.markup_while(lambda _: True))
    trade.description = re.sub(r" \*\*\*", "\n- ***", description)

    return trade
