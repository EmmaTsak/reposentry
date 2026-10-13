from datetime import datetime

from reposentry.models.pull_request import PullRequest


def test_pull_request_model_parses_github_data() -> None:
    data = {
        "number": 15,
        "title": "Add repository health scoring",
        "html_url": "https://github.com/EmmaTsak/reposentry/pull/15",
        "state": "open",
        "user": {
            "login": "EmmaTsak",
            "html_url": "https://github.com/EmmaTsak",
        },
        "draft": False,
        "created_at": "2026-10-05T10:00:00Z",
        "updated_at": "2026-10-12T14:30:00Z",
        "closed_at": None,
        "merged_at": None,
    }

    pull_request = PullRequest.model_validate(data)

    assert pull_request.number == 15
    assert pull_request.title == "Add repository health scoring"
    assert pull_request.state == "open"
    assert pull_request.user.login == "EmmaTsak"
    assert pull_request.draft is False
    assert isinstance(pull_request.created_at, datetime)
    assert pull_request.merged_at is None
