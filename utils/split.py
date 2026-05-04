from lib.fixup_text import fixup_name
from dc_types.text_frag import TextFrag
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from collections.abc import Callable


def split_items_default(frags: FragList) -> list[DCProtoItem]:
    return split_items(frags, ["f3"], ["f4"], 15, ["f2", "f9", "f1"], ["f4"], ["summontraits"])


def split_items(
    frags: FragList,
    header_fonts: list[str],
    section_fonts: list[str],
    max_header_font_size: float,
    discard_fonts: list[str],
    discard_item_fonts: list[str],
    name_false_positives: list[str],
) -> list[DCProtoItem]:
    return split_items_full(
        frags,
        # Discard
        lambda frag: frag.font in discard_fonts,
        lambda frag: frag.font in discard_item_fonts,
        # Header
        lambda frag: (
            frag.font in header_fonts and frag.font_size <= max_header_font_size
        ),
        lambda frag: frag.font in section_fonts,
        # Name
        lambda name: not any(fp in name.lower() for fp in name_false_positives),
        lambda name: fixup_name(name.lower()).title(),
    )


def split_items_full(
    frags: FragList,
    discard_predicate: Callable[[TextFrag], bool],
    discard_item_predicate: Callable[[TextFrag], bool],
    header_predicate: Callable[[TextFrag], bool],
    section_predicate: Callable[[TextFrag], bool],
    name_predicate: Callable[[str], bool],
    fixup_transform: Callable[[str], str] = lambda s: s,
) -> list[DCProtoItem]:
    items: list[DCProtoItem] = []
    current_item: DCProtoItem = DCProtoItem()
    current_item.page = frags.next_get_page()
    prev_frag: TextFrag = TextFrag.blank()
    current_section: int = -1
    item_name_done: bool = False
    discard_item: bool = False

    for frag in frags:
        if section_predicate(frag) and not section_predicate(prev_frag):
            current_section += 1
        if discard_predicate(frag):
            # Discard Predicate is true discarding
            prev_frag = frag
            continue
        if discard_item_predicate(frag):
            discard_item = True
        if header_predicate(frag):
            discard_item = False
            if item_name_done:
                if current_item.name.strip() != "" and name_predicate(
                    current_item.name
                ):
                    current_item.name = fixup_transform(current_item.name)
                    items.append(current_item)
                # Reset current_item
                current_item = DCProtoItem()
                current_item.page = frag.page
                current_item.section = current_section
                item_name_done = False
            current_item.name += frag.text
        else:
            if not discard_item:
                # End of the header, the items's name is done
                item_name_done = True
                current_item.frags.append(frag)
        prev_frag = frag

    current_item.name = fixup_transform(current_item.name)
    items.append(current_item)
    return items
