from __future__ import annotations

from llm import AnthropicLLM


def main() -> int:
    llm = AnthropicLLM()

    print(
        "Connecting to Claude "
        f"(model={llm.model}, effort={llm.effort}, max_tokens={llm.max_tokens})..."
    )

    response = llm.complete(
        "You are a connection check. Reply with the single word READY.",
        "Confirm that the runtime model connection works.",
    )

    print(f"Model responded: {response.strip()}")
    print("Claude runtime connection works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
