"""Redacted live smoke test for the Qloo hackathon API.

The script deliberately prints only status and JSON shape. It never prints the
API key or raw recommendation payloads, so it is safe to run in a terminal log.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow the documented direct invocation from the project root without asking
# users to alter PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tastetrail.qloo import QlooClient, QlooError


def _shape(payload: object) -> str:
    if not isinstance(payload, dict):
        return type(payload).__name__
    keys = sorted(str(key) for key in payload.keys())[:20]
    return f"object(keys={keys})"


def main() -> int:
    if not os.getenv("QLOO_API_KEY"):
        print("FAIL: QLOO_API_KEY is not configured (the value is never printed).")
        return 2
    base = os.getenv("QLOO_API_BASE", "https://hackathon.api.qloo.com").rstrip("/")
    if base != "https://hackathon.api.qloo.com":
        print(f"FAIL: QLOO_API_BASE must be https://hackathon.api.qloo.com, got {base!r}")
        return 2

    client = QlooClient(base_url=base, timeout=20)
    try:
        search = client.search_entity("jazz", take=5)
        print(f"PASS: /search reachable at {base}; {_shape(search)}")
        print("NEXT: if this passes, run the local UI and verify a real Jaipur request.")
        return 0
    except QlooError as exc:
        print(f"FAIL: Qloo request failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

