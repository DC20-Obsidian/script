
words: list[str] = []
with open('./words.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        words.append(line)
words.sort(key=str.__len__, reverse=True)

if __name__ == "__main__":
    print(words)

def fixup(s: str):
    from utils import colors
    import re

    def replace(match: re.Match):
        # return f' {colors.RED}{match.group(1)}{colors.ENDC} '
        # return f' foo{match.group(1)}bar '
        return f' {match.group(1)} '
    def add_space_after(match: re.Match):
        return f'{match.group(1)} '
    def add_space_before(match: re.Match):
        return f' {match.group(1)}'
    def identity(match: re.Match):
        return match.group(1)

    misc_fixes = [
        (r' ona', ' on a'),
        (r' ina', ' in a'),
        (r'([,:\.])', add_space_after), # , . :
        (r'([\(])', add_space_before), # (
        (r'[ \u0001]+', ' '), # Remove duplicate spaces
        (r' ([\.,:\)])', identity), # Remove spaces in front
        (r'([\(]) ', identity), # Remove spaces after
        (r'\) :', '):'), # "Save (5) :" -> "Save (5):"
    ]

    pattern = r'(' + '|'.join(re.escape(w) for w in words) +r')'
    s = re.sub(pattern, replace, s)

    for fix in misc_fixes:
        s = re.sub(fix[0], fix[1], s)
    return s.strip()
