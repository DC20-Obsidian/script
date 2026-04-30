
from .text_frag import TextFrag

class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.page: int = -1
        # self.frags: FragList = FragList()
        self.frags: list[TextFrag] = []
        self.section: str = ""
