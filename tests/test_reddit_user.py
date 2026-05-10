from reaperx.modules import reddit_user


def test_rejects_empty():
    assert reddit_user.run("")["error"]


def test_strips_prefixes(monkeypatch):
    captured = {}

    class _FakeResp:
        status_code = 404
        ok = False

        def json(self):
            return {}

        def raise_for_status(self):
            pass

    def fake_get(url, **kwargs):  # noqa: ARG001
        captured["url"] = url
        return _FakeResp()

    monkeypatch.setattr(reddit_user.requests, "get", fake_get)
    result = reddit_user.run("u/spez")
    assert "/user/spez/" in captured["url"]
    assert result["found"] is False
