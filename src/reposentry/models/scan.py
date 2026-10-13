from pydantic import BaseModel

from reposentry.models.issue import Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository


class RepositoryScan(BaseModel):
    """Complete scan result for a GitHub repository."""

    repository: Repository
    issues: list[Issue]
    pull_requests: list[PullRequest]

    @property
    def open_issue_count(self) -> int:
        """Return the number of open issues."""

        return len(self.issues)

    @property
    def open_pull_request_count(self) -> int:
        """Return the number of open pull requests."""

        return len(self.pull_requests)
