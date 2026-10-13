from datetime import UTC, datetime

import pytest

from reposentry.clients.github import GitHubClient
from reposentry.config import Settings
from reposentry.models.issue import GitHubUser, Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.models.workflow_run import WorkflowRun
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

    workflow_run = WorkflowRun(
        id=1001,
        name="CI",
        html_url=("https://github.com/EmmaTsak/reposentry/actions/runs/1001"),
        status="completed",
        conclusion="failure",
        created_at=now,
        updated_at=now,
        run_started_at=now,
    )

    async def fake_get_repository(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> Repository:
        return repository

    async def fake_get_issues(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> list[Issue]:
        return [issue]

    async def fake_get_pull_requests(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> list[PullRequest]:
        return [pull_request]

    async def fake_get_workflow_runs(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> list[WorkflowRun]:
        return [workflow_run]

    monkeypatch.setattr(
        GitHubClient,
        "get_repository",
        fake_get_repository,
    )

    monkeypatch.setattr(
        GitHubClient,
        "get_issues",
        fake_get_issues,
    )

    monkeypatch.setattr(
        GitHubClient,
        "get_pull_requests",
        fake_get_pull_requests,
    )

    monkeypatch.setattr(
        GitHubClient,
        "get_workflow_runs",
        fake_get_workflow_runs,
    )

    client = GitHubClient(Settings(github_token=None))

    scanner = RepositoryScanner(client)

    result = await scanner.scan(
        "EmmaTsak",
        "reposentry",
    )

    assert result.repository.full_name == "EmmaTsak/reposentry"
    assert result.open_issue_count == 1
    assert result.open_pull_request_count == 1
    assert result.failed_workflow_count == 1
