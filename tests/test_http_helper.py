"""Worked example of the offline collector-test pattern.

Copy this recipe for your real collector test:

  1. ``load_json(...)`` a recorded, sanitized response from ``tests/fixtures/``
  2. mock the route with ``respx`` (no live network)
  3. drive the code under test
  4. assert the normalized result — including that failures degrade into ``notes``
"""

from __future__ import annotations

import httpx
import respx

from argus_vendor_example._common import get_json, http_client, unconfigured_note
from tests._fixtures import load_json

BASE = "https://controller.example"


@respx.mock
async def test_get_json_serves_recorded_fixture() -> None:
    payload = load_json("example/devices.json")
    respx.get(f"{BASE}/v1/devices").mock(return_value=httpx.Response(200, json=payload))

    notes: list[str] = []
    async with http_client(BASE, headers={"X-API-KEY": "token"}) as client:
        data = await get_json(client, "/v1/devices", notes=notes)

    assert data is not None
    assert data == payload
    assert [d["name"] for d in data] == ["edge-01", "sw-01"]
    assert notes == []


@respx.mock
async def test_get_json_degrades_errors_into_notes() -> None:
    respx.get(f"{BASE}/v1/devices").mock(return_value=httpx.Response(503))

    notes: list[str] = []
    async with http_client(BASE) as client:
        data = await get_json(client, "/v1/devices", notes=notes)

    assert data is None
    assert any("HTTP 503" in n for n in notes)


def test_unconfigured_note_flags_missing_vars() -> None:
    assert unconfigured_note("demo", ("ARGUS_EXAMPLE_DEFINITELY_UNSET",)) is not None
    assert unconfigured_note("demo", ()) is None
