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


def test_one_tool_then_final():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "track_package",
            "arguments": {"tracking_id": "PKG123"},
        }),
        encoded({
            "action": "final",
            "answer": "The parcel is delayed at the Penang depot.",
        }),
    ])

    result = run_agent("Where is PKG123?", llm)

    assert result["status"] == "completed"
    assert result["model_turns"] == 2
    assert result["tool_actions"] == 1


def test_unapproved_tool_is_rejected():
    llm = ScriptedLLM([
        encoded({
            "action": "call_tool",
            "tool": "delete_package",
            "arguments": {"tracking_id": "PKG123"},
        })
    ])

    result = run_agent("Where is PKG123?", llm)

    assert result["status"] == "degraded"
    assert result["error"] == "tool_not_allowed"
