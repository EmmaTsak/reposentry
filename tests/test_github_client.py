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


@respx.mock
async def test_get_pull_requests() -> None:
    response_data = [
        {
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
    ]

    respx.get(
        "https://api.github.com/repos/EmmaTsak/reposentry/pulls",
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

    pull_requests = await client.get_pull_requests(
        "EmmaTsak",
        "reposentry",
    )

    assert len(pull_requests) == 1
    assert pull_requests[0].number == 15
    assert pull_requests[0].title == "Add repository health scoring"
    assert pull_requests[0].draft is False


@respx.mock
async def test_get_pull_requests_repository_not_found() -> None:
    respx.get(
        "https://api.github.com/repos/EmmaTsak/missing/pulls",
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
        await client.get_pull_requests(
            "EmmaTsak",
            "missing",
        )


@respx.mock
async def test_get_workflow_runs() -> None:
    response_data = {
        "total_count": 2,
        "workflow_runs": [
            {
                "id": 1001,
                "name": "CI",
                "html_url": (
                    "https://github.com/EmmaTsak/reposentry/actions/runs/1001"
                ),
                "status": "completed",
                "conclusion": "success",
                "created_at": "2026-10-12T10:00:00Z",
                "updated_at": "2026-10-12T10:05:00Z",
                "run_started_at": "2026-10-12T10:01:00Z",
            },
            {
                "id": 1002,
                "name": "Tests",
                "html_url": (
                    "https://github.com/EmmaTsak/reposentry/actions/runs/1002"
                ),
                "status": "completed",
                "conclusion": "failure",
                "created_at": "2026-10-13T08:00:00Z",
                "updated_at": "2026-10-13T08:04:00Z",
                "run_started_at": "2026-10-13T08:01:00Z",
            },
        ],
    }

    respx.get(
        "https://api.github.com/repos/EmmaTsak/reposentry/actions/runs",
        params={
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

    workflow_runs = await client.get_workflow_runs(
        "EmmaTsak",
        "reposentry",
    )

    assert len(workflow_runs) == 2

    assert workflow_runs[0].name == "CI"
    assert workflow_runs[0].conclusion == "success"

    assert workflow_runs[1].name == "Tests"
    assert workflow_runs[1].conclusion == "failure"


@respx.mock
async def test_get_workflow_runs_repository_not_found() -> None:
    respx.get(
        "https://api.github.com/repos/EmmaTsak/missing/actions/runs",
        params={
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
        await client.get_workflow_runs(
            "EmmaTsak",
            "missing",
        )
