from skills.general.keyboard_controls import parse_combo


def test_modifier_combo():
    assert parse_combo("ctrl+shift+s") == [("ctrl", 1), ("shift", 1), ("s", 1)]


def test_single_key():
    assert parse_combo("enter") == [("enter", 1)]


def test_repeat():
    assert parse_combo("right*5") == [("right", 5)]


def test_mixed_repeat_and_key():
    assert parse_combo("tab*3+enter") == [("tab", 3), ("enter", 1)]


def test_whitespace_and_case():
    assert parse_combo("  ctrl + ALT + Delete ") == [("ctrl", 1), ("alt", 1), ("delete", 1)]


def test_empty_parts_skipped():
    assert parse_combo("ctrl++alt") == [("ctrl", 1), ("alt", 1)]


def test_empty_string():
    assert parse_combo("") == []


def test_non_digit_repeat_defaults_one():
    assert parse_combo("a*x") == [("a", 1)]
