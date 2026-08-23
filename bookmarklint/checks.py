"""Checks that turn parsed bookmarks/folders into findings.

Every check here is a pure function: it takes the data structures produced
by bookmarklint.parser and returns a plain list of Finding, with no I/O and
no reliance on anything outside its arguments. That's what makes them easy
to unit test with a handful of Bookmark/Folder literals instead of fixture
files.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Finding:
    line: int
    check: str
    message: str


CHECK_NAMES = (
    "duplicate-url",
    "javascript-url",
    "empty-title",
    "empty-folder",
    "malformed-url",
)

# Schemes where a missing host is normal rather than a sign the URL got
# mangled, e.g. by a bad find-and-replace on export.
_SCHEMES_WITHOUT_REQUIRED_HOST = {"file", "about", "data", "mailto", "tel"}


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


def _malformed_reason(url):
    """Return a description of what's wrong with url, or None if it's fine.

    This never touches the network; it only looks at the URL's shape. A URL
    can be well-formed and still 404, and this makes no attempt to catch
    that - it's aimed at the export-time mistakes that are easy to spot
    statically: no scheme, stray whitespace from a bad copy-paste, or a
    http(s) link with no host at all.
    """
    if any(character.isspace() for character in url):
        return "URL contains whitespace"
    scheme, netloc, _path, _query, _fragment = urlsplit(url)
    if not scheme:
        return "URL has no scheme"
    if not netloc and scheme not in _SCHEMES_WITHOUT_REQUIRED_HOST:
        return f"{scheme}: URL has no host"
    return None


def find_malformed_urls(bookmarks):
    """Flag URLs that are missing a scheme, missing a host, or contain whitespace.

    javascript: bookmarklets are covered by find_javascript_urls instead, and
    bookmarks with no URL at all aren't this check's concern.
    """
    findings = []
    for bookmark in bookmarks:
        url = bookmark.url.strip()
        if not url or url.lower().startswith("javascript:"):
            continue
        reason = _malformed_reason(url)
        if reason:
            findings.append(
                Finding(
                    line=bookmark.line,
                    check="malformed-url",
                    message=f"{reason} ({bookmark.url})",
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
    if "malformed-url" in enabled_checks:
        findings.extend(find_malformed_urls(bookmarks))
    return sorted(findings, key=lambda finding: finding.line)
