from bookmarklint.fix import remove_duplicate_bookmarks
from bookmarklint.parser import parse_bookmarks


def test_removes_only_the_repeat_keeps_the_first():
    html = (
        "<DL><p>\n"
        '    <DT><A HREF="https://example.com">Example</A>\n'
        '    <DT><A HREF="https://a.example">A</A>\n'
        '    <DT><A HREF="https://example.com">Example again</A>\n'
        "</DL><p>\n"
    )
    fixed, removed_count = remove_duplicate_bookmarks(html)
    assert removed_count == 1
    bookmarks, _folders = parse_bookmarks(fixed)
    assert [bookmark.url for bookmark in bookmarks] == [
        "https://example.com",
        "https://a.example",
    ]
    assert [bookmark.title for bookmark in bookmarks] == ["Example", "A"]


def test_removes_every_repeat_when_a_url_appears_three_times():
    html = (
        "<DL><p>\n"
        '    <DT><A HREF="https://example.com">One</A>\n'
        '    <DT><A HREF="https://example.com">Two</A>\n'
        '    <DT><A HREF="https://example.com">Three</A>\n'
        "</DL><p>\n"
    )
    fixed, removed_count = remove_duplicate_bookmarks(html)
    assert removed_count == 2
    bookmarks, _folders = parse_bookmarks(fixed)
    assert [bookmark.title for bookmark in bookmarks] == ["One"]


def test_no_duplicates_returns_input_unchanged():
    html = (
        "<DL><p>\n"
        '    <DT><A HREF="https://a.example">A</A>\n'
        '    <DT><A HREF="https://b.example">B</A>\n'
        "</DL><p>\n"
    )
    fixed, removed_count = remove_duplicate_bookmarks(html)
    assert removed_count == 0
    assert fixed == html


def test_bookmarks_with_no_url_are_not_treated_as_duplicates():
    html = (
        "<DL><p>\n"
        "    <DT><A>No href one</A>\n"
        "    <DT><A>No href two</A>\n"
        "</DL><p>\n"
    )
    fixed, removed_count = remove_duplicate_bookmarks(html)
    assert removed_count == 0
    assert fixed == html


def test_result_is_deterministic():
    html = (
        "<DL><p>\n"
        '    <DT><A HREF="https://example.com">One</A>\n'
        '    <DT><A HREF="https://example.com">Two</A>\n'
        "</DL><p>\n"
    )
    assert remove_duplicate_bookmarks(html) == remove_duplicate_bookmarks(html)
