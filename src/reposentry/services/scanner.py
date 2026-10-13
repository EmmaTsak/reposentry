import asyncio

from reposentry.clients.github import GitHubClient
from reposentry.models.scan import RepositoryScan


class RepositoryScanner:
    """Coordinates GitHub data collection for a repository."""

    def __init__(self, github_client: GitHubClient) -> None:
        self.github_client = github_client

    async def scan(
        self,
        owner: str,
        name: str,
    ) -> RepositoryScan:
        """Collect repository health data concurrently."""

        (
            repository,
            issues,
            pull_requests,
            workflow_runs,
        ) = await asyncio.gather(
            self.github_client.get_repository(owner, name),
            self.github_client.get_issues(owner, name),
            self.github_client.get_pull_requests(owner, name),
            self.github_client.get_workflow_runs(owner, name),
        )

        return RepositoryScan(
            repository=repository,
            issues=issues,
            pull_requests=pull_requests,
            workflow_runs=workflow_runs,
        )
