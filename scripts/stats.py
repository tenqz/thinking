#!/usr/bin/env python3
"""Count essays and words, write Shields.io endpoint JSON for CI badges."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"\S+")


def essay_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text


def word_count(path: Path) -> int:
    return len(WORD_RE.findall(essay_text(path)))


def locale_stats(locale: str) -> dict:
    files = sorted((ROOT / locale).glob("*.md"))
    words = sum(word_count(path) for path in files)
    return {
        "locale": locale,
        "essays": len(files),
        "words_written": words,
        "files": [path.name for path in files],
    }


def endpoint(label: str, message: str, color: str) -> dict:
    return {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
        "cacheSeconds": 300,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def badge_svg(label: str, message: str, color: str) -> str:
    def text_width(value: str) -> int:
        return int(round(len(value) * 6.6 + 12))

    left = text_width(label)
    right = text_width(message)
    total = left + right
    label_x = left * 5
    message_x = (left + right / 2) * 10
    label_len = max(left - 12, 10) * 10
    message_len = max(right - 12, 10) * 10
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" '
        f'aria-label="{label}: {message}">'
        f"<title>{label}: {message}</title>"
        '<linearGradient id="s" x2="0" y2="100%">'
        '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        '<stop offset="1" stop-opacity=".1"/>'
        "</linearGradient>"
        f'<clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>'
        '<g clip-path="url(#r)">'
        f'<rect width="{left}" height="20" fill="#555"/>'
        f'<rect x="{left}" width="{right}" height="20" fill="#{color}"/>'
        f'<rect width="{total}" height="20" fill="url(#s)"/>'
        "</g>"
        '<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" '
        'text-rendering="geometricPrecision" font-size="110">'
        f'<text aria-hidden="true" x="{label_x}" y="150" fill="#010101" fill-opacity=".3" '
        f'transform="scale(.1)" textLength="{label_len}">{label}</text>'
        f'<text x="{label_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{label_len}">{label}</text>'
        f'<text aria-hidden="true" x="{message_x}" y="150" fill="#010101" fill-opacity=".3" '
        f'transform="scale(.1)" textLength="{message_len}">{message}</text>'
        f'<text x="{message_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{message_len}">{message}</text>'
        "</g></svg>\n"
    )


def write_badge(out: Path, name: str, label: str, message: str, color: str) -> None:
    write_json(out / f"{name}.json", endpoint(label, message, color))
    (out / f"{name}.svg").write_text(badge_svg(label, message, color), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="badges", help="Directory for badge JSON files")
    args = parser.parse_args()

    en = locale_stats("en")
    ru = locale_stats("ru")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    write_json(out / "stats.json", {"en": en, "ru": ru})
    write_badge(out, "en", "en", str(en["essays"]), "1f6feb")
    write_badge(out, "en-words", "words_written", str(en["words_written"]), "1f6feb")
    write_badge(out, "ru", "ru", str(ru["essays"]), "2da44e")
    write_badge(out, "ru-words", "words_written", str(ru["words_written"]), "2da44e")

    print(f"en: {en['essays']}, words_written: {en['words_written']}")
    print(f"ru: {ru['essays']}, words_written: {ru['words_written']}")


if __name__ == "__main__":
    main()
