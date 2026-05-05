from collections.abc import Callable
from lib.utils import eprint
from utils.colors import colors
from .item import Item
from .frag_list import FragList


class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.page: int = -1
        self.frags: FragList = FragList()
        # self.frags: list[TextFrag] = []
        self.section: int = -1


def parse_proto_items(
    proto_items: list[DCProtoItem], transform: Callable[[DCProtoItem], Item]
) -> list[Item]:
    items: list[Item] = []
    for proto_item in proto_items:
        try:
            page_number = proto_item.frags.next_get_page()
        except Exception as e:
            eprint(proto_item.__dict__)
            raise e
        try:
            items.append(transform(proto_item))
        except Exception as e:
            eprint(
                f"{colors.RED}Error{colors.ENDC} with item {colors.GREEN}{proto_item.name}{colors.ENDC}, starts on page: {colors.BLUE}{page_number}{colors.ENDC}"
            )
            raise e
            # continue

    return items
