from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE_DATA = ROOT / "data" / "packages.json"


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


def main() -> int:
    tracking_id = sys.argv[1] if len(sys.argv) > 1 else "PKG123"
    print(json.dumps(track_package(tracking_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
