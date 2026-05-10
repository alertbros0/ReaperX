# ReaperX

> An OSINT toolkit with a polished web interface — built for investigators,
> journalists, and security researchers.

ReaperX exposes 16 OSINT pivots across 6 categories through a single Flask web app:

### Identity
| Module | What it does |
| --- | --- |
| **Username Search** | Checks 60+ public social/dev platforms in parallel. |
| **GitHub Recon** | Public profile, top repos, stars/forks, languages, social links. |
| **Reddit Recon** | Public profile, karma, recent posts and comments. |
| **Email Recon** | Validation, MX-record check, Gravatar lookup, optional HIBP breach check. |
| **Phone Number** | Country, region, carrier, timezones via `phonenumbers` (offline). |

### Domain & DNS
| Module | What it does |
| --- | --- |
| **Domain WHOIS & DNS** | Registrar, dates, name servers + A / AAAA / MX / NS / TXT / CNAME / SOA records. |
| **Subdomain Discovery** | Passive enumeration via the [crt.sh](https://crt.sh) certificate-transparency log. |
| **DNS over HTTPS** | Multi-resolver DoH lookups (Cloudflare 1.1.1.1, Google 8.8.8.8, Quad9). |
| **SSL Certificate** | Subject/issuer, validity, SANs, signature algo for any TLS host. |

### Network
| Module | What it does |
| --- | --- |
| **IP Intelligence** | Geolocation, ASN, reverse DNS, and an interactive OpenStreetMap embed. |
| **MAC Vendor** | OUI to vendor lookup via the keyless [maclookup.app](https://maclookup.app) API. |

### Web Archive
| Module | What it does |
| --- | --- |
| **Wayback Machine** | Historical snapshots from the Internet Archive's CDX API. |

### Files
| Module | What it does |
| --- | --- |
| **Image EXIF** | Camera, software, and GPS metadata extraction (with map link). |
| **Reverse Image Search** | Generates Google Lens / TinEye / Yandex / Bing / SauceNAO / IQDB / Karma Decay search links. |

### Search
| Module | What it does |
| --- | --- |
| **Search Dorks** | Generates Google / Bing / DuckDuckGo OSINT pivots. |
| **Threat Intel** | urlscan.io history + verification links to VirusTotal, AbuseIPDB, URLhaus, Shodan, Censys, etc. |

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
