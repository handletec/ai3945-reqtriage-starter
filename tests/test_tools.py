from tools import get_depot_info, track_package


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


def test_known_depot_is_returned():
    result = get_depot_info("Penang depot")

    assert result["found"] is True
    assert result["depot_name"] == "Penang depot"
    assert result["collection_allowed"] is True


def test_unknown_depot_is_a_normal_miss():
    result = get_depot_info("Unknown depot")

    assert result == {
        "found": False,
        "depot_name": "Unknown depot",
    }
