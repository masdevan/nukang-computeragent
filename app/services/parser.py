import json
import re


def parse_tool_call(text):
    candidates = extract_json_blocks(text)
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        tool = payload.get("tool")
        if isinstance(tool, dict) and isinstance(tool.get("name"), str):
            return tool
    return None


def extract_json_blocks(text):
    stripped = re.sub(r"```(?:json)?\s*|\s*```", "", text)
    candidates = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", stripped):
        try:
            payload, _ = decoder.raw_decode(stripped, match.start())
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            candidates.append(json.dumps(payload))
    if stripped not in candidates:
        candidates.append(stripped)
    return candidates


def looks_like_tool_attempt(text):
    return '"tool"' in text and ('"name"' in text or '"args"' in text)


def format_call(tool_call):
    args = tool_call.get("args", {})
    return f"{tool_call['name']}({', '.join(f'{k}={v}' for k, v in args.items())})"
