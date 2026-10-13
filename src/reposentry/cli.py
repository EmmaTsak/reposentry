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
from reposentry.models.repository import Repository

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
        raise typer.BadParameter(
            "Repository must use the format 'owner/name'."
        )

    return parts[0], parts[1]


def display_repository(repository: Repository) -> None:
    """Display repository information in a terminal table."""

    table = Table(
        title=f"Repository: {repository.full_name}",
        show_header=True,
    )

    table.add_column("Property")
    table.add_column("Value")

    table.add_row("Name", repository.name)
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
        "Last push",
        repository.pushed_at.isoformat()
        if repository.pushed_at
        else "Unknown",
    )

    console.print(table)


async def scan_repository(repository_name: str) -> None:
    """Fetch and display a GitHub repository."""

    owner, name = parse_repository(repository_name)

    settings = Settings()
    github = GitHubClient(settings)

    try:
        repository = await github.get_repository(owner, name)
    except RepositoryNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    except GitHubClientError as exc:
        console.print(f"[bold red]GitHub error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    display_repository(repository)


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