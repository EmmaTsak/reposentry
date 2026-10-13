import httpx

from reposentry.config import Settings
from reposentry.models.issue import Issue
from reposentry.models.repository import Repository


class GitHubClientError(Exception):
    """Base exception for GitHub API errors."""


class RepositoryNotFoundError(GitHubClientError):
    """Raised when a requested repository cannot be found."""


class GitHubClient:
    """Client for communicating with the GitHub REST API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "RepoSentry",
        }

        if self.settings.github_token is not None:
            token = self.settings.github_token.get_secret_value()

            if token:
                headers["Authorization"] = f"Bearer {token}"

        return headers

    async def get_repository(
        self,
        owner: str,
        name: str,
    ) -> Repository:
        """Fetch basic information about a GitHub repository."""

        async with httpx.AsyncClient(
            base_url=self.settings.github_api_url,
            headers=self._build_headers(),
            timeout=self.settings.request_timeout_seconds,
        ) as client:
            response = await client.get(f"/repos/{owner}/{name}")

        if response.status_code == 404:
            raise RepositoryNotFoundError(f"Repository '{owner}/{name}' was not found.")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(
                f"GitHub API request failed with status {response.status_code}."
            ) from exc

        return Repository.model_validate(response.json())

    async def get_issues(
        self,
        owner: str,
        name: str,
    ) -> list[Issue]:
        """Fetch open issues for a GitHub repository."""

        async with httpx.AsyncClient(
            base_url=self.settings.github_api_url,
            headers=self._build_headers(),
            timeout=self.settings.request_timeout_seconds,
        ) as client:
            response = await client.get(
                f"/repos/{owner}/{name}/issues",
                params={
                    "state": "open",
                    "per_page": 100,
                },
            )

        if response.status_code == 404:
            raise RepositoryNotFoundError(f"Repository '{owner}/{name}' was not found.")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(
                f"GitHub API request failed with status {response.status_code}."
            ) from exc

        data = response.json()

        return [
            Issue.model_validate(item) for item in data if "pull_request" not in item
        ]
