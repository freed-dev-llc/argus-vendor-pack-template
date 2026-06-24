"""Recorded-response fixture loader for offline collector tests.

The canonical pattern: store real, **sanitized** vendor API responses under
``tests/fixtures/<pack>/<endpoint>.json``, serve them through ``respx`` in a test, and
assert the collector's normalization. This avoids any live network call while testing
against realistic payloads.

    from tests._fixtures import load_json
    payload = load_json("example/devices.json")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Root of the recorded-response fixtures tree.
FIXTURES = Path(__file__).parent / "fixtures"


def load_json(relpath: str) -> Any:
    """Load a recorded JSON fixture, e.g. ``load_json("example/devices.json")``."""
    return json.loads((FIXTURES / relpath).read_text())
