from datetime import UTC, datetime

import pytest
import typer
from typer.testing import CliRunner

from reposentry.cli import app, parse_repository
from reposentry.clients.github import (
    GitHubClient,
    RepositoryNotFoundError,
)
from reposentry.models.repository import Repository

runner = CliRunner()


def test_status_command() -> None:
    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "RepoSentry" in result.output
    assert "installed and working!" in result.output


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_parse_repository() -> None:
    owner, name = parse_repository("EmmaTsak/reposentry")

    assert owner == "EmmaTsak"
    assert name == "reposentry"


def test_parse_repository_rejects_invalid_format() -> None:
    with pytest.raises(
        typer.BadParameter,
        match="owner/name",
    ):
        parse_repository("reposentry")


def test_scan_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_repository(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> Repository:
        return Repository(
            id=123,
            name=name,
            full_name=f"{owner}/{name}",
            description="Repository health analyzer",
            html_url=f"https://github.com/{owner}/{name}",
            language="Python",
            stargazers_count=5,
            forks_count=1,
            default_branch="main",
            created_at=datetime(2026, 7, 31, tzinfo=UTC),
            updated_at=datetime(2026, 8, 7, tzinfo=UTC),
            pushed_at=datetime(2026, 8, 7, tzinfo=UTC),
        )

    monkeypatch.setattr(
        GitHubClient,
        "get_repository",
        fake_get_repository,
    )

    result = runner.invoke(
        app,
        ["scan", "EmmaTsak/reposentry"],
    )

    assert result.exit_code == 0
    assert "EmmaTsak/reposentry" in result.output
    assert "Python" in result.output
    assert "main" in result.output


def test_scan_command_repository_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_repository(
        self: GitHubClient,
        owner: str,
        name: str,
    ) -> Repository:
        raise RepositoryNotFoundError(f"Repository '{owner}/{name}' was not found.")

    monkeypatch.setattr(
        GitHubClient,
        "get_repository",
        fake_get_repository,
    )

    result = runner.invoke(
        app,
        ["scan", "EmmaTsak/missing"],
    )

    assert result.exit_code == 1
    assert "was not found" in result.output
