"""Flask web application for ReaperX."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, render_template, request

from reaperx import __version__
from reaperx.modules import (
    doh,
    dorks,
    email,
    exif,
    github_user,
    ip,
    mac_vendor,
    phone,
    reddit_user,
    reverse_image,
    ssl_cert,
    subdomains,
    threat_intel,
    username,
    wayback,
    whois_domain,
)

MAX_UPLOAD_BYTES = 16 * 1024 * 1024  # 16 MB


# Module catalogue. ``category`` groups items in the dashboard + sidebar.
MODULES: dict[str, dict[str, Any]] = {
    "username": {
        "title": "Username Search",
        "blurb": "Find a handle across 60+ public social and dev platforms.",
        "icon": "U",
        "category": "Identity",
        "form_field": {"name": "username", "label": "Username", "placeholder": "octocat"},
    },
    "github_user": {
        "title": "GitHub Recon",
        "blurb": "Public profile, top repos, languages, social links.",
        "icon": "G",
        "category": "Identity",
        "form_field": {"name": "username", "label": "GitHub user", "placeholder": "torvalds"},
    },
    "reddit_user": {
        "title": "Reddit Recon",
        "blurb": "Public profile, karma, recent posts and comments.",
        "icon": "R",
        "category": "Identity",
        "form_field": {"name": "username", "label": "Reddit user", "placeholder": "spez"},
    },
    "email": {
        "title": "Email Recon",
        "blurb": "Validation, MX records, Gravatar, optional HIBP breach check.",
        "icon": "@",
        "category": "Identity",
        "form_field": {"name": "email", "label": "Email", "placeholder": "alice@example.com"},
    },
    "phone": {
        "title": "Phone Number",
        "blurb": "Country, carrier, region, and timezone for a phone number.",
        "icon": "P",
        "category": "Identity",
        "form_field": {"name": "number", "label": "Phone (E.164)", "placeholder": "+14155552671"},
    },
    "domain": {
        "title": "Domain WHOIS & DNS",
        "blurb": "Registrar, ownership, and DNS records for any domain.",
        "icon": "D",
        "category": "Domain & DNS",
        "form_field": {"name": "domain", "label": "Domain", "placeholder": "example.com"},
    },
    "subdomains": {
        "title": "Subdomain Discovery",
        "blurb": "Passive enumeration via crt.sh certificate transparency logs.",
        "icon": "S",
        "category": "Domain & DNS",
        "form_field": {"name": "domain", "label": "Root domain", "placeholder": "example.com"},
    },
    "doh": {
        "title": "DNS over HTTPS",
        "blurb": "Multi-resolver DoH lookup (Cloudflare, Google, Quad9).",
        "icon": "H",
        "category": "Domain & DNS",
        "form_field": {"name": "host", "label": "Hostname", "placeholder": "example.com"},
    },
    "ssl": {
        "title": "SSL Certificate",
        "blurb": "Inspect the X.509 certificate served by a host.",
        "icon": "L",
        "category": "Domain & DNS",
        "form_field": {"name": "host", "label": "Host", "placeholder": "example.com"},
    },
    "ip": {
        "title": "IP Intelligence",
        "blurb": "Geolocation, ASN, reverse DNS, and an interactive map.",
        "icon": "I",
        "category": "Network",
        "form_field": {"name": "target", "label": "IP / hostname", "placeholder": "1.1.1.1"},
    },
    "mac_vendor": {
        "title": "MAC Vendor",
        "blurb": "OUI to vendor lookup via maclookup.app (keyless).",
        "icon": "M",
        "category": "Network",
        "form_field": {"name": "mac", "label": "MAC address", "placeholder": "00:1A:2B:3C:4D:5E"},
    },
    "wayback": {
        "title": "Wayback Machine",
        "blurb": "Historical snapshots of any URL from the Internet Archive.",
        "icon": "W",
        "category": "Web Archive",
        "form_field": {"name": "url", "label": "URL or domain", "placeholder": "example.com"},
    },
    "exif": {
        "title": "Image EXIF",
        "blurb": "Extract camera, software, and GPS metadata from an image.",
        "icon": "E",
        "category": "Files",
        "form_field": {"name": "image", "label": "Image file", "type": "file"},
    },
    "reverse_image": {
        "title": "Reverse Image Search",
        "blurb": "Generate Google Lens / TinEye / Yandex / Bing search links.",
        "icon": "V",
        "category": "Files",
        "form_field": {"name": "url", "label": "Image URL", "placeholder": "https://…/photo.jpg"},
    },
    "dorks": {
        "title": "Search Dorks",
        "blurb": "Generate Google/Bing/DuckDuckGo OSINT pivots for a target.",
        "icon": "Q",
        "category": "Search",
        "form_field": {"name": "query", "label": "Target", "placeholder": "John Doe"},
    },
    "threat_intel": {
        "title": "Threat Intel",
        "blurb": "urlscan.io history + verification links (VT, AbuseIPDB, URLhaus…).",
        "icon": "T",
        "category": "Search",
        "form_field": {"name": "target", "label": "URL / domain / IP", "placeholder": "1.1.1.1"},
    },
}


def _grouped_modules() -> list[dict[str, Any]]:
    """Return modules grouped by category, preserving insertion order."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for key, meta in MODULES.items():
        cat = meta.get("category", "Other")
        groups.setdefault(cat, []).append({"key": key, **meta})
    return [{"name": cat, "modules": items} for cat, items in groups.items()]


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.context_processor
    def _inject_globals() -> dict[str, Any]:
        return {
            "modules": MODULES,
            "module_groups": _grouped_modules(),
            "app_version": __version__,
        }

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/module/<key>")
    def module_page(key: str) -> str:
        if key not in MODULES:
            return render_template("not_found.html"), 404  # type: ignore[return-value]
        return render_template("module.html", key=key, module=MODULES[key])

    # ---- API endpoints --------------------------------------------------

    @app.post("/api/username")
    def api_username() -> Any:
        return jsonify(username.run(request.form.get("username", "").strip()))

    @app.post("/api/github_user")
    def api_github_user() -> Any:
        return jsonify(github_user.run(request.form.get("username", "").strip()))

    @app.post("/api/reddit_user")
    def api_reddit_user() -> Any:
        return jsonify(reddit_user.run(request.form.get("username", "").strip()))

    @app.post("/api/domain")
    def api_domain() -> Any:
        return jsonify(whois_domain.run(request.form.get("domain", "").strip()))

    @app.post("/api/ip")
    def api_ip() -> Any:
        return jsonify(ip.run(request.form.get("target", "").strip()))

    @app.post("/api/mac_vendor")
    def api_mac_vendor() -> Any:
        return jsonify(mac_vendor.run(request.form.get("mac", "").strip()))

    @app.post("/api/email")
    def api_email() -> Any:
        return jsonify(email.run(request.form.get("email", "").strip()))

    @app.post("/api/phone")
    def api_phone() -> Any:
        return jsonify(
            phone.run(
                request.form.get("number", "").strip(),
                request.form.get("region") or None,
            )
        )

    @app.post("/api/exif")
    def api_exif() -> Any:
        f = request.files.get("image")
        if not f:
            return jsonify({"error": "No image uploaded."}), 400
        return jsonify(exif.run(f.read(), filename=f.filename or "uploaded"))

    @app.post("/api/reverse_image")
    def api_reverse_image() -> Any:
        return jsonify(reverse_image.run(request.form.get("url", "").strip()))

    @app.post("/api/subdomains")
    def api_subdomains() -> Any:
        return jsonify(subdomains.run(request.form.get("domain", "").strip()))

    @app.post("/api/doh")
    def api_doh() -> Any:
        return jsonify(doh.run(request.form.get("host", "").strip()))

    @app.post("/api/wayback")
    def api_wayback() -> Any:
        return jsonify(wayback.run(request.form.get("url", "").strip()))

    @app.post("/api/ssl")
    def api_ssl() -> Any:
        host = request.form.get("host", "").strip()
        try:
            port = int(request.form.get("port", "443"))
        except ValueError:
            port = 443
        return jsonify(ssl_cert.run(host, port))

    @app.post("/api/dorks")
    def api_dorks() -> Any:
        return jsonify(dorks.run(request.form.get("query", "").strip()))

    @app.post("/api/threat_intel")
    def api_threat_intel() -> Any:
        return jsonify(threat_intel.run(request.form.get("target", "").strip()))

    @app.get("/healthz")
    def healthz() -> Any:
        return jsonify({"ok": True, "version": __version__, "modules": len(MODULES)})

    return app
