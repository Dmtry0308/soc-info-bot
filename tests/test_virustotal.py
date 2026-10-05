from app.services.virustotal import detect_ioc_type


def test_detect_ip():
    result = detect_ioc_type("8.8.8.8")

    assert result == "ip"

def test_detect_domain():
    result = detect_ioc_type("example.com")

    assert result == "domain"

def test_detect_SHA_256():
    result = detect_ioc_type("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    assert result == "hash"

def test_detect_SHA_1():
    result = detect_ioc_type("da39a3ee5e6b4b0d3255bfef95601890afd80709")

    assert result == "hash"

def test_detect_MD5():
    result = detect_ioc_type("d41d8cd98f00b204e9800998ecf8427e")

    assert result == "hash"

def test_detect_url():
    result = detect_ioc_type("https://example.com/test")

    assert result == "url"

def test_invalid_ioc():
    result = detect_ioc_type("hello_world")

    assert result is None
