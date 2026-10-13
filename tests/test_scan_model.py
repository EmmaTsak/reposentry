from datetime import UTC, datetime

from reposentry.models.issue import GitHubUser, Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.models.scan import RepositoryScan
from reposentry.models.workflow_run import WorkflowRun


def test_repository_scan_counts_items() -> None:
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
        html_url="https://github.com/EmmaTsak/reposentry/actions/runs/1001",
        status="completed",
        conclusion="failure",
        created_at=now,
        updated_at=now,
        run_started_at=now,
    )

    scan = RepositoryScan(
        repository=repository,
        issues=[issue],
        pull_requests=[pull_request],
        workflow_runs=[workflow_run],
    )

    assert scan.open_issue_count == 1
    assert scan.open_pull_request_count == 1
    assert scan.failed_workflow_count == 1
