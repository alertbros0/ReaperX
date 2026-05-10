from reaperx.modules import github_user


def test_rejects_empty():
    assert github_user.run("")["error"]
    assert github_user.run("   ")["error"]


def test_strips_at_prefix(monkeypatch):
    """Verify the @ prefix is stripped before being used as the path component."""
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

    monkeypatch.setattr(github_user.requests, "get", fake_get)
    result = github_user.run("@octocat")
    assert "octocat" in captured["url"]
    assert "@octocat" not in captured["url"]
    assert result["found"] is False
