from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from reposentry.clients.github import GitHubClient
from reposentry.config import Settings
from reposentry.models.issue import GitHubUser, Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.services.scanner import RepositoryScanner


async def test_scan_combines_repository_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime.now(UTC)

    repository = Repository(
        id=123,
        name="reposentry",
        full_name="EmmaTsak/reposentry",
        description="Repository health analyzer",
        html_url="https://github.com/EmmaTsak/reposentry",
        language="Python",
        stargazers_count=5,
        forks_count=1,
        default_branch="main",
        created_at=now,
        updated_at=now,
        pushed_at=now,
    )

    user = GitHubUser(
        login="EmmaTsak",
        html_url="https://github.com/EmmaTsak",
    )

    issue = Issue(
        number=1,
        title="Example issue",
        html_url="https://github.com/EmmaTsak/reposentry/issues/1",
        state="open",
        user=user,
        created_at=now,
        updated_at=now,
    )

    pull_request = PullRequest(
        number=2,
        title="Example pull request",
        html_url="https://github.com/EmmaTsak/reposentry/pull/2",
        state="open",
        user=user,
        draft=False,
        created_at=now,
        updated_at=now,
    )

    client = GitHubClient(Settings(github_token=None))

    mock_get_repository = AsyncMock(return_value=repository)
    mock_get_issues = AsyncMock(return_value=[issue])
    mock_get_pull_requests = AsyncMock(return_value=[pull_request])

    monkeypatch.setattr(
        client,
        "get_repository",
        mock_get_repository,
    )
    monkeypatch.setattr(
        client,
        "get_issues",
        mock_get_issues,
    )
    monkeypatch.setattr(
        client,
        "get_pull_requests",
        mock_get_pull_requests,
    )

    scanner = RepositoryScanner(client)

    result = await scanner.scan(
        "EmmaTsak",
        "reposentry",
    )

    assert result.repository.full_name == "EmmaTsak/reposentry"
    assert result.open_issue_count == 1
    assert result.open_pull_request_count == 1

    mock_get_repository.assert_awaited_once_with(
        "EmmaTsak",
        "reposentry",
    )
    mock_get_issues.assert_awaited_once_with(
        "EmmaTsak",
        "reposentry",
    )
    mock_get_pull_requests.assert_awaited_once_with(
        "EmmaTsak",
        "reposentry",
    )
