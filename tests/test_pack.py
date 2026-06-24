"""Tests for the example pack — valid descriptor + graceful unconfigured scan."""

from __future__ import annotations

from argus.discovery.vendors.pack import (
    CLIENTS,
    CONFIG,
    DEVICES,
    TOPOLOGY,
    Transport,
    VendorPack,
)

from argus_vendor_example import EXAMPLE_PACK

#: The capabilities a pack is allowed to advertise (the SPI's declared set).
ALLOWED_CAPABILITIES = frozenset({DEVICES, CLIENTS, TOPOLOGY, CONFIG})


def test_pack_descriptor_is_valid() -> None:
    assert isinstance(EXAMPLE_PACK, VendorPack)
    assert EXAMPLE_PACK.manufacturer
    assert isinstance(EXAMPLE_PACK.transport, Transport)
    assert EXAMPLE_PACK.config_vars
    assert EXAMPLE_PACK.capabilities
    assert EXAMPLE_PACK.capabilities <= ALLOWED_CAPABILITIES


async def test_collect_degrades_when_unconfigured() -> None:
    # With no EXAMPLE_* env vars set, collect() returns an empty result + a note
    # rather than raising — the SPI's degrade-gracefully contract.
    result = await EXAMPLE_PACK.collector().collect()
    assert result.collector == EXAMPLE_PACK.name
    assert result.devices == []
    assert any("not configured" in note for note in result.notes)
