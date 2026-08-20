from bookmarklint.parser import parse_bookmarks


def test_empty_document_yields_nothing():
    bookmarks, folders = parse_bookmarks("")
    assert bookmarks == ()
    assert folders == ()


def test_single_top_level_bookmark():
    html = """<DL><p>
    <DT><A HREF="https://example.com">Example</A>
</DL><p>
"""
    bookmarks, folders = parse_bookmarks(html)
    assert folders == ()
    assert len(bookmarks) == 1
    bookmark = bookmarks[0]
    assert bookmark.title == "Example"
    assert bookmark.url == "https://example.com"
    assert bookmark.folder == ()
    assert bookmark.line == 2


def test_bookmark_without_href_gets_empty_url():
    html = """<DL><p>
    <DT><A>No href</A>
</DL><p>
"""
    (bookmark,), _ = parse_bookmarks(html)
    assert bookmark.url == ""


def test_title_decodes_character_references():
    html = '<DL><p><DT><A HREF="https://example.com">Tom &amp; Jerry</A></DL><p>'
    (bookmark,), _ = parse_bookmarks(html)
    assert bookmark.title == "Tom & Jerry"


def test_folder_contents_get_folder_path():
    html = """<DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://a.example">A</A>
    </DL><p>
</DL><p>
"""
    bookmarks, folders = parse_bookmarks(html)
    assert len(folders) == 1
    assert folders[0].name == "Work"
    assert folders[0].parent == ()
    assert len(bookmarks) == 1
    assert bookmarks[0].folder == ("Work",)


def test_nested_folders_build_up_a_path():
    html = """<DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://a.example">A</A>
        <DT><H3>Archive</H3>
        <DL><p>
            <DT><A HREF="https://b.example">B</A>
        </DL><p>
    </DL><p>
</DL><p>
"""
    bookmarks, folders = parse_bookmarks(html)
    by_url = {bookmark.url: bookmark for bookmark in bookmarks}
    assert by_url["https://a.example"].folder == ("Work",)
    assert by_url["https://b.example"].folder == ("Work", "Archive")

    by_name = {folder.name: folder for folder in folders}
    assert by_name["Work"].parent == ()
    assert by_name["Archive"].parent == ("Work",)


def test_sibling_folders_do_not_leak_into_each_other():
    html = """<DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://a.example">A</A>
    </DL><p>
    <DT><H3>Home</H3>
    <DL><p>
        <DT><A HREF="https://b.example">B</A>
    </DL><p>
</DL><p>
"""
    bookmarks, _ = parse_bookmarks(html)
    by_url = {bookmark.url: bookmark for bookmark in bookmarks}
    assert by_url["https://a.example"].folder == ("Work",)
    assert by_url["https://b.example"].folder == ("Home",)


def test_empty_folder_is_still_recorded():
    html = """<DL><p>
    <DT><H3>Someday</H3>
    <DL><p>
    </DL><p>
</DL><p>
"""
    bookmarks, folders = parse_bookmarks(html)
    assert bookmarks == ()
    assert len(folders) == 1
    assert folders[0].name == "Someday"


def test_line_numbers_track_source_position():
    html = (
        "<DL><p>\n"
        "    <DT><H3>Work</H3>\n"
        "    <DL><p>\n"
        '        <DT><A HREF="https://a.example">A</A>\n'
        "    </DL><p>\n"
        "</DL><p>\n"
    )
    bookmarks, folders = parse_bookmarks(html)
    assert folders[0].line == 2
    assert bookmarks[0].line == 4


def test_parsing_is_deterministic():
    html = """<DL><p>
    <DT><H3>Work</H3>
    <DL><p>
        <DT><A HREF="https://a.example">A</A>
    </DL><p>
</DL><p>
"""
    assert parse_bookmarks(html) == parse_bookmarks(html)
