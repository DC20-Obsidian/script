import re

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

acronyms: str = (
    f"(?: |^)({'|'.join(re.escape(a) for a in load_words(['acronyms']))})(?: |$)"
)
articles: str = (
    f"(?: |^)({'|'.join(re.escape(a) for a in load_words(['articles']))})(?: |$)"
)


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

    misc_fixes = [
        (r"’", r"'"),
        (r"\u0001+", r" "),
        # (r'([,:\.])', add_space_after), # , . :
        (r" \n", "\n"),
        (r"([\(])", add_space_before),  # (
        (r" ([\.,:\)])", identity),  # Remove spaces in front
        (r"([\(]) ", identity),  # Remove spaces after
        # (r"([*\)]) :", r"\1:"),  # "Save (5) :" -> "Save (5):"
        (r"\*+ \*+", r" "),
        (r"P ?a ?s ?s ?i ?v ?e", r"Passive"),
        (r" ?\*\*Spell Passive ?", r"\n**Spell Passive"),
        (r"Additionaly", r"Additionally"),
        (r" +", r" "),  # Remove duplicate spaces
    ]

    for fix in misc_fixes:
        s = re.sub(fix[0], fix[1], s)
    return s.strip()


def fixup_name(name: str, ty: str) -> str:
    name = re.sub("’", "'", name)
    if words.get(ty) is not None:
        name = fixup(name.lower(), words[ty])
    name = name.title()
    name = cap_acronyms(name)
    name = lower_articles(name)
    name = lower_articles(name)  # Run it twice
    name = re.sub(
        "-([A-Z])", lambda m: f"-{m.group(1).lower()}", name
    )  # Foo-Bar -> Foo-bar
    name = re.sub(" +", " ", name)
    return re.sub("'S", "'s", name).strip()


def fixup_description(s: str) -> str:
    s = fixup_misc(s).removesuffix("\n-")
    s = re.sub(r"Wild Magic Table", "[[Wild Magic Table]]", s)
    return s
