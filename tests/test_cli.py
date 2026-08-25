import json

from bookmarklint.checks import Finding
from bookmarklint.cli import main, render_json, render_text

BOOKMARKS_HTML = """
<DL><p>
    <DT><A HREF="https://example.com">Example</A>
    <DT><A HREF="https://example.com">Example again</A>
</DL><p>
"""


def test_render_text_formats_one_line_per_finding():
    findings = [
        Finding(line=3, check="duplicate-url", message="duplicate bookmark for https://example.com"),
    ]
    lines = render_text("bookmarks.html", findings)
    assert lines == ["bookmarks.html:3: duplicate-url: duplicate bookmark for https://example.com"]


def test_render_text_empty_findings_is_empty_list():
    assert render_text("bookmarks.html", []) == []


def test_render_json_shape_and_stability():
    findings = [
        Finding(line=3, check="duplicate-url", message="duplicate bookmark for https://example.com"),
    ]
    payload = json.loads(render_json("bookmarks.html", findings))
    assert payload == {
        "file": "bookmarks.html",
        "findings": [
            {"line": 3, "check": "duplicate-url", "message": "duplicate bookmark for https://example.com"}
        ],
    }


def test_render_json_empty_findings():
    payload = json.loads(render_json("bookmarks.html", []))
    assert payload == {"file": "bookmarks.html", "findings": []}


def test_main_json_format_prints_valid_json(tmp_path, capsys):
    bookmarks_file = tmp_path / "bookmarks.html"
    bookmarks_file.write_text(BOOKMARKS_HTML, encoding="utf-8")

    exit_code = main(["--format", "json", str(bookmarks_file)])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["file"] == str(bookmarks_file)
    assert len(payload["findings"]) == 1
    assert payload["findings"][0]["check"] == "duplicate-url"


def test_main_default_format_is_text(tmp_path, capsys):
    bookmarks_file = tmp_path / "bookmarks.html"
    bookmarks_file.write_text(BOOKMARKS_HTML, encoding="utf-8")

    exit_code = main([str(bookmarks_file)])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert out.startswith(str(bookmarks_file) + ":")


def test_main_rejects_unknown_format(tmp_path, capsys):
    bookmarks_file = tmp_path / "bookmarks.html"
    bookmarks_file.write_text(BOOKMARKS_HTML, encoding="utf-8")

    exit_code = main(["--format", "xml", str(bookmarks_file)])

    assert exit_code == 2
    assert "must be 'text' or 'json'" in capsys.readouterr().err


def test_main_format_missing_argument(tmp_path, capsys):
    bookmarks_file = tmp_path / "bookmarks.html"
    bookmarks_file.write_text(BOOKMARKS_HTML, encoding="utf-8")

    exit_code = main([str(bookmarks_file), "--format"])

    assert exit_code == 2
    assert "--format requires an argument" in capsys.readouterr().err


def test_main_clean_file_exits_zero(tmp_path, capsys):
    bookmarks_file = tmp_path / "bookmarks.html"
    bookmarks_file.write_text(
        '<DL><p><DT><A HREF="https://example.com">Example</A></DL><p>', encoding="utf-8"
    )

    exit_code = main(["--format", "json", str(bookmarks_file)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["findings"] == []
