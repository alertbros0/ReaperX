from reaperx.modules import mac_vendor


def test_normalizes_with_separators():
    assert mac_vendor._normalize("00-1A-2B-3C-4D-5E") == "00:1A:2B:3C:4D:5E"
    assert mac_vendor._normalize("00:1a:2b:3c:4d:5e") == "00:1A:2B:3C:4D:5E"
    assert mac_vendor._normalize("001A.2B3C.4D5E") == "00:1A:2B:3C:4D:5E"
    assert mac_vendor._normalize("00 1A 2B 3C 4D 5E") == "00:1A:2B:3C:4D:5E"


def test_normalizes_short_oui():
    assert mac_vendor._normalize("00:1A:2B") == "00:1A:2B"


def test_rejects_too_short():
    assert mac_vendor._normalize("00:1A") is None
    assert mac_vendor._normalize("") is None


def test_rejects_empty_input():
    assert mac_vendor.run("")["error"] == "MAC address required."


def test_rejects_invalid_input():
    out = mac_vendor.run("not a mac")
    assert "error" in out
