import re


def load_words(files: list[str]) -> list[str]:
    words: list[str] = []
    for file in files:
        with open(file, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                words.append(line)
    words.sort(key=str.__len__, reverse=True)
    return words


names = load_words(["./words/names.txt"])


def fixup(s: str, words: list[str]) -> str:
    def replace(match: re.Match):
        # return f' {colors.RED}{match.group(1)}{colors.ENDC} '
        # return f' foo{match.group(1)}bar '
        return f" {match.group(1)} "

    pattern = r"(" + "|".join(re.escape(w) for w in words) + r")"
    s = re.sub(pattern, replace, s)
    s = re.sub(" +", " ", s)
    s = re.sub("’", "'", s)

    return s.strip()


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
        (r" +", r" "),  # Remove duplicate spaces
    ]

    for fix in misc_fixes:
        s = re.sub(fix[0], fix[1], s)
    return s.strip()


def fixup_name(s: str) -> str:
    s = fixup(s.lower(), names).title()
    return re.sub("'S", "'s", s)


def fixup_description(s: str) -> str:
    return fixup_misc(s)
