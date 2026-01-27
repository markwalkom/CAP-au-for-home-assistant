#!/usr/bin/env python3
"""
Check for missing translation keys and placeholders across locales.

- Compares the base locale (en.json) against all other JSON files in
  custom_components/cap_alerts/translations/.
- Reports missing keys and missing placeholders (e.g., {link}, {slug}, {url}).
- Exits with code 1 if any issues are found; 0 otherwise.

Usage:
    python scripts/check_missing_translation_keys.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TRANSLATIONS_DIR = Path("custom_components/cap_alerts/translations")
BASE_LOCALE = "en.json"
PLACEHOLDER_PATTERN = re.compile(r"\{[a-zA-Z_]+\}")


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_keys(data: Any, prefix: str = "") -> List[str]:
    keys: List[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            keys.append(new_prefix)
            keys.extend(iter_keys(v, new_prefix))
    return keys


def get_value(data: Dict[str, Any], key_path: str) -> Any:
    parts = key_path.split(".")
    cur: Any = data
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def placeholders_in(text: str) -> List[str]:
    return PLACEHOLDER_PATTERN.findall(text)


def main() -> int:
    base_path = TRANSLATIONS_DIR / BASE_LOCALE
    if not base_path.exists():
        print(f"❌ Base locale not found: {base_path}")
        return 2

    base = load_json(base_path)

    all_locales = [p for p in TRANSLATIONS_DIR.glob("*.json") if p.name != BASE_LOCALE]
    if not all_locales:
        print("ℹ️ No additional locales to check.")
        return 0

    base_keys = iter_keys(base)
    issues: List[Tuple[str, str, str]] = []  # (locale, key, message)

    for locale_path in sorted(all_locales):
        locale = locale_path.name
        try:
            data = load_json(locale_path)
        except Exception as ex:
            issues.append((locale, "<file>", f"Failed to parse JSON: {ex}"))
            continue

        for key in base_keys:
            bv = get_value(base, key)
            tv = get_value(data, key)
            if tv is None:
                issues.append((locale, key, "Missing key"))
                continue
            # If the base value is a string with placeholders, ensure translation preserves them
            if isinstance(bv, str) and isinstance(tv, str):
                bph = set(placeholders_in(bv))
                tph = set(placeholders_in(tv))
                missing_ph = bph - tph
                if missing_ph:
                    issues.append((locale, key, f"Missing placeholders: {', '.join(sorted(missing_ph))}"))

    if issues:
        print("\n❌ Missing translation keys/placeholders detected:\n")
        for locale, key, msg in issues:
            print(f"- [{locale}] {key}: {msg}")
        print("\nTotal issues:", len(issues))
        return 1

    print("✅ All locales contain required keys and placeholders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
