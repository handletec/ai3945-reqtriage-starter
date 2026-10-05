from __future__ import annotations

import json

from agent import run_agent
from tools import get_depot_info


class ScriptedLLM:
    def __init__(self, responses: list[dict]) -> None:
        self.responses = [json.dumps(item) for item in responses]
        self.index = 0

    def complete(self, system: str, user: str) -> str:
        response = self.responses[self.index]
        self.index += 1
        return response


def check_l2_still_works() -> None:
    llm = ScriptedLLM([
        {
            "action": "call_tool",
            "tool": "track_package",
            "arguments": {"tracking_id": "PKG123"},
        },
        {
            "action": "final",
            "answer": "PKG123 is delayed at the Penang depot.",
        },
    ])

    result = run_agent("Where is PKG123?", llm, level="l2")

    assert result["status"] == "completed"
    assert result["level"] == "L2"
    assert result["model_turns"] == 2
    assert result["tool_actions"] == 1


def check_l3_two_actions() -> None:
    llm = ScriptedLLM([
        {
            "action": "call_tool",
            "tool": "track_package",
            "arguments": {"tracking_id": "PKG123"},
        },
        {
            "action": "call_tool",
            "tool": "get_depot_info",
            "arguments": {"depot_name": "Penang depot"},
        },
        {
            "action": "final",
            "answer": "Collection is allowed from 09:00 to 18:00.",
        },
    ])

    result = run_agent(
        "My parcel PKG123 is delayed. Can I collect it today?",
        llm,
        level="l3",
    )

    assert result["status"] == "completed"
    assert result["level"] == "L3"
    assert result["model_turns"] == 3
    assert result["tool_actions"] == 2


def check_l2_rejects_l3_tool() -> None:
    llm = ScriptedLLM([
        {
            "action": "call_tool",
            "tool": "get_depot_info",
            "arguments": {"depot_name": "Penang depot"},
        }
    ])

    result = run_agent("Can I collect from Penang depot?", llm, level="l2")

    assert result["status"] == "degraded"
    assert result["error"] == "tool_not_allowed"


def check_depot_tool() -> None:
    result = get_depot_info("Penang depot")

    assert result["found"] is True
    assert result["collection_allowed"] is True
    assert result["opening_hours"] == "09:00-18:00"


def main() -> int:
    check_l2_still_works()
    check_l3_two_actions()
    check_l2_rejects_l3_tool()
    check_depot_tool()

    print("L3 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
