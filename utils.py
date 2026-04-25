import argparse

def eprint(*args, **kw):
    import sys
    print(*args, file=sys.stderr, **kw)

# from blender
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
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
