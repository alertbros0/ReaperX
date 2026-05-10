---
name: reaperx-dev-and-testing
description: How to set up, lint, test, and end-to-end exercise the ReaperX Flask web app. Trigger when working on any module under reaperx/, the Flask app, templates/static assets, or the test suite.
---

# ReaperX dev & testing

## Install (one-time)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

The blueprint already runs the venv + editable install during snapshot build, so in a fresh Devin session you usually only need `. .venv/bin/activate`.

## Lint and unit tests

```bash
. .venv/bin/activate
ruff check .
pytest -q
```

There are 26 unit tests covering dorks, phone, exif, username, and Flask routes for every module. CI runs the same pair on Python 3.10/3.11/3.12.

## Run the web UI locally

```bash
. .venv/bin/activate
reaperx --host 127.0.0.1 --port 5050
```

- `GET /` → dashboard with all 10 modules
- `GET /module/<key>` → module page (keys: `username`, `domain`, `ip`, `email`, `phone`, `exif`, `subdomains`, `wayback`, `ssl`, `dorks`)
- `POST /api/<key>` → JSON API for each module
- `GET /healthz` → `{"ok": true, "version": ...}`

## Deterministic E2E test fixtures

Use these inputs whenever the test must produce **exact, repeatable** output (no rate-limited external calls):

| Module | Input | Expected highlights |
| --- | --- | --- |
| Phone Number | `+14155552671` | region=US, location=San Francisco CA, timezones=America/Los_Angeles |
| Search Dorks | `AlertBros` | 13 templated rows, each with Google/Bing/DuckDuckGo links |
| SSL Certificate | `github.com` (port 443) | SAN list contains `github.com`, `is_expired=false`, `expires_in_days > 0` |
| Image EXIF | a 40x30 RGB JPEG (see `tests/test_exif.py`) | format=JPEG, exif={} |

## Optional API keys

- `HIBP_API_KEY` — unlocks Have-I-Been-Pwned breach lookup in the Email Recon module. Without it, the module returns a `note: "Set HIBP_API_KEY..."` payload, which is fine for normal testing. Do not request this key unless the user explicitly asks to exercise the breach path.

## Adding a new OSINT module

1. Create `reaperx/modules/<name>.py` exposing `def run(...) -> dict`.
2. Re-export it in `reaperx/modules/__init__.py`.
3. Register the module metadata in `MODULES` in `reaperx/app.py` and add an `@app.post("/api/<name>")` endpoint.
4. Add a custom renderer in `reaperx/static/reaperx.js` under the `renderers` map (optional — falls back to a generic key/value list).
5. Add unit tests under `tests/test_<name>.py`.

## Known UX nit

The JS renderer (`reaperx/static/reaperx.js`) paints every boolean `false` red and every `true` green. That's correct for `is_valid` but inverted for fields like `is_expired`. If you touch the renderer, prefer making boolean colour neutral by default and adding an explicit allow-list for fields where `true` = good.
