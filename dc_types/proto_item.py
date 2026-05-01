from .text_frag import TextFrag
from .frag_list import FragList


class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.page: int = -1
        self.frags: FragList = FragList()
        # self.frags: list[TextFrag] = []
        self.section: int = -1
