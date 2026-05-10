from reaperx.modules import reverse_image


def test_generates_engine_links():
    out = reverse_image.run("https://example.com/photo.jpg")
    assert out["query"] == "https://example.com/photo.jpg"
    assert out["image_host"] == "example.com"
    engines = {e["name"]: e["url"] for e in out["engines"]}
    assert "Google Lens" in engines
    assert "TinEye" in engines
    assert "Yandex Images" in engines
    assert "Bing Images" in engines
    encoded = "https%3A%2F%2Fexample.com%2Fphoto.jpg"
    assert encoded in engines["Google Lens"]
    assert encoded in engines["TinEye"]


def test_rejects_empty_input():
    assert reverse_image.run("")["error"]
    assert reverse_image.run("   ")["error"]


def test_rejects_non_http_url():
    out = reverse_image.run("ftp://example.com/photo.jpg")
    assert "error" in out


def test_rejects_invalid_url():
    out = reverse_image.run("not a url")
    assert "error" in out
