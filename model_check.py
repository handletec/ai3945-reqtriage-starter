from __future__ import annotations

from dotenv import load_dotenv

from llm import AnthropicLLM


def main() -> int:
    load_dotenv()

    print("Connecting to runtime model...")

    llm = AnthropicLLM()

    response = llm.complete(
        "You are a connection check. Reply with the single word READY.",
        "Confirm that the model connection works.",
    )

    print(f"Model responded: {response.strip()}")
    print("Real-model connection works.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
