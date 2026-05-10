"""Flask web application for ReaperX."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, render_template, request

from reaperx import __version__
from reaperx.modules import (
    dorks,
    email,
    exif,
    ip,
    phone,
    ssl_cert,
    subdomains,
    username,
    wayback,
    whois_domain,
)

MAX_UPLOAD_BYTES = 16 * 1024 * 1024  # 16 MB


MODULES: dict[str, dict[str, Any]] = {
    "username": {
        "title": "Username Search",
        "blurb": "Find a handle across 25+ public social and dev platforms.",
        "icon": "user",
        "form_field": {"name": "username", "label": "Username", "placeholder": "octocat"},
    },
    "domain": {
        "title": "Domain WHOIS & DNS",
        "blurb": "Registrar, ownership, and DNS records for any domain.",
        "icon": "globe",
        "form_field": {"name": "domain", "label": "Domain", "placeholder": "example.com"},
    },
    "ip": {
        "title": "IP Intelligence",
        "blurb": "Geolocation, ASN, and reverse DNS for an IP or hostname.",
        "icon": "map-pin",
        "form_field": {"name": "target", "label": "IP / hostname", "placeholder": "1.1.1.1"},
    },
    "email": {
        "title": "Email Recon",
        "blurb": "Validation, MX records, Gravatar, optional HIBP breach check.",
        "icon": "mail",
        "form_field": {"name": "email", "label": "Email", "placeholder": "alice@example.com"},
    },
    "phone": {
        "title": "Phone Number",
        "blurb": "Country, carrier, region, and timezone for a phone number.",
        "icon": "phone",
        "form_field": {"name": "number", "label": "Phone (E.164)", "placeholder": "+14155552671"},
    },
    "exif": {
        "title": "Image EXIF",
        "blurb": "Extract camera, software, and GPS metadata from an image.",
        "icon": "image",
        "form_field": {"name": "image", "label": "Image file", "type": "file"},
    },
    "subdomains": {
        "title": "Subdomain Discovery",
        "blurb": "Passive enumeration via crt.sh certificate transparency logs.",
        "icon": "git-branch",
        "form_field": {"name": "domain", "label": "Root domain", "placeholder": "example.com"},
    },
    "wayback": {
        "title": "Wayback Machine",
        "blurb": "Historical snapshots of any URL from the Internet Archive.",
        "icon": "clock",
        "form_field": {"name": "url", "label": "URL or domain", "placeholder": "example.com"},
    },
    "ssl": {
        "title": "SSL Certificate",
        "blurb": "Inspect the X.509 certificate served by a host.",
        "icon": "lock",
        "form_field": {"name": "host", "label": "Host", "placeholder": "example.com"},
    },
    "dorks": {
        "title": "Search Dorks",
        "blurb": "Generate Google/Bing/DuckDuckGo OSINT pivots for a target.",
        "icon": "search",
        "form_field": {"name": "query", "label": "Target", "placeholder": "John Doe"},
    },
}


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.context_processor
    def _inject_globals() -> dict[str, Any]:
        return {"modules": MODULES, "app_version": __version__}

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

    @app.post("/api/domain")
    def api_domain() -> Any:
        return jsonify(whois_domain.run(request.form.get("domain", "").strip()))

    @app.post("/api/ip")
    def api_ip() -> Any:
        return jsonify(ip.run(request.form.get("target", "").strip()))

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

    @app.post("/api/subdomains")
    def api_subdomains() -> Any:
        return jsonify(subdomains.run(request.form.get("domain", "").strip()))

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

    @app.get("/healthz")
    def healthz() -> Any:
        return jsonify({"ok": True, "version": __version__})

    return app
