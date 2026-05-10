"""Command-line entrypoint for ReaperX.

Usage:
    reaperx                 # launch web UI on http://127.0.0.1:5000
    reaperx --host 0.0.0.0 --port 8000
    reaperx --debug
"""

from __future__ import annotations

import argparse
import sys

from reaperx import __version__
from reaperx.app import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reaperx",
        description="ReaperX - Ultimate OSINT toolkit (web UI).",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    parser.add_argument("--version", action="version", version=f"ReaperX {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = create_app()
    banner = (
        "\n"
        "  ____                          __  __\n"
        " |  _ \\ ___  __ _ _ __   ___ _ _\\ \\/ /\n"
        " | |_) / _ \\/ _` | '_ \\ / _ \\ '__\\  / \n"
        " |  _ <  __/ (_| | |_) |  __/ |  /  \\ \n"
        " |_| \\_\\___|\\__,_| .__/ \\___|_| /_/\\_\\\n"
        "                 |_|                  \n"
        f"  Ultimate OSINT toolkit  v{__version__}\n"
        f"  Listening on http://{args.host}:{args.port}\n"
    )
    print(banner, file=sys.stderr)
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
