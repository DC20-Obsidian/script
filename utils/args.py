import argparse

class Args:
    def __init__(self, default_page: int):
        parser = argparse.ArgumentParser(
            prog='parse-spells'
        )
        parser.add_argument('page', default=default_page, nargs='?')
        parser.add_argument('last_page', nargs='?')
        parser.add_argument('-a', '--all', action='store_true', help="use all page (configured by type)")
        parser.add_argument('-r', '--raw', action='store_true', help="output raw data")
        parser.add_argument('-w', '--write', action='store_true', help="write the output to files")
        parser.add_argument('-p', '--print', action='store_true', help="print the output to stdout")
        parser.add_argument('-t', '--type', choices=["spells", "conditions"], help="the type of item to parse")
        parser.add_argument('-u', '--unprocessed', action='store_true', help="only output unprocessed text fragments (implies --raw)")
        parser.add_argument('-f', '--file', help="filtered JSON containing PDF data to use")
        parser.add_argument('-s', '--saved', action='store_true', help="use saved json data instead of parsing it anew")
        args = parser.parse_args()

        first_page = int(args.page)
        last_page = int(args.last_page or first_page)
        self.page_range = slice(first_page - 1, last_page)
        self.all: bool = bool(args.all)
        self.unprocessed = bool(args.unprocessed)
        self.raw: bool = bool(args.raw) or self.unprocessed
        self.write: bool = bool(args.write)
        self.print: bool = bool(args.print)
        self.file: str = args.file
        self.type: str = args.type
        self.saved: bool = bool(args.saved)
