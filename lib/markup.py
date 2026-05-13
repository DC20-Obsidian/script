import re
import enum
from typing import Optional
from utils.colors import colors
from dc_types.text_frag import TextFrag


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


def markup(
    frag: Optional[TextFrag], prev_frag: Optional[TextFrag], style: MarkupStyle
) -> str:
    markup: list[dict] = [
        {"bold": ("", " "), "em": ("", " "), "list": ("", " ")},  # NONE
        {
            "bold": (f"{colors.BOLD}", f"{colors.ENDC}"),
            "em": (f"{colors.BOLD}{colors.ITALICS}", f"{colors.ENDC}"),
            "list": ("\n ", " "),
        },  # ANSI
        {
            "bold": ("**", "**"),
            "em": ("***", "***"),
            "list": ("\n- ", ""),
        },  # MARKDOWN
    ]
    markup: dict = markup[style.value]
    # import json
    # eprint(json.dumps(markup))

    if frag is None and prev_frag is None:
        return ""
    if frag is None:  # TMP
        return ""

    def bold_italic(s: str) -> str:
        return f"{markup['em'][0]}{s}{markup['em'][1]} "

    def bold(s: str) -> str:
        return f"{markup['bold'][0]}{s.strip()}{markup['bold'][1]} "

    def normal(s: str) -> str:
        return f"{s} "

    def header(s: str) -> str:
        return f"\n## {s}\n"

    def quote(s: str, type: str = "tip") -> str:
        (title, _, body) = s.partition(":")
        if body:
            body += " "
        return f"\n> [!{type}] {title}:\n> {body}"

    def list_mark(s: str):
        if "•" in s:
            s = re.sub("•", "", s)
            return f"{markup['list'][0]}{s}{markup['list'][1]}"
        else:
            return normal(s)

    # TODO support prev_item

    font = frag.font
    t = frag.text
    # prev_font = (prev_item.font if prev_item else None)

    if re.match(r"^DC Tip:", t):
        return quote(t, "tip")

    if re.match(r"^Beta Note:", t):
        return quote(t, "note")

    if re.match(r"^Example:", t):
        return quote(t, "example")

    match font:
        case "f11" | "f14":
            return bold(t)
        case "f21" | "f7":
            return bold_italic(t)
        case "f15":
            return list_mark(t)
        case "f27":
            return header(t)
        case "f5":
            return normal(t)
        case _:
            return normal(t)

    raise Exception("Unknown font")


def assert_font(frag: TextFrag, fonts: list[str]):
    assert frag.font in fonts, (
        f"Invalid font on page: {frag.page}. Expected one of: {fonts}, found: {frag.font}"
    )


def assert_item(frag: TextFrag, fonts: list[str], regex: re.Pattern):
    assert_font(frag, fonts)
    assert regex.match(frag.text) is not None, "frag does not match regex"
