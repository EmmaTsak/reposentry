import asyncio

import typer
from rich.console import Console
from rich.table import Table

from reposentry import __version__
from reposentry.clients.github import (
    GitHubClient,
    GitHubClientError,
    RepositoryNotFoundError,
)
from reposentry.config import Settings
from reposentry.models.health_report import RepositoryHealthReport
from reposentry.models.scan import RepositoryScan
from reposentry.services.health import RepositoryHealthAnalyzer
from reposentry.services.scanner import RepositoryScanner

app = typer.Typer(
    name="reposentry",
    help="Analyze GitHub repository health and generate engineering reports.",
    no_args_is_help=True,
)

console = Console()


def parse_repository(value: str) -> tuple[str, str]:
    """Parse a repository in owner/name format."""

    parts = value.strip().split("/")

    if len(parts) != 2 or not all(parts):
        raise typer.BadParameter("Repository must use the format 'owner/name'.")

    return parts[0], parts[1]


def display_scan(
    scan: RepositoryScan,
    health_report: RepositoryHealthReport,
) -> None:
    """Display repository scan information."""

    repository = scan.repository

    table = Table(
        title=f"Repository: {repository.full_name}",
        show_header=True,
    )

    table.add_column("Property")
    table.add_column("Value")

    table.add_row(
        "Health score",
        f"{health_report.score}/100",
    )
    table.add_row(
        "Name",
        repository.name,
    )
    table.add_row(
        "Description",
        repository.description or "No description",
    )
    table.add_row(
        "Language",
        repository.language or "Unknown",
    )
    table.add_row(
        "Stars",
        str(repository.stargazers_count),
    )
    table.add_row(
        "Forks",
        str(repository.forks_count),
    )
    table.add_row(
        "Default branch",
        repository.default_branch,
    )
    table.add_row(
        "Open issues",
        str(scan.open_issue_count),
    )
    table.add_row(
        "Stale issues",
        str(health_report.stale_issue_count),
    )
    table.add_row(
        "Open pull requests",
        str(scan.open_pull_request_count),
    )
    table.add_row(
        "Stale pull requests",
        str(health_report.stale_pull_request_count),
    )
    table.add_row(
        "Last push",
        repository.pushed_at.isoformat() if repository.pushed_at else "Unknown",
    )

    console.print(table)


async def scan_repository(repository_name: str) -> None:
    """Scan and display a GitHub repository."""

    owner, name = parse_repository(repository_name)

    settings = Settings()
    github_client = GitHubClient(settings)
    scanner = RepositoryScanner(github_client)
    analyzer = RepositoryHealthAnalyzer()

    try:
        scan = await scanner.scan(owner, name)
        health_report = analyzer.analyze(scan)
    except RepositoryNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    except GitHubClientError as exc:
        console.print(f"[bold red]GitHub error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    display_scan(scan, health_report)


@app.command()
def scan(
    repository: str = typer.Argument(
        ...,
        help="GitHub repository in owner/name format.",
    ),
) -> None:
    """Scan a GitHub repository."""

    asyncio.run(scan_repository(repository))


@app.command()
def status() -> None:
    """Confirm that RepoSentry is installed and working."""

    console.print(
        f"[bold green]RepoSentry[/bold green] version "
        f"[bold blue]{__version__}[/bold blue] "
        "is installed and working!"
    )


@app.command()
def version() -> None:
    """Display the installed RepoSentry version."""

    console.print(f"RepoSentry {__version__}")


def main() -> None:
    """Start the RepoSentry command-line interface."""

    app()
