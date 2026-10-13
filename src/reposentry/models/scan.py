from pydantic import BaseModel

from reposentry.models.issue import Issue
from reposentry.models.pull_request import PullRequest
from reposentry.models.repository import Repository
from reposentry.models.workflow_run import WorkflowRun


class RepositoryScan(BaseModel):
    """Complete scan result for a GitHub repository."""

    repository: Repository
    issues: list[Issue]
    pull_requests: list[PullRequest]
    workflow_runs: list[WorkflowRun]

    @property
    def open_issue_count(self) -> int:
        """Return the number of open issues."""

        return len(self.issues)

    @property
    def open_pull_request_count(self) -> int:
        """Return the number of open pull requests."""

        return len(self.pull_requests)

    @property
    def failed_workflow_count(self) -> int:
        """Return the number of failed workflow runs."""

        return sum(
            1
            for workflow_run in self.workflow_runs
            if workflow_run.conclusion == "failure"
        )
