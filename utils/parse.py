from collections.abc import Callable

from dc_types.item import Item
from dc_types.proto_item import DCProtoItem
from utils.colors import colors
from utils.debug import eprint


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
