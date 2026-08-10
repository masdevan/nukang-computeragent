import sys
from pathlib import Path

MAX_CHARS = 10000


def read_file(path):
    file = Path(path)
    if not file.exists():
        return f"File not found: {path}"
    if not file.is_file():
        return f"Not a file: {path}"
    try:
        content = file.read_text(encoding="utf-8", errors="replace")
    except Exception as error:
        return f"Cannot read: {error}"
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + f"\n...[truncated {len(content) - MAX_CHARS} chars]"
    return content


def main():
    print("File reader ready.")
    print("Commands: read <path> | quit")
    while True:
        try:
            line = input("file> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == "quit":
            break
        if line.startswith("read "):
            print(read_file(line[5:].strip()))
            continue
        print(f"Unknown command: {line}")


if __name__ == "__main__":
    sys.exit(main())
