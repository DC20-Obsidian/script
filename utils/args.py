import argparse
from lib.utils import eprint
from utils.colors import colors


class Args:
    def __init__(self, default_page: int):
        parser = argparse.ArgumentParser(prog="parse-spells")
        parser.add_argument("page", default=default_page, nargs="?")
        parser.add_argument("last_page", nargs="?")
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="use all pages (configured by type)",
        )
        parser.add_argument(
            "-r", "--raw", action="store_true", help="output raw data (implies --print)"
        )
        parser.add_argument(
            "-w", "--write", action="store_true", help="write the output to files"
        )
        parser.add_argument(
            "-p", "--print", action="store_true", help="print the output to stdout"
        )
        choices: list[str] = ["spells", "conditions", "maneuvers", "ancestries"]
        parser.add_argument(
            "-t",
            "--type",
            choices=choices,
            help="the type of item to parse",
        )
        parser.add_argument(
            "-u",
            "--unprocessed",
            action="store_true",
            help="only output unprocessed text fragments (implies --raw) (usefull for debugging)",
        )
        parser.add_argument(
            "-f",
            "--file",
            help="filtered JSON containing PDF data to use or saved JSON (see --saved)",
        )
        parser.add_argument(
            "-s",
            "--saved",
            action="store_true",
            help="use saved json data instead of parsing it anew",
        )
        parser.add_argument(
            "-m",
            "--markdown",
            action="store_true",
            help="output markdown insted of JSON",
        )
        args = parser.parse_args()

        first_page = int(args.page)
        last_page = int(args.last_page or first_page)
        self.page_range = slice(first_page - 1, last_page)
        self.all: bool = bool(args.all)
        self.unprocessed = bool(args.unprocessed)
        self.raw: bool = bool(args.raw) or self.unprocessed
        self.write: bool = bool(args.write)
        self.print: bool = bool(args.print) or self.raw
        self.file: str = args.file
        self.type: str = args.type
        self.saved: bool = bool(args.saved)
        self.markdown: bool = bool(args.markdown)

        if (not self.print) and (not self.write):
            bail("You must select either --print or --write or --help")
        if self.write and self.raw:
            bail("--write is not supported with --raw")
        if self.markdown and self.raw:
            bail("--markdown is not supported with --raw")
        if self.type not in choices:
            bail(f"Invalid selection of --type. Must be one of {choices}")
        if (
            self.page_range.start < 0 or self.page_range.stop < self.page_range.start
        ) and not self.all:
            bail("Invalid or missing page range")


def bail(msg: str):
    eprint(f"{colors.RED}{msg}{colors.ENDC}")
    exit(1)
