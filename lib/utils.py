from dc_types.text_frag import TextFrag
from dc_types.frag_list import FragList


def eprint(*args, **kw):
    import sys

    print(*args, file=sys.stderr, **kw)


def flatten_pages(pages: list[dict]) -> FragList:
    frags: FragList = FragList()
    for page in pages:
        page_number: int = page["page"]
        for text_frag in page["textItems"]:
            frag: TextFrag = TextFrag(text_frag, page_number)
            frags.append(frag)
    return frags

