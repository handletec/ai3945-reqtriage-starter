from __future__ import annotations

from llm import CopilotLLM


def main() -> int:
    print("Connecting through your signed-in GitHub Copilot account...")

    llm = CopilotLLM()

    response = llm.complete(
        "You are a connection check. Reply with the single word READY.",
        "Confirm that the runtime model connection works.",
    )

    print(f"Model responded: {response.strip()}")
    print("Copilot runtime connection works.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
