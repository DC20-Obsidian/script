import argparse
import re
from typing import Optional
import enum

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

class MarkupStyle(enum.Enum):
    NONE = 0
    ANSI = 1
    MARKDOWN = 2

class FontType(enum.Enum):
    UNKNOWN = 0
    NORMAL = 1
    BOLD = 2
    BOLD_ITALIC = 3
    LIST = 4

def markup(item: Optional[TextItem], prev_item: Optional[TextItem], style: MarkupStyle) -> str:
    markup: list[dict] = [
        {
            "bold": ('', ' '),
            "em": ('', ' '),
            "list": lambda s: s
        }, # NONE
        {
            "bold": (f'{colors.BOLD}', f'{colors.ENDC}'),
            "em": (f'{colors.BOLD}{colors.ITALICS}', f'{colors.ENDC}'),
            "list": lambda s: f'\n {s} '
        }, # ANSI
        {
            "bold": ('**', '**'),
            "em": ('***', '***'),
            "list": (f'\n- ', ''),
        }, # MARKDOWN
    ]
    markup: dict = markup[style.value]
    # import json
    # eprint(json.dumps(markup))

    if item is None and prev_item is None:
        return ""
    if item is None: #TMP
        return ""

    def bold_italic(s: str):
        return f'{markup['em'][0]}{s}{markup['em'][1]} '

    def bold(s: str):
        return f'{markup['bold'][0]}{s}{markup['bold'][1]} '

    def normal(s: str):
        return f'{s} '

    def list_mark(s: str):
        if "•" in s:
            return f'{markup['list'][0]}{s}{markup['list'][1]}'
        else:
            return normal(s)

    # TODO support prev_item

    font = item.font.removeprefix('g_d0_')
    t = item.text
    prev_font = (prev_item.font.removeprefix('g_d0_') if prev_item else None)

    match font:
        case 'f11' | 'f14':
            return bold(t)
        case 'f21' | 'f7':
            return bold_italic(t)
        case 'f15':
            return list_mark(t)
        case 'f5':
            return normal(t)
        case _:
            return normal(t)

    raise Exception("Unknown font")

def assert_font(item: TextItem, fonts: list[str]):
    assert item.font in fonts, f'Invalid font on page: {item.page}. Expected one of: {fonts}, found: {item.font}'

def assert_item(item: TextItem, fonts: list[str], regex: re.Pattern):
    assert_font(item, fonts)
    assert regex.match(item.text) != None, f'item does not match regex'
