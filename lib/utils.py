from dc_types import TextItem
from dc_types.item_list import ItemList
import argparse

def eprint(*args, **kw):
    import sys
    print(*args, file=sys.stderr, **kw)

class colors:
    ITALICS = '\033[3m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    LIGHTYELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    LIGHTPURPLE = '\033[95m'
    LIGHTCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Args:
    def __init__(self, default_page: int):
        parser = argparse.ArgumentParser(
            prog='parse-spells'
        )
        parser.add_argument('page', default=default_page, nargs='?')
        parser.add_argument('last_page', nargs='?')
        parser.add_argument('-a', '--all', action='store_true', help="use all page (configured by type)")
        parser.add_argument('-r', '--raw', action='store_true', help="output raw data")
        parser.add_argument('-w', '--write', action='store_true', help="write the output to files")
        parser.add_argument('-p', '--print', action='store_true', help="print the output to stdout")
        parser.add_argument('-t', '--type', choices=["spells"], help="the type of item to parse")
        parser.add_argument('-u', '--unprocessed', action='store_true', help="only output unprocessed textitems (implies --raw)")
        parser.add_argument('-f', '--file', help="filtered JSON containing PDF data to use")
        parser.add_argument('-s', '--saved', action='store_true', help="use saved json data instead of parsing it anew")
        args = parser.parse_args()

        first_page = int(args.page)
        last_page = int(args.last_page or first_page)
        self.page_range = slice(first_page - 1, last_page)
        self.all: bool = bool(args.all)
        self.unprocessed = bool(args.unprocessed)
        self.raw: bool = bool(args.raw) or self.unprocessed
        self.write: bool = bool(args.write)
        self.print: bool = bool(args.print)
        self.file: str = args.file
        self.type: str = args.type
        self.saved: bool = bool(args.saved)

def flatten_pages(pages: list[dict]) -> ItemList:
    items: ItemList = ItemList()
    for page in pages:
        page_number: int = page['page']
        for text_item in page['textItems']:
            item: TextItem = TextItem(text_item, page_number)
            items.append(item)
    return items

def save_file(path: str, name: str, s: str):
    name = f'{path}{name}.md'
    with open(name, 'w') as file:
        file.write(s)

def get_file_paths() -> dict[str, str]:
    return {
        "words": "./words/",
        "output": "./dc-obsidian/",
        "input": "./dc-obsidian/json/dc20_0.10.5_pdf_filtered.json",
    }
