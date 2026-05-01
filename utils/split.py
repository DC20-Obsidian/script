from lib.fixup_text import fixup_name
from dc_types.text_frag import TextFrag
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList
from collections.abc import Callable


def split_items_default(frags: FragList) -> list[DCProtoItem]:
    return split_items(frags, ["f3"], ["f2", "f9", "f1"], ["summontraits"])


def split_items(
    frags: FragList,
    header_fonts: list[str],
    discard_fonts: list[str],
    name_false_positives: list[str],
) -> list[DCProtoItem]:
    return split_items_full(
        frags,
        # Header
        lambda frag: frag.font in header_fonts,
        lambda frag: frag.font in discard_fonts,
        lambda name: not any(fp in name.lower() for fp in name_false_positives),
        lambda name: fixup_name(name.lower()).title(),
    )


def split_items_full(
    frags: FragList,
    header_predicate: Callable[[TextFrag], bool],
    discard_predicate: Callable[[TextFrag], bool],
    name_predicate: Callable[[str], bool],
    fixup_transform: Callable[[str], str] = lambda s: s,
) -> list[DCProtoItem]:
    items: list[DCProtoItem] = []
    current_item: DCProtoItem = DCProtoItem()
    item_name_done: bool = False

    for frag in frags:
        if discard_predicate(frag):
            # Discard Predicate is true discarding
            continue
        if header_predicate(frag):
            if item_name_done:
                if current_item.name.strip() != "" and name_predicate(
                    current_item.name
                ):
                    current_item.name = fixup_transform(current_item.name)
                    items.append(current_item)
                # Reset current_item
                current_item = DCProtoItem()
                item_name_done = False
            current_item.name += frag.text
        else:
            # End of the header, the items's name is done
            item_name_done = True
            current_item.frags.append(frag)

    current_item.name = fixup_transform(current_item.name)
    items.append(current_item)
    return items
