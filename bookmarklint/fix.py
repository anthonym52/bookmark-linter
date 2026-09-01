"""Fix mode: rewrite a bookmarks export with exact duplicate bookmarks removed.

Only what find_duplicate_urls in checks.py flags gets touched: the first
bookmark with a given URL is always kept, and later repeats of that same URL
are dropped. Nothing else about the file changes.
"""

from .checks import find_duplicate_urls
from .parser import parse_bookmarks


def remove_duplicate_bookmarks(html_text):
    """Return (fixed_text, removed_count).

    A bookmark's line, as recorded by parse_bookmarks, is where its <A> tag
    starts. Netscape bookmark exports put one <DT><A ...>...</A> entry per
    line, so dropping that line removes exactly the duplicate bookmark and
    nothing else. Pure function: same input always produces the same output,
    and nothing here touches the filesystem.
    """
    bookmarks, _folders = parse_bookmarks(html_text)
    duplicate_lines = {finding.line for finding in find_duplicate_urls(bookmarks)}
    if not duplicate_lines:
        return html_text, 0

    lines = html_text.splitlines(keepends=True)
    kept_lines = [line for index, line in enumerate(lines, start=1) if index not in duplicate_lines]
    return "".join(kept_lines), len(duplicate_lines)
