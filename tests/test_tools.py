from tools import track_package


def test_known_package_is_returned():
    result = track_package("PKG123")

    assert result["found"] is True
    assert result["tracking_id"] == "PKG123"
    assert result["status"] == "Delayed"


def test_unknown_package_is_a_normal_miss():
    result = track_package("DOES-NOT-EXIST")

    assert result == {
        "found": False,
        "tracking_id": "DOES-NOT-EXIST",
    }
