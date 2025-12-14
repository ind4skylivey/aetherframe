#!/usr/bin/env python3
# aetherframe-ecosystem (proprietary) | Fingerprint: AETHERFRAME-FP-2025-098f058124bbcb6891adb2503839273334364898d9414c857aca457235ef0077
# Copyright (c) 2025 ind4skylivey. All Rights Reserved.
# Unauthorized copying, modification, distribution, or sale is strictly prohibited.
"""Generate canonical fingerprint for the aetherframe-ecosystem codebase."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[2]
FINGERPRINT_FILE = ROOT / ".fingerprint"
FIXED_TAG = "AETHERFRAME-FP-2025-098f058124bbcb6891adb2503839273334364898d9414c857aca457235ef0077"
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if parts & EXCLUDE_DIRS:
            continue
        yield path


def _compute_fingerprint(paths: List[Path]) -> str:
    digest = hashlib.sha256()
    for rel_path in sorted(paths):
        rel_str = rel_path.as_posix()
        digest.update(rel_str.encode("utf-8"))
        digest.update(b"\0")
        digest.update(rel_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    paths = [p.relative_to(ROOT) for p in _iter_python_files(ROOT)]
    fingerprint_sha256 = _compute_fingerprint(paths)
    timestamp_utc = (
        _dt.datetime.now(_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    data = {
        "fingerprint_sha256": fingerprint_sha256,
        "fixed_tag": FIXED_TAG,
        "timestamp_utc": timestamp_utc,
        "file_count": len(paths),
    }
    FINGERPRINT_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
