# Argus vendor pack template

A minimal, copy-to-start **out-of-tree vendor pack** for
[Argus](https://github.com/freed-dev-llc/argus). Use it to add support for a
vendor/technology without modifying Argus itself — in your own repo, **public or private**.

> **This is a GitHub template repository.** Click **“Use this template”** above to create
> your own pack repo, then follow [Use it](#use-it).

It is structured like Argus's built-in vendor packs, and is how private (e.g.
MSP-supported) vendor packs attach: Argus is the **host**, your pack is a **plugin**
discovered via the `argus.vendor_packs` entry point — Argus never needs to know your pack
exists at build time. Vendor *practices* and read-only management-plane data are optional,
separately-added capabilities (ADR-0009 / ADR-0010); a pack works fine without them. See Argus
[ADR-0005](https://github.com/freed-dev-llc/argus/blob/main/docs/architecture/adr/0005-vendor-packs.md).

## What a pack is

A `VendorPack` bundles, for one vendor:

- a **`Collector`** — the read-only adapter that observes live state and returns a
  normalized `DiscoveryResult` (devices / clients / links / ip_addresses / notes);
- **metadata** — `manufacturer`, `transport`, `capabilities`, and the `config_vars` it
  consumes;
- **model normalization** — vendor model strings → NetBox role / manufacturer.

The public SPI it builds against ships in the `argus-netbox` distribution:
`argus.discovery.base` (`Collector`, `DiscoveryResult`, `Discovered*`),
`argus.discovery.vendors.pack` (`VendorPack`, `Transport`, capability constants), and the
optional `argus.discovery.practices` (vendor-practices SPI, ADR-0009).

**Practices & management (optional).** A pack may publish reusable practices via
`argus.discovery.practices` (ADR-0009) and attach read-only management-plane data through a
`DeviceManagement` on each discovered device (ADR-0010); both are optional add-ons that a
basic pack can skip. See the upstream
[vendor-pack guide](https://github.com/freed-dev-llc/argus/blob/main/docs/VENDOR_PACKS.md).

## Use it

1. **Use this template** (or copy this repo) and rename `argus_vendor_example` → your vendor.
2. **Implement** `Collector.collect()` in `collector.py` against your vendor's API/protocol
   (keep it read-only), and fill in `models.py`.
3. **Describe** the pack in `__init__.py` (`VendorPack(...)`).
4. **Register** it via the entry point in `pyproject.toml`:

   ```toml
   [project.entry-points."argus.vendor_packs"]
   yourvendor = "your_package:YOUR_PACK"
   ```

5. **Install** it alongside Argus and confirm it registers:

   ```bash
   pip install -e .
   python -c "from argus.discovery.vendors import discover_packs; print(sorted(discover_packs()))"
   # -> [..., 'example', 'unifi']
   ```

Once registered, your pack's `name` is selectable everywhere a collector is (the
`discovery_scan` / `network_topology` / reconcile tools, `SCHEDULE_COLLECTOR`, etc.).

## Develop

The template ships dev tooling, CI, and an **offline** test harness so your pack starts
from a passing baseline:

```bash
pip install -e ".[dev]"     # pulls argus-netbox (the SPI) from PyPI
ruff check src tests && mypy src && pytest -q
```

- `src/argus_vendor_example/_common.py` — a shared async-HTTP collector helper (auth'd
  client + a JSON GET that degrades HTTP/transport/JSON errors into
  `DiscoveryResult.notes`, plus an `unconfigured_note()` guard). Your `collect()` becomes
  just *auth + endpoints + normalization*.
- `tests/` — a recorded-fixture harness (`tests/_fixtures.py` loader + `tests/fixtures/`)
  with a worked example (`tests/test_http_helper.py`); tests run fully offline via `respx`.
- `.github/workflows/ci.yml` — runs ruff + mypy + pytest on every push/PR.

See the upstream [vendor-pack guide](https://github.com/freed-dev-llc/argus/blob/main/docs/VENDOR_PACKS.md)
for the full contract.

## Private packs

Nothing here has to be public. A private pack lives in a private repo, depends on the
public `argus-netbox`, and is installed into your Argus deployment from a private index or
`git+ssh`. Argus is Apache-2.0 (permissive), and this template is too — your derived pack's
source stays yours to license however you like, including closed.
