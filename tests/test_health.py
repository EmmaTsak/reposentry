from datetime import UTC, datetime, timedelta

from reposentry.models.issue import GitHubUser, Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.models.scan import RepositoryScan
from reposentry.services.health import RepositoryHealthAnalyzer


def test_detects_stale_issues_and_pull_requests() -> None:
    now = datetime(2026, 10, 13, tzinfo=UTC)

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

    stale_issue = Issue(
        number=1,
        title="Old issue",
        html_url="https://github.com/EmmaTsak/reposentry/issues/1",
        state="open",
        user=user,
        created_at=now - timedelta(days=60),
        updated_at=now - timedelta(days=40),
    )

    recent_issue = Issue(
        number=2,
        title="Recent issue",
        html_url="https://github.com/EmmaTsak/reposentry/issues/2",
        state="open",
        user=user,
        created_at=now - timedelta(days=5),
        updated_at=now - timedelta(days=2),
    )

    stale_pull_request = PullRequest(
        number=3,
        title="Old pull request",
        html_url="https://github.com/EmmaTsak/reposentry/pull/3",
        state="open",
        user=user,
        draft=False,
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=20),
    )

    recent_pull_request = PullRequest(
        number=4,
        title="Recent pull request",
        html_url="https://github.com/EmmaTsak/reposentry/pull/4",
        state="open",
        user=user,
        draft=False,
        created_at=now - timedelta(days=5),
        updated_at=now - timedelta(days=3),
    )

    scan = RepositoryScan(
        repository=repository,
        issues=[
            stale_issue,
            recent_issue,
        ],
        pull_requests=[
            stale_pull_request,
            recent_pull_request,
        ],
    )

    analyzer = RepositoryHealthAnalyzer(
        stale_issue_days=30,
        stale_pull_request_days=14,
    )

    stale_issues = analyzer.get_stale_issues(
        scan,
        now=now,
    )

    stale_pull_requests = analyzer.get_stale_pull_requests(
        scan,
        now=now,
    )

    assert len(stale_issues) == 1
    assert stale_issues[0].number == 1

    assert len(stale_pull_requests) == 1
    assert stale_pull_requests[0].number == 3
