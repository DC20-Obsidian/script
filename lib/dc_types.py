import json
import re
import enum
from .fixup_text import fixup_name
from .utils import colors

class Spell:
    def __init__(self):
        self.name: str = ""
        self.page_number: int = -1
        self.source: list[str] = []
        self.school: str = ""
        self.tags: list[str] = []
        self.cost: str = ""
        self.ap_cost: int = -1
        self.mp_cost: int = -1
        self.sustained: bool = False
        self.range: str = ""
        self.duration: str = ""
        self.description: str = ""
        self.enhancements: list[Enhancement] = []

    def fixup(self) -> Spell:
        ap = re.search(r'([0-9]+) ?AP', self.cost)
        ap = ap.group(1) if ap else 0
        self.ap_cost = int(ap)
        mp = re.search(r'([0-9]+) ?MP|minimum of ([0-9]+)', self.cost)
        mp = mp.groups() if mp else (0, 0)
        mp = mp[0] or mp[1]
        self.mp_cost = int(mp)
        if "Sustained" in self.duration:
            self.sustained = True
            self.duration = re.sub(r' ?\(?Sustained\)?', '', self.duration)
        return self

class Enhancement:
    def __init__(self):
        from typing import Optional
        self.name: str = ""
        self.cost: str = ""
        self.repeatable: bool = False
        self.sustained: bool = False
        self.dependent_on: Optional[str] = None
        # ap/mp_cost is a string because "X" is a valid value
        self.ap_cost: str = ""
        self.mp_cost: str = ""
        self.description: str = ""

    def fixup(self):
        if "Repeatable" in self.cost:
            self.repeatable = True
            self.cost = re.sub(r',? ?Repeatable', '', self.cost)

        if "Sustained" in self.cost:
            self.sustained = True
            self.cost = re.sub(r',? ?Sustained', '', self.cost)

        # doesn't use full "Requires" because of a spelling error in "Luminous Burst" (page 129)
        if "Requi" in self.cost:
            regex = re.compile(r',? ?Requir?es ([a-zA-Z ]+)')
            self.dependent_on = regex.search(self.cost).group(1)
            self.cost = regex.sub('', self.cost)

        ap = re.search(r'([0-9X]+) ?AP', self.cost)
        self.ap_cost = (ap.group(1) if ap else "0")

        mp = re.search(r'([0-9X]+) ?MP', self.cost)
        self.mp_cost = (mp.group(1) if mp else "0")

        return self

class DCObjEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Spell, Enhancement, TextItem, DCProtoItem)):
            d = o.__dict__
            # if isinstance(o, Spell):
            #     d.pop("_current_enhmt")
            return d
        else:
            return json.JSONEncoder.default(self, o)

class TextItem:
    def __init__(self, item: dict, page: int):
        self.page: int = page
        self.text: str = item['text']
        self.font: str = item['fontName']
        self.font_size = item['fontSize']

class DCProtoItem:
    def __init__(self):
        self.name: str = ""
        self.items: list[TextItem] = []

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
