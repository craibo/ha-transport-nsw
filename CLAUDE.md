# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_coordinator.py -v

# Run a single test
pytest tests/test_coordinator.py::test_fetch_departures -v

# Run with coverage
pytest tests/ --cov=custom_components/transport_nsw

# Lint / format
ruff check custom_components/ tests/
black custom_components/ tests/
mypy custom_components/transport_nsw/
```

## Architecture

This is a Home Assistant custom component (HACS-compatible) that surfaces real-time NSW public transport departure data as sensors. It wraps the `PyTransportNSW` library against the Transport NSW Open Data API.

### Dual configuration model

The integration supports two config modes that coexist:

- **Subentry mode** (current): Main config entry holds the API key; individual stops are added as subentries, each with its own `TransportNSWCoordinator`. This is the preferred path for new installs.
- **Legacy mode**: Single stop configured directly on the config entry (no subentries). `coordinator.py` and `sensor.py` both branch on `entry.subentries` to support both.

### Key files

| File | Role |
|---|---|
| `custom_components/transport_nsw/__init__.py` | Entry setup/unload; wires coordinators to config entries |
| `custom_components/transport_nsw/config_flow.py` | Two-step UI: API key validation → stop config (subentry) |
| `custom_components/transport_nsw/coordinator.py` | `TransportNSWCoordinator` — polls API every 60 s, normalises response |
| `custom_components/transport_nsw/sensor.py` | `TransportNSWSensor` — state = minutes until departure; attributes include route, delay, mode, real_time |
| `custom_components/transport_nsw/const.py` | Domain, config keys, attribute names, MDI icon map by transport mode |

### Data flow

Config Entry → Subentry → `TransportNSWCoordinator` (per stop) → `TransportNSWSensor`

The coordinator normalises `"n/a"` strings from the API to `None` before exposing data. The sensor derives its icon dynamically from `coordinator.data["mode"]` using the map in `const.py`.

### Testing conventions

Tests use `pytest-homeassistant-custom-component` for HA test helpers. Fixtures are in `tests/conftest.py`. The `PyTransportNSW` API client is always mocked — never hits the real API in tests. Coverage target is 99%.
