"""Shared helpers for vendor-pack collectors.

Controller-API collectors all repeat the same mechanics: an authenticated async HTTP
client, JSON GETs that tolerate failure, and the discovery SPI's *degrade-gracefully*
contract — errors become :attr:`DiscoveryResult.notes` and a partial result is
returned, **never** an exception. Centralising that here keeps each collector to just
*auth + endpoints + normalization*. See ``collector.py`` for usage.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx

#: Default per-request timeout (seconds) for vendor controller APIs.
DEFAULT_TIMEOUT = 30.0


@asynccontextmanager
async def http_client(
    base_url: str,
    *,
    headers: dict[str, str] | None = None,
    verify: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """An async ``httpx`` client scoped to one vendor controller.

    ``base_url`` is normalised (trailing slash stripped) so callers pass relative,
    leading-slash paths (``"/v1/devices"``) to :func:`get_json`.
    """
    async with httpx.AsyncClient(
        base_url=base_url.rstrip("/"),
        headers=headers or {},
        verify=verify,
        timeout=timeout,
    ) as client:
        yield client


async def get_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    notes: list[str],
    params: dict[str, Any] | None = None,
) -> Any | None:
    """GET ``url`` and parse JSON, tolerating failure.

    On any HTTP status, transport, or decode error this appends a short message to
    ``notes`` and returns ``None`` — so the caller can keep collecting and return a
    partial :class:`DiscoveryResult` rather than raising (the SPI contract).
    """
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        notes.append(f"{url} -> HTTP {exc.response.status_code}")
    except httpx.HTTPError as exc:
        notes.append(f"{url} -> request failed: {type(exc).__name__}")
    except ValueError:
        notes.append(f"{url} -> invalid JSON")
    return None


def unconfigured_note(pack_name: str, config_vars: tuple[str, ...]) -> str | None:
    """Return a ``"not configured"`` note if any ``config_vars`` env var is unset.

    Returns ``None`` when everything is set, so a collector can do::

        if note := unconfigured_note(self.name, CONFIG_VARS):
            result.notes.append(note)
            return result
    """
    missing = [v for v in config_vars if not os.environ.get(v)]
    if missing:
        return f"{pack_name} pack not configured: set {', '.join(missing)}."
    return None
