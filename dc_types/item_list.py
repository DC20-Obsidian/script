from typing import Self
from .text_item import TextItem

class ItemList:
    def __init__(self):
        self._items: list[TextItem] = []

    def __iter__(self) -> Self:
        self._current_item: int = 0
        return self

    def __next__(self) -> TextItem:
        self._current_item += 1
        if self._current_item > len(self._items):
            raise StopIteration
        return self._items[self._current_item - 1]

    def append(self, item: TextItem) -> Self:
        self._items.append(item)
        return self
