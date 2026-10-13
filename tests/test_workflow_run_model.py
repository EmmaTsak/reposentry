from datetime import datetime

from reposentry.models.workflow_run import WorkflowRun


def test_workflow_run_model_parses_github_data() -> None:
    data = {
        "id": 987,
        "name": "CI",
        "html_url": ("https://github.com/EmmaTsak/reposentry/actions/runs/987"),
        "status": "completed",
        "conclusion": "failure",
        "created_at": "2026-10-12T09:00:00Z",
        "updated_at": "2026-10-12T09:10:00Z",
        "run_started_at": "2026-10-12T09:01:00Z",
    }

    workflow_run = WorkflowRun.model_validate(data)

    assert workflow_run.id == 987
    assert workflow_run.name == "CI"
    assert workflow_run.status == "completed"
    assert workflow_run.conclusion == "failure"
    assert isinstance(workflow_run.created_at, datetime)
