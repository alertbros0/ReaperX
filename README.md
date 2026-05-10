# ReaperX

> An OSINT toolkit with a polished web interface — built for investigators,
> journalists, and security researchers.

ReaperX exposes a focused set of OSINT pivots through a single Flask web app:

| Module | What it does |
| --- | --- |
| **Username Search** | Checks 25+ public social/dev platforms in parallel. |
| **Domain WHOIS & DNS** | Registrar, dates, name servers + A / AAAA / MX / NS / TXT / CNAME / SOA records. |
| **IP Intelligence** | Geolocation, ASN, organisation, reverse DNS via the keyless `ip-api.com` endpoint. |
| **Email Recon** | Validation, MX-record check, Gravatar lookup, optional Have-I-Been-Pwned breach check. |
| **Phone Number** | Country, region, carrier, timezones via `phonenumbers` (offline). |
| **Image EXIF** | Camera, software, and GPS metadata extraction (with map link). |
| **Subdomain Discovery** | Passive enumeration via the [crt.sh](https://crt.sh) certificate-transparency log. |
| **Wayback Machine** | Historical snapshots from the Internet Archive's CDX API. |
| **SSL Certificate** | Subject/issuer, validity, SANs, signature algo for any TLS host. |
| **Search Dorks** | Generates Google / Bing / DuckDuckGo OSINT pivots. |

> **Scope.** ReaperX only consumes **publicly available** information. It does
> not log into anything, bypass paywalls, harvest credentials, or perform any
> active exploitation. Use it lawfully.

## Quick start

```bash
git clone https://github.com/alertbros0/ReaperX.git
cd ReaperX
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

reaperx                      # http://127.0.0.1:5000
reaperx --host 0.0.0.0 --port 8000
reaperx --debug
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Optional API keys

Set these in your environment to unlock additional functionality:

| Env var | Used by | Notes |
| --- | --- | --- |
| `HIBP_API_KEY` | Email recon | Required for breach lookups via Have-I-Been-Pwned. |

## Development

```bash
pip install -e ".[dev]"

# lint + format
ruff check .
ruff format .

# tests
pytest
```

## Project layout

```
reaperx/
  app.py            # Flask application factory + routes
  cli.py            # `reaperx` CLI entrypoint
  modules/          # one self-contained module per OSINT pivot
  templates/        # Jinja2 templates (dark UI)
  static/           # CSS + JS
  data/sites.json   # site list for username search
tests/              # pytest suite
```

Each module exposes a single `run(...)` function returning a JSON-serialisable
dict, so it is trivial to embed in scripts or other tools:

```python
from reaperx.modules import phone
print(phone.run("+14155552671"))
```

## Disclaimer

ReaperX is a tool. Its operator is responsible for using it within the bounds
of applicable law, the targeted services' terms of service, and ethical norms
of OSINT research.

## License

MIT — see [LICENSE](./LICENSE).
