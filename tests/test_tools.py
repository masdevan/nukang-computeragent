from app.services.tools import (
    execute_tool, format_call, looks_like_tool_attempt, parse_tool_call,
)


def test_parse_valid_json():
    text = '{"tool": {"name": "click", "args": {"button": "left"}}}'
    assert parse_tool_call(text) == {"name": "click", "args": {"button": "left"}}


def test_parse_prose_around_json():
    text = 'Sekarang saya klik dulu. {"tool": {"name": "click", "args": {"button": "left"}}}'
    assert parse_tool_call(text)["name"] == "click"


def test_parse_code_fence():
    text = '```json\n{"tool": {"name": "press_key", "args": {"key": "enter"}}}\n```'
    assert parse_tool_call(text)["name"] == "press_key"


def test_parse_broken_quotes_returns_none():
    text = '{"tool": {"name": "type_text", "args": {"text": "rusak "kutip" di sini"}}}'
    assert parse_tool_call(text) is None
    assert looks_like_tool_attempt(text)


def test_parse_plain_text_returns_none():
    assert parse_tool_call("jawaban teks biasa saja") is None
    assert not looks_like_tool_attempt("jawaban teks biasa saja")


def test_parse_empty_text():
    assert parse_tool_call("") is None


def test_format_call():
    tool_call = {"name": "press_combo", "args": {"combo": "win"}}
    assert format_call(tool_call) == "press_combo(combo=win)"


def test_execute_unknown_tool():
    result = execute_tool({"name": "explode", "args": {}})
    assert result == "Unknown tool: explode"
