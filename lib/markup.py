import re
import enum
from typing import Optional
from dc_types import TextItem
from .utils import colors

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
            "list": ('', ' ')
        }, # NONE
        {
            "bold": (f'{colors.BOLD}', f'{colors.ENDC}'),
            "em": (f'{colors.BOLD}{colors.ITALICS}', f'{colors.ENDC}'),
            "list": ('\n ', ' ')
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
            s = re.sub('•', '', s)
            return f'{markup['list'][0]}{s}{markup['list'][1]}'
        else:
            return normal(s)

    # TODO support prev_item

    font = item.font
    t = item.text
    prev_font = (prev_item.font if prev_item else None)

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
