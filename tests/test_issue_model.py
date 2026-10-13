from datetime import datetime

from reposentry.models.issue import Issue


def test_issue_model_parses_github_data() -> None:
    data = {
        "number": 12,
        "title": "Fix CLI output",
        "html_url": "https://github.com/EmmaTsak/reposentry/issues/12",
        "state": "open",
        "user": {
            "login": "EmmaTsak",
            "html_url": "https://github.com/EmmaTsak",
        },
        "created_at": "2026-10-01T10:00:00Z",
        "updated_at": "2026-10-10T15:30:00Z",
        "closed_at": None,
    }

    issue = Issue.model_validate(data)

    assert issue.number == 12
    assert issue.title == "Fix CLI output"
    assert issue.state == "open"
    assert issue.user.login == "EmmaTsak"
    assert isinstance(issue.created_at, datetime)
    assert issue.closed_at is None
