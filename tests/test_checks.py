from bookmarklint.checks import (
    find_duplicate_urls,
    find_empty_folders,
    find_empty_titles,
    find_javascript_urls,
    lint_all,
)
from bookmarklint.parser import Bookmark, Folder


def make_bookmark(title="Title", url="https://example.com", line=1, folder=()):
    return Bookmark(title=title, url=url, line=line, folder=folder)


def make_folder(name="Folder", line=1, parent=()):
    return Folder(name=name, line=line, parent=parent)


def test_find_duplicate_urls_flags_repeats():
    bookmarks = (
        make_bookmark(url="https://a.example", line=1),
        make_bookmark(url="https://b.example", line=2),
        make_bookmark(url="https://a.example", line=3),
    )
    findings = find_duplicate_urls(bookmarks)
    assert len(findings) == 1
    assert findings[0].line == 3
    assert findings[0].check == "duplicate-url"
    assert "line 1" in findings[0].message


def test_find_duplicate_urls_ignores_bookmarks_with_no_url():
    bookmarks = (
        make_bookmark(url="", line=1),
        make_bookmark(url="", line=2),
    )
    assert find_duplicate_urls(bookmarks) == []


def test_find_duplicate_urls_no_duplicates():
    bookmarks = (
        make_bookmark(url="https://a.example", line=1),
        make_bookmark(url="https://b.example", line=2),
    )
    assert find_duplicate_urls(bookmarks) == []


def test_find_javascript_urls_matches_case_insensitively():
    bookmarks = (
        make_bookmark(url="JavaScript:void(0)", line=1),
        make_bookmark(url="https://example.com", line=2),
    )
    findings = find_javascript_urls(bookmarks)
    assert len(findings) == 1
    assert findings[0].line == 1
    assert findings[0].check == "javascript-url"


def test_find_javascript_urls_ignores_leading_whitespace():
    bookmarks = (make_bookmark(url="  javascript:doStuff()", line=5),)
    findings = find_javascript_urls(bookmarks)
    assert len(findings) == 1
    assert findings[0].line == 5


def test_find_empty_titles_flags_blank_and_whitespace_only():
    bookmarks = (
        make_bookmark(title="", line=1),
        make_bookmark(title="   ", line=2),
        make_bookmark(title="Real Title", line=3),
    )
    findings = find_empty_titles(bookmarks)
    assert {finding.line for finding in findings} == {1, 2}
    assert all(finding.check == "empty-title" for finding in findings)


def test_find_empty_folders_flags_folder_with_no_bookmarks_or_subfolders():
    folders = (make_folder(name="Someday", line=1, parent=()),)
    findings = find_empty_folders((), folders)
    assert len(findings) == 1
    assert findings[0].check == "empty-folder"
    assert "Someday" in findings[0].message


def test_find_empty_folders_ignores_folder_with_direct_bookmark():
    folders = (make_folder(name="Work", line=1, parent=()),)
    bookmarks = (make_bookmark(url="https://a.example", line=2, folder=("Work",)),)
    assert find_empty_folders(bookmarks, folders) == []


def test_find_empty_folders_ignores_folder_that_only_holds_a_subfolder():
    folders = (
        make_folder(name="Parent", line=1, parent=()),
        make_folder(name="Child", line=2, parent=("Parent",)),
    )
    bookmarks = (
        make_bookmark(url="https://a.example", line=3, folder=("Parent", "Child")),
    )
    findings = find_empty_folders(bookmarks, folders)
    assert findings == []


def test_find_empty_folders_flags_only_the_truly_empty_one():
    folders = (
        make_folder(name="Parent", line=1, parent=()),
        make_folder(name="Empty Child", line=2, parent=("Parent",)),
    )
    bookmarks = ()
    findings = find_empty_folders(bookmarks, folders)
    assert len(findings) == 1
    assert findings[0].line == 2
    assert "Empty Child" in findings[0].message


def test_lint_all_combines_and_sorts_by_line():
    bookmarks = (
        make_bookmark(title="", url="javascript:void(0)", line=10),
        make_bookmark(url="https://a.example", line=1),
        make_bookmark(url="https://a.example", line=5),
    )
    findings = lint_all(bookmarks, ())
    assert [finding.line for finding in findings] == [5, 10, 10]
    checks_at_line_10 = {finding.check for finding in findings if finding.line == 10}
    assert checks_at_line_10 == {"javascript-url", "empty-title"}
