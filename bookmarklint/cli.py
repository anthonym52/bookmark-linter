"""Command-line entry point. Kept thin on purpose: all the logic that needs
testing lives in pure functions in parser.py and checks.py, this module just
wires stdin/argv/stdout to them.
"""

import json
import sys

from .checks import lint_all
from .config import ConfigError, load_config
from .fix import remove_duplicate_bookmarks
from .parser import parse_bookmarks

USAGE = "usage: bookmarklint [--config PATH] [--format text|json] [--fix] <bookmarks.html>"


def render_text(path, findings):
    """Render findings the way a compiler would: one line per finding."""
    return [f"{path}:{finding.line}: {finding.check}: {finding.message}" for finding in findings]


def render_json(path, findings):
    """Render findings as a single JSON object, for editors and CI to parse.

    Pure function: same arguments always produce the same string, with keys
    sorted so the output is stable across runs.
    """
    payload = {
        "file": path,
        "findings": [
            {"line": finding.line, "check": finding.check, "message": finding.message}
            for finding in findings
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2

    config_path = None
    output_format = "text"
    fix = False
    positional = []
    args = iter(argv)
    for arg in args:
        if arg == "--config":
            try:
                config_path = next(args)
            except StopIteration:
                print("--config requires a path argument", file=sys.stderr)
                return 2
        elif arg == "--format":
            try:
                output_format = next(args)
            except StopIteration:
                print("--format requires an argument (text or json)", file=sys.stderr)
                return 2
            if output_format not in ("text", "json"):
                print(f"--format must be 'text' or 'json', got {output_format!r}", file=sys.stderr)
                return 2
        elif arg == "--fix":
            fix = True
        else:
            positional.append(arg)

    if not positional:
        print(USAGE, file=sys.stderr)
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

    if fix:
        fixed_text, removed_count = remove_duplicate_bookmarks(html_text)
        if removed_count:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(fixed_text)
            noun = "bookmark" if removed_count == 1 else "bookmarks"
            print(f"{path}: removed {removed_count} duplicate {noun}", file=sys.stderr)
            html_text = fixed_text

    bookmarks, folders = parse_bookmarks(html_text)
    findings = lint_all(bookmarks, folders, enabled_checks)

    if output_format == "json":
        print(render_json(path, findings))
    else:
        for line in render_text(path, findings):
            print(line)

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
