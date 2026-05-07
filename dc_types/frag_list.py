import re
from typing import Self, Optional
from collections.abc import Callable
from lib.markup import markup, MarkupStyle
from .text_frag import TextFrag


class FragList:
    def __init__(self):
        self._frags: list[TextFrag] = []

    def __iter__(self) -> Self:
        self._current_frag: int = 0
        return self

    def __next__(self) -> TextFrag:
        self._current_frag += 1
        if self._current_frag > len(self._frags):
            raise StopIteration
        return self._frags[self._current_frag - 1]

    @classmethod
    def copy(cls, source: Self) -> Self:
        fl: Self = cls()
        fl._frags = source._frags.copy()
        return fl

    def append(self, frag: TextFrag) -> Self:
        self._frags.append(frag)
        return self

    def extend(self, frags: Self) -> Self:
        self._frags.extend(frags._frags)
        return self

    def is_empty(self) -> bool:
        return len(self._frags) == 0

    def next(self) -> TextFrag:
        return self._frags.pop(0)

    def next_get_page(self) -> int:
        return self._frags[0].page

    def match_next(self, predicate: Callable[[TextFrag], bool]):
        return predicate(self._frags[0])

    def match_next_regex(self, regex: str) -> bool:
        return re.match(regex, self._frags[0].text) is not None

    def find_multi_while(
        self, predicate: Callable[[TextFrag], bool], multi_filter: str,
        min_one: bool = True
    ) -> list[str]:
        li: list[str] = []
        frag: TextFrag = self.next()

        if min_one:
            assert predicate(frag), "predicate is false on the first fragment"

        while predicate(frag):
            li.extend(re.findall(multi_filter, frag.text))
            frag = self.next()

        # predicate() returned false, reinsert fragment
        self._frags.insert(0, frag)
        return li

    def find_words_while_font(self, fonts: list[str]) -> list[str]:
        return self.find_multi_while(lambda i: i.font in fonts, r"[a-zA-Z]+")

    def cat_while(
        self,
        predicate: Callable[[TextFrag, str], bool],
        transform: Callable[[str], str] = lambda s: s,
        min_one: bool = True,
    ) -> str:
        s: str = ""
        frag: TextFrag = self.next()

        if min_one:
            assert predicate(frag, s), "predicate is false on the first fragment"

        while predicate(frag, s):
            s += transform(frag.text)
            if not self.is_empty():
                frag = self.next()
            else:
                return s

        self._frags.insert(0, frag)
        return s

    def cat_until(
        self,
        predicate: Callable[[TextFrag, str], bool],
        transform: Callable[[str], str] = lambda s: s,
    ) -> str:
        return self.cat_while(lambda f, s: not predicate(f, s), transform)

    def markup_while(self, predicate: Callable[[TextFrag], bool], min_one: bool = True) -> str:
        if self.is_empty():
            return ""
        s: str = ""
        frag: Optional[TextFrag] = self.next()
        prev_frag: Optional[TextFrag] = frag
        if min_one:
            assert predicate(frag), "predicate is false on the first fragment"
        while predicate(frag):
            s += markup(frag, prev_frag, MarkupStyle.MARKDOWN)
            prev_frag = frag
            if self.is_empty():
                break
            else:
                frag = self.next()
        else:
            self._frags.insert(0, frag)
        s += markup(None, prev_frag, MarkupStyle.MARKDOWN)
        return s

    def markup_until(self, predicate: Callable[[TextFrag], bool], min_one: bool = True) -> str:
        return self.markup_while(lambda f: not predicate(f), min_one)

    def assert_frag(self, f: Callable[[TextFrag], bool], msg: Optional[str] = None):
        frag = self.next()
        if not f(frag):
            raise Exception(msg or "TextFrag Assertion Failed")

    def discard_next(self):
        self.next()

    def discard_with_font(self, fonts: list[str]):
        frag: TextFrag = self.next()
        assert frag.font in fonts, (
            f"Invalid font on page: {frag.page}. Expected one of: {fonts}, found: {frag.font}"
        )

    def discard_until(self, predicate: Callable[[TextFrag], bool]) -> int:
        frag = self.next()
        count = 0

        while not predicate(frag):
            count += 1
            frag = self.next()

        self._frags.insert(0, frag)
        return count

    def discard_while(self, predicate: Callable[[TextFrag], bool]) -> int:
        return self.discard_until(lambda f: not predicate(f))
