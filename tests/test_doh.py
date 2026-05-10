from reaperx.modules import doh


def test_resolvers_constants():
    assert "Cloudflare (1.1.1.1)" in doh.RESOLVERS
    assert "Google (8.8.8.8)" in doh.RESOLVERS
    assert "Quad9 (9.9.9.9)" in doh.RESOLVERS
    assert "A" in doh.RECORD_TYPES
    assert "AAAA" in doh.RECORD_TYPES
    assert "MX" in doh.RECORD_TYPES


def test_rejects_empty():
    assert doh.run("")["error"]
    assert doh.run("   ")["error"]
