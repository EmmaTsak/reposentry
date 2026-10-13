from datetime import UTC, datetime, timedelta

from reposentry.models.health_report import (
    HealthDeduction,
    RepositoryHealthReport,
)
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

    def analyze(
        self,
        scan: RepositoryScan,
        now: datetime | None = None,
    ) -> RepositoryHealthReport:
        """Calculate an explainable repository health score."""

        current_time = now or datetime.now(UTC)

        stale_issues = self.get_stale_issues(
            scan,
            now=current_time,
        )

        stale_pull_requests = self.get_stale_pull_requests(
            scan,
            now=current_time,
        )

        score = 100
        deductions: list[HealthDeduction] = []

        if stale_issues:
            points = len(stale_issues) * 3
            score -= points

            deductions.append(
                HealthDeduction(
                    reason=f"{len(stale_issues)} stale issue(s)",
                    points=points,
                )
            )

        if stale_pull_requests:
            points = len(stale_pull_requests) * 5
            score -= points

            deductions.append(
                HealthDeduction(
                    reason=(f"{len(stale_pull_requests)} stale pull request(s)"),
                    points=points,
                )
            )

        if scan.repository.pushed_at is not None:
            inactive_days = (current_time - scan.repository.pushed_at).days

            if inactive_days > 90:
                score -= 20

                deductions.append(
                    HealthDeduction(
                        reason="Repository inactive for over 90 days",
                        points=20,
                    )
                )

            elif inactive_days > 30:
                score -= 10

                deductions.append(
                    HealthDeduction(
                        reason="Repository inactive for over 30 days",
                        points=10,
                    )
                )

        score = max(0, min(score, 100))

        return RepositoryHealthReport(
            score=score,
            stale_issue_count=len(stale_issues),
            stale_pull_request_count=len(stale_pull_requests),
            deductions=deductions,
        )
