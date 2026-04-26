import argparse

def eprint(*args, **kw):
    import sys
    print(*args, file=sys.stderr, **kw)

class colors:
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
        args = parser.parse_args()

        first_page = int(args.page)
        last_page = int(args.last_page if args.last_page else first_page)
        self.page_range = slice(first_page - 1, last_page)
