from datetime import datetime

from reposentry.models.repository import Repository


def test_repository_model_parses_github_data() -> None:
    data = {
        "id": 123,
        "name": "reposentry",
        "full_name": "EmmaTsak/reposentry",
        "description": "Repository health analyzer",
        "html_url": "https://github.com/EmmaTsak/reposentry",
        "language": "Python",
        "stargazers_count": 5,
        "forks_count": 1,
        "default_branch": "main",
        "created_at": "2026-07-31T10:00:00Z",
        "updated_at": "2026-08-07T16:00:00Z",
        "pushed_at": "2026-08-07T16:00:00Z",
    }

    repository = Repository.model_validate(data)

    assert repository.id == 123
    assert repository.full_name == "EmmaTsak/reposentry"
    assert repository.language == "Python"
    assert isinstance(repository.created_at, datetime)
