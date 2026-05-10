from reaperx.modules import phone


def test_valid_us_number():
    out = phone.run("+14155552671")
    assert out["is_valid"] is True
    assert out["country_code"] == 1
    assert out["region"] == "US"
    assert out["e164"] == "+14155552671"


def test_invalid_input_returns_error():
    out = phone.run("not-a-phone")
    assert "error" in out


def test_empty_input_returns_error():
    assert "error" in phone.run("")
