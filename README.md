# bookmarklint

A linter for exported browser bookmark files. Point it at an HTML export from
Chrome, Firefox, or Safari and it reports problems by line number: duplicate
URLs saved twice under different folders, `javascript:` bookmarklets sitting
in the same list as real links, bookmarks with no title, folders that hold
nothing, and URLs that are missing a scheme, missing a host, or contain
whitespace.

Bookmark files accumulate this kind of cruft for years because nothing in
the browser UI ever points it out. This tool reads the export and tells you
exactly where the problems are so you can go fix them by hand.

## Usage

Export your bookmarks first (Chrome: `chrome://bookmarks` -> the three-dot
menu -> Export bookmarks. Firefox: Library -> Import and Backup -> Export
Bookmarks to HTML).

Then run:

```
python -m bookmarklint.cli bookmarks.html
```

or, after installing:

```
bookmarklint bookmarks.html
```

Example output:

```
bookmarks.html:42: duplicate-url: duplicate bookmark for https://example.com/ (first seen at line 17)
bookmarks.html:58: javascript-url: bookmarklet ('Toggle Reader View') stored as a javascript: URL
bookmarks.html:71: empty-title: bookmark has no title (https://old-project.example.org)
bookmarks.html:83: malformed-url: URL has no host (https:///broken)
bookmarks.html:90: empty-folder: folder 'Someday' contains no bookmarks
```

Exit code is 1 if any findings were reported, 0 if the file is clean.

## Disabling checks

By default all five checks run. To turn individual checks off, pass
`--config` with a path to an INI file with a `[checks]` section:

```ini
[checks]
empty-folder = false
```

Checks left out of the file keep running; only the ones listed as `false`
are skipped. Check names match the ones printed in the output:
`duplicate-url`, `javascript-url`, `empty-title`, `empty-folder`,
`malformed-url`.

```
bookmarklint --config bookmarklint.ini bookmarks.html
```

## Using it as a library

The parser and every check are pure functions: given the same input they
always return the same output, and none of them touch the filesystem or
network. That makes them straightforward to call from your own code or from
tests without fixture files:

```python
from bookmarklint import parse_bookmarks, lint_all

html_text = """
<DL><p>
    <DT><A HREF="https://example.com">Example</A>
    <DT><A HREF="https://example.com">Example again</A>
</DL><p>
"""

bookmarks, folders = parse_bookmarks(html_text)
for finding in lint_all(bookmarks, folders):
    print(finding.line, finding.check, finding.message)
```

## Installing

No third-party dependencies, standard library only.

```
pip install -e .
```

## Running tests

The test suite uses pytest, which is not a runtime dependency of the
package itself:

```
pip install pytest
pytest
```

## Status

Early skeleton. Five checks exist today: duplicate URLs, `javascript:` URLs,
empty titles, empty folders, and malformed URLs (missing scheme, missing
host, or stray whitespace). Each can be turned off via `--config`. The
malformed-URL check is purely structural - it never makes a network request,
so it won't catch a well-formed URL that happens to be dead. No JSON output
mode yet.
