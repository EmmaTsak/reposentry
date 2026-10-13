from datetime import UTC, datetime

import pytest
import typer
from typer.testing import CliRunner

from reposentry.cli import app, parse_repository
from reposentry.clients.github import RepositoryNotFoundError
from reposentry.models.health_report import RepositoryHealthReport
from reposentry.models.repository import Repository
from reposentry.models.scan import RepositoryScan
from reposentry.services.health import RepositoryHealthAnalyzer
from reposentry.services.scanner import RepositoryScanner

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

    fake_scan = RepositoryScan(
        repository=repository,
        issues=[],
        pull_requests=[],
        workflow_runs=[],
    )

    fake_health_report = RepositoryHealthReport(
        score=92,
        stale_issue_count=1,
        stale_pull_request_count=0,
        failed_workflow_count=0,
        deductions=[],
    )

    async def fake_scan_repository(
        self: RepositoryScanner,
        owner: str,
        name: str,
    ) -> RepositoryScan:
        return fake_scan

    def fake_analyze(
        self: RepositoryHealthAnalyzer,
        scan: RepositoryScan,
        now: datetime | None = None,
    ) -> RepositoryHealthReport:
        return fake_health_report

    monkeypatch.setattr(
        RepositoryScanner,
        "scan",
        fake_scan_repository,
    )

    monkeypatch.setattr(
        RepositoryHealthAnalyzer,
        "analyze",
        fake_analyze,
    )

    result = runner.invoke(
        app,
        ["scan", "EmmaTsak/reposentry"],
    )

    assert result.exit_code == 0
    assert "EmmaTsak/reposentry" in result.output
    assert "Python" in result.output
    assert "Health score" in result.output
    assert "92/100" in result.output
    assert "Open issues" in result.output
    assert "Stale issues" in result.output
    assert "Open pull requests" in result.output
    assert "Stale pull requests" in result.output


def test_scan_command_repository_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_scan_repository(
        self: RepositoryScanner,
        owner: str,
        name: str,
    ) -> RepositoryScan:
        raise RepositoryNotFoundError(f"Repository '{owner}/{name}' was not found.")

    monkeypatch.setattr(
        RepositoryScanner,
        "scan",
        fake_scan_repository,
    )

    result = runner.invoke(
        app,
        ["scan", "EmmaTsak/missing"],
    )

    assert result.exit_code == 1
    assert "was not found" in result.output
