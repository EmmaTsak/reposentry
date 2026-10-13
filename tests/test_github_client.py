import httpx
import pytest
import respx

from reposentry.clients.github import (
    GitHubClient,
    RepositoryNotFoundError,
)
from reposentry.config import Settings


@respx.mock
async def test_get_repository() -> None:
    response_data = {
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

    route = respx.get("https://api.github.com/repos/EmmaTsak/reposentry").mock(
        return_value=httpx.Response(
            200,
            json=response_data,
        )
    )

    settings = Settings(github_token=None)
    client = GitHubClient(settings)

    repository = await client.get_repository(
        "EmmaTsak",
        "reposentry",
    )

    assert route.called
    assert repository.id == 123
    assert repository.full_name == "EmmaTsak/reposentry"
    assert repository.language == "Python"


@respx.mock
async def test_repository_not_found() -> None:
    respx.get("https://api.github.com/repos/EmmaTsak/missing").mock(
        return_value=httpx.Response(
            404,
            json={"message": "Not Found"},
        )
    )

    settings = Settings(github_token=None)
    client = GitHubClient(settings)

    with pytest.raises(
        RepositoryNotFoundError,
        match="EmmaTsak/missing",
    ):
        await client.get_repository(
            "EmmaTsak",
            "missing",
        )


@respx.mock
async def test_get_issues_filters_pull_requests() -> None:
    response_data = [
        {
            "number": 10,
            "title": "Fix README",
            "html_url": "https://github.com/EmmaTsak/reposentry/issues/10",
            "state": "open",
            "user": {
                "login": "EmmaTsak",
                "html_url": "https://github.com/EmmaTsak",
            },
            "created_at": "2026-10-01T10:00:00Z",
            "updated_at": "2026-10-10T10:00:00Z",
            "closed_at": None,
        },
        {
            "number": 11,
            "title": "Add API support",
            "html_url": "https://github.com/EmmaTsak/reposentry/pull/11",
            "state": "open",
            "user": {
                "login": "EmmaTsak",
                "html_url": "https://github.com/EmmaTsak",
            },
            "created_at": "2026-10-02T10:00:00Z",
            "updated_at": "2026-10-11T10:00:00Z",
            "closed_at": None,
            "pull_request": {
                "url": "https://api.github.com/repos/EmmaTsak/reposentry/pulls/11",
            },
        },
    ]

    respx.get(
        "https://api.github.com/repos/EmmaTsak/reposentry/issues",
        params={
            "state": "open",
            "per_page": 100,
        },
    ).mock(
        return_value=httpx.Response(
            200,
            json=response_data,
        )
    )

    settings = Settings(github_token=None)
    client = GitHubClient(settings)

    issues = await client.get_issues(
        "EmmaTsak",
        "reposentry",
    )

    assert len(issues) == 1
    assert issues[0].number == 10
    assert issues[0].title == "Fix README"


@respx.mock
async def test_get_issues_repository_not_found() -> None:
    respx.get(
        "https://api.github.com/repos/EmmaTsak/missing/issues",
        params={
            "state": "open",
            "per_page": 100,
        },
    ).mock(
        return_value=httpx.Response(
            404,
            json={"message": "Not Found"},
        )
    )

    settings = Settings(github_token=None)
    client = GitHubClient(settings)

    with pytest.raises(
        RepositoryNotFoundError,
        match="EmmaTsak/missing",
    ):
        await client.get_issues(
            "EmmaTsak",
            "missing",
        )
