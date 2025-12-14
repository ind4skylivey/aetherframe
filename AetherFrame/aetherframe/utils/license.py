"""License enforcement utilities."""

from __future__ import annotations

import os
from functools import lru_cache
from base64 import b64decode
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import HTTPException

from aetherframe.utils.config import get_settings

# Public key (ed25519) for offline-signed tokens; private key is kept by owner.
LICENSE_PUBLIC_KEY_B64 = "QM+4R8A7XJX5fnq7Xn5N0v+zJ8Y1v7kSxV8E/dVkx1E="
LICENSE_MESSAGE = b"AETHERFRAME_LICENSE"


@lru_cache()
def _public_key() -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(b64decode(LICENSE_PUBLIC_KEY_B64))


def verify_token(token: str) -> Tuple[bool, str]:
    """Verify a base64-encoded ed25519 signature token."""
    try:
        signature = b64decode(token)
        _public_key().verify(signature, LICENSE_MESSAGE)
        return True, "ok"
    except Exception as exc:  # pragma: no cover
        return False, f"invalid signature ({exc})"


def check_license() -> Tuple[bool, str]:
    """Return (ok, reason)."""
    settings = get_settings()
    print(f"DEBUG: env={settings.environment}, enforce={settings.license_enforce}, token={os.getenv('AETHERFRAME_LICENSE_TOKEN')}", flush=True)
    if settings.environment.lower() == "test":
        return True, "test bypass"
    if not settings.license_enforce:
        return True, "enforcement disabled"
    token = os.getenv("AETHERFRAME_LICENSE_TOKEN")
    if not token:
        return False, "missing token"
    return verify_token(token)


def enforce_or_raise():
    ok, reason = check_license()
    if not ok:
        raise HTTPException(status_code=402, detail=f"License required: {reason}")


def enforce_or_fail_worker():
    ok, reason = check_license()
    if not ok:
        raise RuntimeError(f"License required: {reason}")
