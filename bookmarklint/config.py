"""Optional config file for turning individual checks on or off.

The format is a minimal INI file with one section:

    [checks]
    duplicate-url = false
    javascript-url = true

Checks left out of the file keep their default of enabled. This mirrors
how most linters handle config: absence means "use the default", not
"disabled".
"""

import configparser

from .checks import CHECK_NAMES


class ConfigError(ValueError):
    """A config file named an unknown check or gave one a non-boolean value."""


def parse_config(text):
    """Parse config file text into a frozenset of enabled check names.

    Pure function: the same text always yields the same set, and nothing
    here touches the filesystem.
    """
    parser = configparser.ConfigParser()
    parser.read_string(text)

    enabled = set(CHECK_NAMES)
    if not parser.has_section("checks"):
        return frozenset(enabled)

    for name, raw_value in parser.items("checks"):
        if name not in CHECK_NAMES:
            known = ", ".join(sorted(CHECK_NAMES))
            raise ConfigError(f"unknown check {name!r} (known checks: {known})")
        try:
            is_enabled = parser.getboolean("checks", name)
        except ValueError:
            raise ConfigError(f"check {name!r} must be true or false, got {raw_value!r}") from None
        if is_enabled:
            enabled.add(name)
        else:
            enabled.discard(name)

    return frozenset(enabled)


def load_config(path):
    """Read a config file from disk and parse it."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    return parse_config(text)
