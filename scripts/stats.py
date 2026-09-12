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
        "cacheSeconds": 3600,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="badges", help="Directory for badge JSON files")
    args = parser.parse_args()

    en = locale_stats("en")
    ru = locale_stats("ru")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    write_json(out / "stats.json", {"en": en, "ru": ru})
    write_json(out / "en.json", endpoint("en", str(en["essays"]), "1f6feb"))
    write_json(
        out / "en-words.json",
        endpoint("words_written", str(en["words_written"]), "1f6feb"),
    )
    write_json(out / "ru.json", endpoint("ru", str(ru["essays"]), "2da44e"))
    write_json(
        out / "ru-words.json",
        endpoint("words_written", str(ru["words_written"]), "2da44e"),
    )

    print(f"en: {en['essays']}, words_written: {en['words_written']}")
    print(f"ru: {ru['essays']}, words_written: {ru['words_written']}")


if __name__ == "__main__":
    main()
