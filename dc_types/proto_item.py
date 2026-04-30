
from .text_item import TextItem

class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.page: int = -1
        # self.items: ItemList = ItemList()
        self.items: list[TextItem] = []
        self.section: str = ""
