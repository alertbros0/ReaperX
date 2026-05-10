import pytest

from reaperx.app import MODULES, create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "ReaperX" in body
    for m in MODULES.values():
        # Jinja2 escapes &, so compare against the escaped form
        assert m["title"].replace("&", "&amp;") in body


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert "version" in payload


@pytest.mark.parametrize("key", list(MODULES.keys()))
def test_module_pages_render(client, key):
    resp = client.get(f"/module/{key}")
    assert resp.status_code == 200
    title = MODULES[key]["title"].replace("&", "&amp;")
    assert title in resp.get_data(as_text=True)


def test_unknown_module_404(client):
    resp = client.get("/module/does-not-exist")
    assert resp.status_code == 404


def test_dorks_api(client):
    resp = client.post("/api/dorks", data={"query": "alice"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["query"] == "alice"
    assert data["dorks"]


def test_phone_api(client):
    resp = client.post("/api/phone", data={"number": "+14155552671"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["is_valid"] is True


def test_exif_api_requires_file(client):
    resp = client.post("/api/exif", data={})
    assert resp.status_code == 400
