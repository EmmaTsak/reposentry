from typer.testing import CliRunner

from reposentry.cli import app

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
