#!/usr/bin/env python3
# aetherframe-ecosystem (proprietary) | Fingerprint: AETHERFRAME-FP-2025-098f058124bbcb6891adb2503839273334364898d9414c857aca457235ef0077
# Copyright (c) 2025 ind4skylivey. All Rights Reserved.
# Unauthorized copying, modification, distribution, or sale is strictly prohibited.
"""Optional beacon for forensic telemetry when explicitly enabled."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
FINGERPRINT_PATH = ROOT / ".fingerprint"
FIXED_TAG = "AETHERFRAME-FP-2025-098f058124bbcb6891adb2503839273334364898d9414c857aca457235ef0077"
ENV_URL = "SAFE_RECON_BEACON_URL"

def _load_fingerprint() -> Dict[str, Any]:
    try:
        return json.loads(FINGERPRINT_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def send_beacon() -> None:
    url = os.environ.get(ENV_URL)
    if not url:
        return

    fp = _load_fingerprint()
    fallback_ts = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    payload = {
        "fingerprint_sha256": fp.get("fingerprint_sha256"),
        "fixed_tag": fp.get("fixed_tag", FIXED_TAG),
        "timestamp_utc": fp.get("timestamp_utc", fallback_ts),
        "session_id": uuid.uuid4().hex,
        "tool": "aetherframe-ecosystem",
        "purpose": "forensic-telemetry",
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=5):  # nosec B310
            pass
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return


if __name__ == "__main__":
    send_beacon()
