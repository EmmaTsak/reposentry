from datetime import UTC, datetime, timedelta

from reposentry.models.issue import Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.scan import RepositoryScan


class RepositoryHealthAnalyzer:
    """Analyze repository activity for potential maintenance problems."""

    def __init__(
        self,
        stale_issue_days: int = 30,
        stale_pull_request_days: int = 14,
    ) -> None:
        self.stale_issue_days = stale_issue_days
        self.stale_pull_request_days = stale_pull_request_days

    def get_stale_issues(
        self,
        scan: RepositoryScan,
        now: datetime | None = None,
    ) -> list[Issue]:
        """Return issues that have not been updated recently."""

        current_time = now or datetime.now(UTC)
        cutoff = current_time - timedelta(days=self.stale_issue_days)

        return [issue for issue in scan.issues if issue.updated_at < cutoff]

    def get_stale_pull_requests(
        self,
        scan: RepositoryScan,
        now: datetime | None = None,
    ) -> list[PullRequest]:
        """Return pull requests that have not been updated recently."""

        current_time = now or datetime.now(UTC)
        cutoff = current_time - timedelta(days=self.stale_pull_request_days)

        return [
            pull_request
            for pull_request in scan.pull_requests
            if pull_request.updated_at < cutoff
        ]
