from dataclasses import dataclass, field
from typing import Any, Union
from utils.debug import eprint
from collections.abc import Callable
from utils.fixup_text import fixup_name
from dc_types.text_frag import TextFrag
from dc_types.proto_item import DCProtoItem
from dc_types.frag_list import FragList


def split_items_default(frags: FragList, type: str) -> list[DCProtoItem]:
    return split_items(
        frags, ["f3"], ["f4"], 15, ["f2", "f9", "f1"], ["f4"], ["summontraits"], type
    )


def split_items(
    frags: FragList,
    header_fonts: list[str],
    section_fonts: list[str],
    max_header_font_size: float,
    discard_fonts: list[str],
    discard_item_fonts: list[str],
    name_false_positives: list[str],
    type: str,
) -> list[DCProtoItem]:
    prams: SplitPrams = SplitBuilder(
        is_header=(header_fonts, max_header_font_size),
        is_section=section_fonts,
        discard_frag=discard_fonts,
        discard_from_frag=discard_item_fonts,
        discard_item=name_false_positives,
    ).build()
    return split_items_full(
        frags,
        prams,
        type,
    )

class SplitPrams:
    def __init__(self, is_header: Callable[[str, TextFrag], bool]):
        # Discard from here to next header
        self.discard_from_frag: Callable[[TextFrag], bool] = _false

        self.is_header: Callable[[str, TextFrag], bool] = is_header

        # False positive header, Append it's contents to prev item
        self.cont_item: Callable[[str], bool] = _false

        # False positive header, Discard
        self.discard_item: Callable[[str], bool] = _false

        # Ignore frag completely
        self.discard_frag: Callable[[TextFrag], bool] = _false

        # Increment section counter
        self.is_section: Callable[[TextFrag], bool] = _false

def split_items_full(
    frags: FragList,
    prams: SplitPrams,
    type: str,
    fixup_transform: Callable[[str, str], str] = fixup_name,
) -> list[DCProtoItem]:
    items: list[DCProtoItem] = []
    current_item: DCProtoItem = DCProtoItem()
    current_item.page = frags.next_get_page()
    prev_frag: TextFrag = TextFrag.blank()
    current_section: int = -1
    item_name_done: bool = False
    discard_item: bool = False

    for frag in frags:
        if prams.is_section(frag) and not prams.is_section(prev_frag):
            current_section += 1

        if prams.discard_frag(frag):
            prev_frag = frag
            continue

        item_name: str = "" if item_name_done else current_item.name.strip().lower()
        # Discard fragments from here to next header
        if prams.discard_from_frag(frag) and not prams.is_header(item_name, frag):
            discard_item = True

        if prams.is_header(item_name, frag):
            discard_item = False
            if item_name_done:
                finish_item(current_item, items, prams, type, fixup_transform)
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

    finish_item(current_item, items, prams, type, fixup_transform)
    return items

def finish_item(item: DCProtoItem, items: list[DCProtoItem], prams: SplitPrams, type: str, fixup: Callable[[str, str], str]):
    item.name = item.name.strip().lower()
    if not item.name:
        # Discard Items with empty names
        # This should only happen for the first (blank) item
        return

    if prams.discard_item(item.name):
        return

    if prams.cont_item(item.name):
        prev_item: DCProtoItem = items[-1]
        name_frag: TextFrag = TextFrag.blank()
        name_frag.text = fixup(item.name, type)
        name_frag.page = item.page
        name_frag.font = "<cont item>"
        prev_item.frags.append(name_frag)
        prev_item.frags.extend(item.frags)
        return

    # else Add Item
    item.name = fixup(item.name, type)
    items.append(item)



def _false(*_args) -> bool:
    return False

def _empty_list():
    return field(default_factory=lambda: [])


@dataclass(kw_only=True)
class SplitBuilder:
    discard_from_frag: Union[Callable[[TextFrag], bool], list[str]] = _empty_list()
    is_header: Union[Callable[[str, TextFrag], bool], list[str], tuple[list[str], float]]
    cont_item: Union[Callable[[str], bool], list[str]] = _empty_list()
    discard_item: Union[Callable[[str], bool], list[str]] = _empty_list()
    discard_frag: Union[Callable[[TextFrag], bool], list[str]] = field(default_factory=lambda: ["f2", "f9", "f1"])
    is_section: Union[Callable[[TextFrag], bool], list[str]] = _empty_list()

    def build(self) -> SplitPrams:
        prams: SplitPrams = SplitPrams(_is_header(self.is_header))
        prams.discard_from_frag = _frag_list(self.discard_from_frag)
        prams.cont_item = _name_list(self.cont_item)
        prams.discard_item = _name_list(self.discard_item)
        prams.discard_frag = _frag_list(self.discard_frag)
        prams.is_section = _frag_list(self.is_section)
        return prams


def _frag_list(x: Union[Callable[[TextFrag], bool], list[str], tuple[list[str], float]]) -> Callable[[TextFrag], bool]:
    def f(frag: TextFrag, li, size) -> bool:
        return frag.font in li and frag.font_size <= size
    if isinstance(x, list):
        return lambda frag: frag.font in x
    if isinstance(x, tuple):
        li = x[0]
        assert isinstance(li, list)
        size = x[1]
        assert isinstance(size, float) or isinstance(size, int)
        return lambda frag: f(frag, li, size)
    return x

def _is_header(x: Union[Callable[[str, TextFrag], bool], list[str], tuple[list[str], float]]) -> Callable[[str, TextFrag], bool]:
    def f(frag: TextFrag, li, size) -> bool:
        return frag.font in li and frag.font_size <= size
    if isinstance(x, list):
        return lambda _, frag: frag.font in x
    if isinstance(x, tuple):
        li = x[0]
        assert isinstance(li, list)
        size = x[1]
        assert isinstance(size, float) or isinstance(size, int)
        return lambda _, frag: f(frag, li, size)
    return x

def _name_list(x: Union[Callable[[str], bool], list[str]]) -> Callable[[str], bool]:
    if isinstance(x, list):
        return lambda name: name in x
    return x
