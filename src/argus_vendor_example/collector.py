"""Example collector skeleton — implement ``collect()`` against your vendor's API/protocol.

Collectors are READ-ONLY against the network: the only writes Argus makes are into NetBox,
via the reconcile engine. Return a normalized :class:`DiscoveryResult`.
"""

from __future__ import annotations

from argus.discovery.base import Collector, DiscoveredDevice, DiscoveryResult

from ._common import get_json, http_client, unconfigured_note
from .models import MANUFACTURER, role_from_model

#: Env vars this pack consumes. Referenced by the VendorPack descriptor in __init__.py.
CONFIG_VARS = ("EXAMPLE_URL", "EXAMPLE_API_TOKEN")


class ExampleCollector(Collector):
    name = "example"

    async def collect(self) -> DiscoveryResult:
        result = DiscoveryResult(collector=self.name)

        # 1) Guard the unconfigured case so a scan degrades gracefully (never raise).
        if note := unconfigured_note(self.name, CONFIG_VARS):
            result.notes.append(note)
            return result

        # 2) Call your vendor API (read-only) with the shared helper. Read your config
        #    from argus's settings (`from argus.config import get_settings`) or your own env:
        #
        #        settings = get_settings()
        #        async with http_client(
        #            settings.example_url,
        #            headers={"Authorization": f"Bearer {settings.example_api_token}"},
        #        ) as client:
        #            devices = await get_json(client, "/v1/devices", notes=result.notes) or []
        #
        # 3) Normalize each device:
        #
        #        for d in devices:
        #            result.devices.append(DiscoveredDevice(
        #                name=d["name"], mac=d.get("mac"), primary_ip=d.get("ip"),
        #                role=role_from_model(d.get("model")), model=d.get("model"),
        #                manufacturer=MANUFACTURER, raw=d,
        #            ))
        #    DiscoveredDevice also accepts optional `site=` and a read-only
        #    `management=DeviceManagement(...)` (management-plane data, ADR-0010).
        #    Optionally populate result.clients / result.links / result.ip_addresses.

        # Referenced by the implementation sketch above (remove once implemented):
        _ = (DiscoveredDevice, MANUFACTURER, role_from_model, get_json, http_client)
        result.notes.append("example vendor pack template — implement ExampleCollector.collect().")
        return result
