import re
from .utils import get_file_paths

def load_words(files: list[str]) -> list[str]:
    words: list[str] = []
    for file in files:
        with open(file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                words.append(line)
    words.sort(key=str.__len__, reverse=True)
    return words

dir = get_file_paths()['words']
names = load_words([f'{dir}names.txt'])

def fixup(s: str, words: list[str]) -> str:
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
        (r'’', "'"),
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

def fixup_name(s: str) -> str:
    s = fixup(s.lower(), names).title()
    return re.sub("'S", "'s", s)
