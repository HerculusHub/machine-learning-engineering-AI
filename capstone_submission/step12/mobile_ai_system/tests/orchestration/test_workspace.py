from mobile_ai_system.workspace.workspace import Workspace


def test_workspace():

    ws = Workspace()

    ws.update(
        "analysis",
        {
            "score": 95
        },
    )

    assert ws.get("analysis")["score"] == 95

    ws.add_artifact(
        "report",
        "report.md",
    )

    assert ws.artifact("report") == "report.md"

    ws.clear()

    assert ws.get("analysis") == {}