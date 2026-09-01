"""Lint exported browser bookmark files and report findings by line number."""

from .parser import Bookmark, Folder, parse_bookmarks
from .checks import (
    CHECK_NAMES,
    Finding,
    find_duplicate_urls,
    find_empty_folders,
    find_empty_titles,
    find_javascript_urls,
    find_malformed_urls,
    lint_all,
)
from .config import ConfigError, load_config, parse_config
from .fix import remove_duplicate_bookmarks

__all__ = [
    "Bookmark",
    "Folder",
    "Finding",
    "CHECK_NAMES",
    "ConfigError",
    "parse_bookmarks",
    "find_duplicate_urls",
    "find_empty_folders",
    "find_empty_titles",
    "find_javascript_urls",
    "find_malformed_urls",
    "lint_all",
    "load_config",
    "parse_config",
    "remove_duplicate_bookmarks",
]
