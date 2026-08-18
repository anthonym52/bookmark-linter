"""Parse the Netscape Bookmark File Format used by Chrome, Firefox, and Safari exports.

The format nests folders as <H3> headings followed by a sibling <DL> that holds
the folder's contents, and represents each bookmark as an <A HREF="..."> inside
a <DT>. There is no official grammar for it beyond "what browsers happen to
write", so this parser tracks just enough structure (folder stack, current
element) to recover titles, URLs, folder paths, and source line numbers.
"""

from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class Bookmark:
    title: str
    url: str
    line: int
    folder: tuple


@dataclass(frozen=True)
class Folder:
    name: str
    line: int
    parent: tuple


class _NetscapeBookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bookmarks = []
        self.folders = []
        self._folder_stack = []
        self._pending_folder_name = None
        self._current_tag = None
        self._current_text = []
        self._current_href = None
        self._current_line = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._current_tag = "a"
            self._current_text = []
            self._current_href = dict(attrs).get("href", "")
            self._current_line = self.getpos()[0]
        elif tag == "h3":
            self._current_tag = "h3"
            self._current_text = []
            self._current_line = self.getpos()[0]
        elif tag == "dl":
            # A DL immediately following a folder heading holds that folder's
            # contents, so entering it pushes the folder onto the path stack.
            if self._pending_folder_name is not None:
                self._folder_stack.append(self._pending_folder_name)
                self._pending_folder_name = None

    def handle_endtag(self, tag):
        if tag == "a" and self._current_tag == "a":
            title = "".join(self._current_text).strip()
            self.bookmarks.append(
                Bookmark(
                    title=title,
                    url=self._current_href or "",
                    line=self._current_line,
                    folder=tuple(self._folder_stack),
                )
            )
            self._current_tag = None
        elif tag == "h3" and self._current_tag == "h3":
            name = "".join(self._current_text).strip()
            self.folders.append(
                Folder(name=name, line=self._current_line, parent=tuple(self._folder_stack))
            )
            self._pending_folder_name = name
            self._current_tag = None
        elif tag == "dl":
            if self._folder_stack:
                self._folder_stack.pop()

    def handle_data(self, data):
        if self._current_tag in ("a", "h3"):
            self._current_text.append(data)


def parse_bookmarks(html_text):
    """Parse a Netscape Bookmark File Format string.

    Returns a (bookmarks, folders) tuple of tuples. Same input always
    produces the same output; no filesystem or network access happens here.
    """
    parser = _NetscapeBookmarkParser()
    parser.feed(html_text)
    parser.close()
    return tuple(parser.bookmarks), tuple(parser.folders)
