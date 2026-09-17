# Changelog

## Unreleased

- `--fix` now reports a clean CLI error and exits 2 if the file can't be
  written back (permission denied, read-only filesystem, etc.) instead of
  crashing with a traceback.

## 0.1.0

First release.

- Parser for the Netscape Bookmark File Format (Chrome, Firefox, Safari
  exports), recovering titles, URLs, folder paths, and source line numbers.
- Checks: `duplicate-url`, `javascript-url`, `empty-title`, `empty-folder`,
  `malformed-url` (missing scheme, missing host, or stray whitespace).
- `--config` to enable/disable individual checks via an INI file.
- `--format json` for machine-readable output alongside the default text
  format.
- `--fix` to rewrite a file in place, dropping exact duplicate bookmarks.
- Parser and checks are pure functions with no filesystem or network access,
  usable as a library independent of the CLI.
