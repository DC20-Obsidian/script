
words: list[str] = []
with open('./words.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        words.append(line)
# words.sort(key=str.__len__, reverse=True)

if __name__ == "__main__":
    print(words)

def fixup(s: str):
    from utils import colors
    import re

    def replace(match):
        return f' {colors.RED}{match.group(0).strip()}{colors.ENDC} '

    pattern = r' ?(' + '|'.join(re.escape(w) for w in words) +r') ?'
    return re.sub(pattern, replace, s)
