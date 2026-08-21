"""Checks that turn parsed bookmarks/folders into findings.

Every check here is a pure function: it takes the data structures produced
by bookmarklint.parser and returns a plain list of Finding, with no I/O and
no reliance on anything outside its arguments. That's what makes them easy
to unit test with a handful of Bookmark/Folder literals instead of fixture
files.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    line: int
    check: str
    message: str


CHECK_NAMES = ("duplicate-url", "javascript-url", "empty-title", "empty-folder")


def find_duplicate_urls(bookmarks):
    """Flag bookmarks that repeat a URL already seen earlier in the file."""
    first_seen_at = {}
    findings = []
    for bookmark in bookmarks:
        if not bookmark.url:
            continue
        if bookmark.url in first_seen_at:
            findings.append(
                Finding(
                    line=bookmark.line,
                    check="duplicate-url",
                    message=(
                        f"duplicate bookmark for {bookmark.url} "
                        f"(first seen at line {first_seen_at[bookmark.url]})"
                    ),
                )
            )
        else:
            first_seen_at[bookmark.url] = bookmark.line
    return findings


def find_javascript_urls(bookmarks):
    """Flag javascript: bookmarklets, which browsers happily export mixed in with real links."""
    findings = []
    for bookmark in bookmarks:
        if bookmark.url.strip().lower().startswith("javascript:"):
            findings.append(
                Finding(
                    line=bookmark.line,
                    check="javascript-url",
                    message=f"bookmarklet ({bookmark.title!r}) stored as a javascript: URL",
                )
            )
    return findings


def find_empty_titles(bookmarks):
    """Flag bookmarks saved with no title, which are useless in a bookmarks menu."""
    findings = []
    for bookmark in bookmarks:
        if not bookmark.title.strip():
            findings.append(
                Finding(
                    line=bookmark.line,
                    check="empty-title",
                    message=f"bookmark has no title ({bookmark.url})",
                )
            )
    return findings


def find_empty_folders(bookmarks, folders):
    """Flag folders that hold neither a bookmark nor a subfolder."""
    paths_with_bookmarks = {bookmark.folder for bookmark in bookmarks}
    parent_paths = {folder.parent for folder in folders}
    findings = []
    for folder in folders:
        full_path = folder.parent + (folder.name,)
        if full_path not in paths_with_bookmarks and full_path not in parent_paths:
            findings.append(
                Finding(
                    line=folder.line,
                    check="empty-folder",
                    message=f"folder {folder.name!r} contains no bookmarks",
                )
            )
    return findings


def lint_all(bookmarks, folders, enabled_checks=None):
    """Run the enabled checks and return findings sorted by line number.

    enabled_checks, if given, is an iterable of names from CHECK_NAMES; any
    check not in it is skipped. Defaults to running every check.
    """
    if enabled_checks is None:
        enabled_checks = CHECK_NAMES
    enabled_checks = set(enabled_checks)

    findings = []
    if "duplicate-url" in enabled_checks:
        findings.extend(find_duplicate_urls(bookmarks))
    if "javascript-url" in enabled_checks:
        findings.extend(find_javascript_urls(bookmarks))
    if "empty-title" in enabled_checks:
        findings.extend(find_empty_titles(bookmarks))
    if "empty-folder" in enabled_checks:
        findings.extend(find_empty_folders(bookmarks, folders))
    return sorted(findings, key=lambda finding: finding.line)
