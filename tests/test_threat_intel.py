from reaperx.modules import threat_intel


def test_classifies_ip():
    assert threat_intel._classify("8.8.8.8") == "ip"
    assert threat_intel._classify("2001:4860:4860::8888") == "ip"


def test_classifies_domain():
    assert threat_intel._classify("example.com") == "domain"
    assert threat_intel._classify("sub.example.co.uk") == "domain"


def test_classifies_url():
    assert threat_intel._classify("https://example.com/path") == "url"
    assert threat_intel._classify("http://example.com") == "url"


def test_classifies_unknown():
    assert threat_intel._classify("not a thing") == "unknown"


def test_verification_links_for_ip():
    links = threat_intel._verification_links("8.8.8.8", "ip")
    assert "VirusTotal" in links
    assert "AbuseIPDB" in links
    assert "Shodan" in links
    assert "8.8.8.8" in links["VirusTotal"]


def test_verification_links_for_domain():
    links = threat_intel._verification_links("example.com", "domain")
    assert "URLhaus" in links
    assert "crt.sh" in links


def test_rejects_empty():
    out = threat_intel.run("")
    assert out["error"]


def test_rejects_unclassifiable():
    out = threat_intel.run("nothing-ish")
    assert "error" in out
