from __future__ import annotations

import json
from pathlib import Path


def track_package(tracking_id: str, data_path: Path) -> dict:
    """Read one package status from local synthetic data."""

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
