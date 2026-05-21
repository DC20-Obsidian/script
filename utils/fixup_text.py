import re
from typing import Callable, Union

# from utils.debug import eprint


def load_words(files: list[str]) -> list[str]:
    words: list[str] = []
    for file in files:
        with open(f"./words/{file}.txt", "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                words.append(line)
    words.sort(key=str.__len__, reverse=True)
    return words


def load_links(files: list[str]) -> list[tuple[re.Pattern, str]]:
    lines: list[str] = load_words(files)
    links = [line.partition(":") for line in lines]
    # return [(re.compile(fr"(?<=[\* \.,]|^){link[0].strip()}(?=[$\* \.,])"), link[2].strip()) for link in links]
    return [
        (re.compile(rf"(?<![^\* \.,\n]){link[0].strip()}(?![^\* \.,\n])"), link[2].strip())
        for link in links
    ]


def cap_acronyms(s: str) -> str:
    return re.sub(acronyms, lambda m: f" {m.group(1).upper()} ", s)


def lower_articles(s: str) -> str:
    return re.sub(articles, lambda m: f" {m.group(1).lower()} ", s)


words: dict[str, list[str]] = {
    "spell": load_words(["spells"]),
    "maneuver": load_words(["maneuvers"]),
    "enhancement": load_words(["enhancements"]),
    "condition": load_words(["conditions"]),
    "ancestry_trait": load_words(["ancestry_traits"]),
    "talent": load_words(["talents"]),
    "combat training": load_words(["combat_training"]),
    "features": load_words(["features"]),
    "subclasses": load_words(["subclasses"]),
}

links = load_links(["links"])

acronyms: str = (
    f"(?: |^)({'|'.join(re.escape(a) for a in load_words(['acronyms']))})(?: |$)"
)
articles: str = (
    f"(?: |^)({'|'.join(re.escape(a) for a in load_words(['articles']))})(?: |$)"
)


def fix_links(text: str, links: list[tuple[re.Pattern, str]]) -> str:
    for link in links:
        (replace_pat, link) = link

        def replace_link(match: re.Match[str]) -> str:
            if link:
                return f"[[{link}/{match.group(0)}|{match.group(0)}]]"
            else:
                return f"[[{match.group(0)}]]"

        text = re.sub(replace_pat, replace_link, text)
    return text


def fixup(s: str, words: list[str]) -> str:
    def replace(match: re.Match):
        # return f' {colors.RED}{match.group(1)}{colors.ENDC} '
        # return f' foo{match.group(1)}bar '
        return f" {match.group(1)} "

    if words:
        pattern = r"(" + "|".join(re.escape(w) for w in words) + r")"
        s = re.sub(pattern, replace, s)

    return s


def fixup_misc(s: str) -> str:
    def add_space_after(match: re.Match):
        return f"{match.group(1)} "

    def add_space_before(match: re.Match):
        return f" {match.group(1)}"

    def identity(match: re.Match):
        return match.group(1)

    misc_fixes: list[tuple[str, Union[str, Callable]]] = [
        (r"’", r"'"),
        (r"\u0001+", r" "),
        # (r'([,:\.])', add_space_after), # , . :
        (r" \n", "\n"),
        (r"([\(])", add_space_before),  # (
        (r" ([\.,:\)])", identity),  # Remove spaces in front
        (r"([\(]) ", identity),  # Remove spaces after
        # (r"([*\)]) :", r"\1:"),  # "Save (5) :" -> "Save (5):"
        ("-At-", "-at-"),
        (r"\*+ +\*+", r" "),
        (r"P ?a ?s ?s ?i ?v ?e", r"Passive"),
        (r" ?\*\*Spell Passive ?", r"\n**Spell Passive"),
        (r" +", r" "),  # Remove duplicate spaces
    ]

    for fix in misc_fixes:
        s = re.sub(fix[0], fix[1], s)
    return s.strip()


def fix_spelling(s: str) -> str:
    spelling: list[tuple[str, str]] = [
        (r"Additionaly", r"Additionally"),
        (r"Otherwordly", r"Otherworldly"),  # for Otherworldly Gift
        (r"discernable", r"discernible"),  # for Arcane Sigil
    ]
    for fix in spelling:
        s = re.sub(fix[0], fix[1], s)
    return s


def fixup_name(name: str, ty: str) -> str:
    if words.get(ty) is not None:
        name = fixup(name.lower(), words[ty])
    name = name.title()
    name = cap_acronyms(name)
    name = lower_articles(name)
    name = lower_articles(name)  # Run it twice
    # name = re.sub(
    #     "-([A-Z])", lambda m: f"-{m.group(1).lower()}", name
    # )  # Foo-Bar -> Foo-bar
    name = fixup_misc(name)
    name = re.sub("'S", "'s", name).strip()
    return fix_spelling(name)


def fixup_description(s: str) -> str:
    s = fixup_misc(s).removesuffix("\n-")
    s = fix_spelling(s)
    s = fix_links(s, links)
    return s
