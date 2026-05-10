from reaperx.modules import dorks


def test_dorks_returns_engine_links_for_each_template():
    out = dorks.run("alice")
    assert out["query"] == "alice"
    assert out["dorks"], "should generate at least one dork"
    for row in out["dorks"]:
        assert "alice" in row["dork"]
        assert set(row["engines"]) == {"Google", "Bing", "DuckDuckGo"}
        for url in row["engines"].values():
            assert url.startswith("https://")


def test_dorks_rejects_empty_query():
    assert "error" in dorks.run("")
