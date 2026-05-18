def eprint(*args, **kw):
    import sys

    print(*args, file=sys.stderr, **kw)
