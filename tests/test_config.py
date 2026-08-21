import pytest

from bookmarklint.checks import CHECK_NAMES
from bookmarklint.config import ConfigError, parse_config


def test_no_config_text_enables_everything():
    assert parse_config("") == frozenset(CHECK_NAMES)


def test_missing_checks_section_enables_everything():
    text = "[other]\nkey = value\n"
    assert parse_config(text) == frozenset(CHECK_NAMES)


def test_disabling_one_check_leaves_the_rest_enabled():
    text = "[checks]\nempty-title = false\n"
    enabled = parse_config(text)
    assert "empty-title" not in enabled
    assert enabled == frozenset(CHECK_NAMES) - {"empty-title"}


def test_explicitly_enabling_a_check_is_a_no_op():
    text = "[checks]\nduplicate-url = true\n"
    assert parse_config(text) == frozenset(CHECK_NAMES)


def test_disabling_every_check_yields_empty_set():
    lines = [f"{name} = false" for name in CHECK_NAMES]
    text = "[checks]\n" + "\n".join(lines) + "\n"
    assert parse_config(text) == frozenset()


def test_unknown_check_name_raises_config_error():
    text = "[checks]\nnot-a-real-check = true\n"
    with pytest.raises(ConfigError):
        parse_config(text)


def test_non_boolean_value_raises_config_error():
    text = "[checks]\nempty-title = maybe\n"
    with pytest.raises(ConfigError):
        parse_config(text)


def test_boolean_values_accept_common_spellings():
    text = "[checks]\nempty-title = no\nempty-folder = yes\n"
    enabled = parse_config(text)
    assert "empty-title" not in enabled
    assert "empty-folder" in enabled
