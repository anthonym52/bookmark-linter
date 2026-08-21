"""Command-line entry point. Kept thin on purpose: all the logic that needs
testing lives in pure functions in parser.py and checks.py, this module just
wires stdin/argv/stdout to them.
"""

import sys

from .checks import lint_all
from .config import ConfigError, load_config
from .parser import parse_bookmarks


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: bookmarklint [--config PATH] <bookmarks.html>", file=sys.stderr)
        return 2

    config_path = None
    positional = []
    args = iter(argv)
    for arg in args:
        if arg == "--config":
            try:
                config_path = next(args)
            except StopIteration:
                print("--config requires a path argument", file=sys.stderr)
                return 2
        else:
            positional.append(arg)

    if not positional:
        print("usage: bookmarklint [--config PATH] <bookmarks.html>", file=sys.stderr)
        return 2

    enabled_checks = None
    if config_path is not None:
        try:
            enabled_checks = load_config(config_path)
        except OSError as error:
            print(f"{config_path}: {error.strerror}", file=sys.stderr)
            return 2
        except ConfigError as error:
            print(f"{config_path}: {error}", file=sys.stderr)
            return 2

    path = positional[0]
    with open(path, encoding="utf-8") as handle:
        html_text = handle.read()

    bookmarks, folders = parse_bookmarks(html_text)
    findings = lint_all(bookmarks, folders, enabled_checks)

    for finding in findings:
        print(f"{path}:{finding.line}: {finding.check}: {finding.message}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
