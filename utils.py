import argparse
import re

from dc_types import TextItem
from fixup_text import fixup_name

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
        args = parser.parse_args()

        first_page = int(args.page)
        last_page = int(args.last_page if args.last_page else first_page)
        self.page_range = slice(first_page - 1, last_page)
        self.all: bool = bool(args.all)
        self.unprocessed = bool(args.unprocessed)
        self.raw: bool = bool(args.raw) or self.unprocessed
        self.write: bool = bool(args.write)
        self.print: bool = bool(args.print)
        self.type: str = args.type

def debug_headings(pages: list[dict]):
    headings = []
    current_heading = ""
    for page in pages:
        page_number = page['page']
        for text_item in page['textItems']:
            item = TextItem(text_item, page_number)
            if item.font == "g_d0_f3":
                current_heading += item.text
            else:
                if current_heading != "":
                    t = fixup_name(current_heading).title()
                    headings.append(t)
                    current_heading = ""

    for heading in headings:
        print(heading)

    return headings

def assert_font(item: TextItem, fonts: list[str]):
    assert item.font in fonts, f'Invalid font on page: {item.page}. Expected one of: {fonts}, found: {item.font}'

def assert_item(item: TextItem, fonts: list[str], regex: re.Pattern):
    assert_font(item, fonts)
    assert regex.match(item.text) != None, f'item does not match regex'
