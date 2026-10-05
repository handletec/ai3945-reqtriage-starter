import json

from agent import run_agent


class ScriptedLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.index = 0

    def complete(self, system: str, user: str) -> str:
        response = self.responses[self.index]
        self.index += 1
        return response


def encoded(value: dict) -> str:
    return json.dumps(value)


def test_l2_one_tool_then_limited_final():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "track_package",
            "arguments": {"tracking_id": "PKG123"},
        }),
        encoded({
            "action": "final",
            "answer": (
                "The parcel is delayed at the Penang depot, "
                "but I cannot verify collection information under L2."
            ),
        }),
    ])

    result = run_agent(
        "My parcel PKG123 is delayed. Can I collect it today?",
        llm,
        level="l2",
    )

    assert result["status"] == "completed"
    assert result["level"] == "L2"
    assert result["model_turns"] == 2
    assert result["tool_actions"] == 1
    assert "cannot verify" in result["answer"]


def test_l3_two_tools_then_final():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "track_package",
            "arguments": {"tracking_id": "PKG123"},
        }),
        encoded({
            "action": "call_tool",
            "tool": "get_depot_info",
            "arguments": {"depot_name": "Penang depot"},
        }),
        encoded({
            "action": "final",
            "answer": (
                "Collection is allowed at the Penang depot "
                "while it is open from 09:00 to 18:00."
            ),
        }),
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
    assert "Collection is allowed" in result["answer"]


def test_l2_rejects_l3_only_tool():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "get_depot_info",
            "arguments": {"depot_name": "Penang depot"},
        })
    ])

    result = run_agent(
        "Can I collect from Penang depot?",
        llm,
        level="l2",
    )

    assert result["status"] == "degraded"
    assert result["level"] == "L2"
    assert result["error"] == "tool_not_allowed"


def test_unapproved_tool_is_rejected_at_l3():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "delete_package",
            "arguments": {"tracking_id": "PKG123"},
        })
    ])

    result = run_agent(
        "Delete PKG123",
        llm,
        level="l3",
    )

    assert result["status"] == "degraded"
    assert result["error"] == "tool_not_allowed"
