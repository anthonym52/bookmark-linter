"""Command-line entry point. Kept thin on purpose: all the logic that needs
testing lives in pure functions in parser.py and checks.py, this module just
wires stdin/argv/stdout to them.
"""

import sys

from .checks import lint_all
from .parser import parse_bookmarks


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: bookmarklint <bookmarks.html>", file=sys.stderr)
        return 2

    path = argv[0]
    with open(path, encoding="utf-8") as handle:
        html_text = handle.read()

    bookmarks, folders = parse_bookmarks(html_text)
    findings = lint_all(bookmarks, folders)

    for finding in findings:
        print(f"{path}:{finding.line}: {finding.check}: {finding.message}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
