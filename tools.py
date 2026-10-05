from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE_DATA = ROOT / "data" / "packages.json"
DEPOT_DATA = ROOT / "data" / "depots.json"


def track_package(tracking_id: str, data_path: Path = PACKAGE_DATA) -> dict:
    """Read one package status from synthetic local data."""

    packages = json.loads(data_path.read_text(encoding="utf-8"))
    package = packages.get(tracking_id)

    if package is None:
        return {
            "found": False,
            "tracking_id": tracking_id,
        }

    return {
        "found": True,
        "tracking_id": tracking_id,
        **package,
    }


def get_depot_info(depot_name: str, data_path: Path = DEPOT_DATA) -> dict:
    """Read collection information for one synthetic depot."""

    depots = json.loads(data_path.read_text(encoding="utf-8"))
    depot = depots.get(depot_name)

    if depot is None:
        return {
            "found": False,
            "depot_name": depot_name,
        }

    return {
        "found": True,
        "depot_name": depot_name,
        **depot,
    }


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "depot":
        print(json.dumps(get_depot_info(sys.argv[2]), indent=2))
        return 0

    tracking_id = sys.argv[1] if len(sys.argv) > 1 else "PKG123"
    print(json.dumps(track_package(tracking_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
