def list_to_yaml(li: list[str], link_folder: str = "") -> str:
    if not li:
        return "" # Empty
    a = "  - "
    if link_folder:
        fn = lambda s: f'"[[{link_folder}/{s.title()}|{s.title()}]]"'
    else:
        fn = lambda s: f'"{s}"'
    a += "\n  - ".join(map(fn, li))
    return a

def fmt_bool(b: bool) -> str:
    return str(b).lower()
