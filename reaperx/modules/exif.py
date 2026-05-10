"""EXIF metadata extraction from uploaded images.

Reads the file via Pillow and returns:
  * Basic image info (size, mode, format)
  * All EXIF tags in human-readable form
  * GPS coordinates as decimal lat/lon when present
"""

from __future__ import annotations

from typing import Any

from PIL import ExifTags, Image, UnidentifiedImageError


def _convert(value: Any) -> Any:
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            return value.hex()
    if isinstance(value, dict):
        return {str(k): _convert(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_convert(v) for v in value]
    return value


def _gps_to_decimal(coords: tuple, ref: str) -> float | None:
    try:
        d, m, s = (float(c) for c in coords)
    except (TypeError, ValueError):
        return None
    decimal = d + (m / 60.0) + (s / 3600.0)
    if ref in ("S", "W"):
        decimal = -decimal
    return round(decimal, 6)


def _gps_block(exif: dict[int, Any]) -> dict[str, Any] | None:
    gps_ifd = exif.get(ExifTags.IFD.GPSInfo) if hasattr(ExifTags, "IFD") else None
    if not gps_ifd:
        # fallback for older Pillow
        gps_ifd = exif.get(34853)
    if not gps_ifd:
        return None

    named = {ExifTags.GPSTAGS.get(k, str(k)): v for k, v in gps_ifd.items()}
    out = {"raw": _convert(named)}
    if {"GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef"} <= named.keys():
        lat = _gps_to_decimal(named["GPSLatitude"], named["GPSLatitudeRef"])
        lon = _gps_to_decimal(named["GPSLongitude"], named["GPSLongitudeRef"])
        if lat is not None and lon is not None:
            out["latitude"] = lat
            out["longitude"] = lon
            out["maps_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
    return out


def run(image_bytes: bytes, filename: str = "uploaded") -> dict[str, Any]:
    if not image_bytes:
        return {"query": filename, "error": "No image provided."}

    try:
        from io import BytesIO

        img = Image.open(BytesIO(image_bytes))
        img.load()
    except UnidentifiedImageError:
        return {"query": filename, "error": "Unsupported or corrupt image."}
    except Exception as exc:
        return {"query": filename, "error": f"Could not read image: {exc}"}

    info = {
        "filename": filename,
        "format": img.format,
        "mode": img.mode,
        "size": list(img.size),
    }

    raw_exif = img.getexif()
    if not raw_exif:
        return {**info, "exif": {}, "gps": None, "note": "No EXIF data present."}

    named: dict[str, Any] = {}
    for tag_id, value in raw_exif.items():
        tag = ExifTags.TAGS.get(tag_id, str(tag_id))
        named[tag] = _convert(value)

    return {**info, "exif": named, "gps": _gps_block(raw_exif)}
