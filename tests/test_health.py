from datetime import UTC, datetime, timedelta

from reposentry.models.issue import GitHubUser, Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.models.scan import RepositoryScan
from reposentry.models.workflow_run import WorkflowRun
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
        workflow_runs=[],
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


def test_health_score_includes_explainable_deductions() -> None:
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
        created_at=now - timedelta(days=200),
        updated_at=now - timedelta(days=40),
        pushed_at=now - timedelta(days=40),
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

    stale_pull_request = PullRequest(
        number=2,
        title="Old pull request",
        html_url="https://github.com/EmmaTsak/reposentry/pull/2",
        state="open",
        user=user,
        draft=False,
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=20),
    )

    scan = RepositoryScan(
        repository=repository,
        issues=[stale_issue],
        pull_requests=[stale_pull_request],
        workflow_runs=[],
    )

    analyzer = RepositoryHealthAnalyzer(
        stale_issue_days=30,
        stale_pull_request_days=14,
    )

    report = analyzer.analyze(
        scan,
        now=now,
    )

    assert report.score == 82
    assert report.stale_issue_count == 1
    assert report.stale_pull_request_count == 1
    assert len(report.deductions) == 3
    assert report.failed_workflow_count == 0


def test_recent_failed_workflow_reduces_health_score() -> None:
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
        created_at=now - timedelta(days=100),
        updated_at=now,
        pushed_at=now,
    )

    failed_workflow = WorkflowRun(
        id=1001,
        name="CI",
        html_url=("https://github.com/EmmaTsak/reposentry/actions/runs/1001"),
        status="completed",
        conclusion="failure",
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
        run_started_at=now - timedelta(days=1),
    )

    successful_workflow = WorkflowRun(
        id=1002,
        name="CI",
        html_url=("https://github.com/EmmaTsak/reposentry/actions/runs/1002"),
        status="completed",
        conclusion="success",
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
        run_started_at=now - timedelta(days=1),
    )

    old_failed_workflow = WorkflowRun(
        id=1003,
        name="CI",
        html_url=("https://github.com/EmmaTsak/reposentry/actions/runs/1003"),
        status="completed",
        conclusion="failure",
        created_at=now - timedelta(days=20),
        updated_at=now - timedelta(days=20),
        run_started_at=now - timedelta(days=20),
    )

    scan = RepositoryScan(
        repository=repository,
        issues=[],
        pull_requests=[],
        workflow_runs=[
            failed_workflow,
            successful_workflow,
            old_failed_workflow,
        ],
    )

    analyzer = RepositoryHealthAnalyzer(
        recent_workflow_days=7,
    )

    report = analyzer.analyze(
        scan,
        now=now,
    )

    assert report.score == 90
    assert report.failed_workflow_count == 1
    assert len(report.deductions) == 1
    assert report.deductions[0].points == 10
