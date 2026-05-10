from io import BytesIO

from PIL import Image

from reaperx.modules import exif


def _make_jpeg() -> bytes:
    img = Image.new("RGB", (40, 30), color=(120, 60, 60))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_exif_no_metadata_image():
    out = exif.run(_make_jpeg(), filename="blank.jpg")
    assert out["format"] == "JPEG"
    assert out["size"] == [40, 30]
    assert out["exif"] == {}


def test_exif_rejects_empty():
    assert "error" in exif.run(b"", filename="x")


def test_exif_rejects_garbage():
    assert "error" in exif.run(b"not-an-image", filename="x")
