import typer
from rich.console import Console

from reposentry import __version__

app = typer.Typer(
    name="reposentry",
    help="Analyze GitHub repository health and generate engineering reports.",
    no_args_is_help=True,
)

console = Console()


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
