from reaperx.modules import username


def test_invalid_username_rejected():
    out = username.run("not a valid name!")
    assert "error" in out
    assert out["hits"] == []


def test_load_sites_non_empty():
    sites = username._load_sites()
    assert len(sites) >= 60
    for spec in sites.values():
        assert "url" in spec
        assert "{u}" in spec["url"]
