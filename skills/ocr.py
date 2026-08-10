import asyncio
import sys
from pathlib import Path

MAX_MODEL_CHARS = 12000


def ocr_image(image_bytes):
    try:
        return asyncio.run(ocr_async(image_bytes))
    except (ImportError, ModuleNotFoundError):
        return None
    except Exception as error:
        return f"OCR failed: {error}"


def ocr_file(path):
    return ocr_image(Path(path).read_bytes())


async def ocr_async(image_bytes):
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream

    stream = InMemoryRandomAccessStream()
    writer = DataWriter(stream)
    writer.write_bytes(image_bytes)
    await writer.store_async()
    stream.seek(0)

    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()

    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None and OcrEngine.available_recognizer_languages:
        engine = OcrEngine.try_create_from_language(OcrEngine.available_recognizer_languages[0])
    if engine is None:
        return "OCR unavailable"

    result = await engine.recognize_async(bitmap)
    lines = []
    for line in result.lines:
        if not line.words:
            continue
        words = []
        for word in line.words:
            rect = word.bounding_rect
            words.append((
                word.text,
                (round(rect.x), round(rect.y), round(rect.width), round(rect.height)),
                (round(rect.x + rect.width / 2), round(rect.y + rect.height / 2)),
            ))
        left = min(word.bounding_rect.x for word in line.words)
        top = min(word.bounding_rect.y for word in line.words)
        right = max(word.bounding_rect.x + word.bounding_rect.width for word in line.words)
        bottom = max(word.bounding_rect.y + word.bounding_rect.height for word in line.words)
        box = (round(left), round(top), round(right - left), round(bottom - top))
        center = (round((left + right) / 2), round((top + bottom) / 2))
        lines.append((line.text, box, center, words))
    return lines


def format_lines(lines):
    if isinstance(lines, str):
        return lines
    output = []
    for text, box, center, words in lines:
        output.append(f'"{text}" box{box} center{center}')
        for word_text, word_box, word_center in words:
            output.append(f'  "{word_text}" box{word_box} center{word_center}')
    return "\n".join(output)


def write_ocr_sidecar(png_path):
    lines = ocr_file(png_path)
    if isinstance(lines, str) or lines is None:
        return lines
    text = format_lines(lines)
    sidecar = Path(png_path).with_suffix(".ocr.txt")
    sidecar.write_text(text, encoding="utf-8")
    if len(text) > MAX_MODEL_CHARS:
        text = text[:MAX_MODEL_CHARS] + f"\n...[truncated {len(text) - MAX_MODEL_CHARS} chars]"
    return text


def main():
    print("OCR ready. Commands: ocr <image path> | screen | quit")
    while True:
        try:
            line = input("ocr> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == "quit":
            break
        if line == "screen":
            import pyautogui

            path = Path(pyautogui.screenshot().save if False else "ocr_capture.png")
            pyautogui.screenshot().save(str(path))
            print(format_lines(ocr_image(path.read_bytes())))
            path.unlink(missing_ok=True)
            continue
        if line.startswith("ocr "):
            print(format_lines(ocr_file(line[4:].strip())))
            continue
        print(f"Unknown command: {line}")


if __name__ == "__main__":
    sys.exit(main())
