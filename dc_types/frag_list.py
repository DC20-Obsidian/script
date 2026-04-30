from typing import Self
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

    def append(self, frag: TextFrag) -> Self:
        self._frags.append(frag)
        return self
