from __future__ import annotations

import os

from anthropic import Anthropic


def main() -> int:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    page = client.models.list(limit=100)

    print("Models available to this Anthropic API key:\n")

    for model in page.data:
        display_name = getattr(model, "display_name", "")
        suffix = f" — {display_name}" if display_name else ""
        print(f"{model.id}{suffix}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
