from glob import glob
import os
from pathlib import Path
import subprocess
import tempfile

import click
from prompt_toolkit import prompt
from prompt_toolkit.completion.filesystem import PathCompleter
from rich.console import Console

from .logo import logo2 as logo

# Enable overrides for local testing purposes
PYTHON_CODEMODDER = os.environ.get("PIXEE_PYTHON_CODEMODDER", "pixee-python-codemodder")
JAVA_CODEMODDER = os.environ.get("PIXEE_JAVA_CODEMODDER", "pixee-java-codemodder")

console = Console()


@click.group()
def main():
    console.print(logo, style="bold cyan")


def run_codemodder(codemodder, path, dry_run):
    common_codemodder_args = ["--dry-run"] if dry_run else []

    codetf = tempfile.NamedTemporaryFile()
    subprocess.run(
        [codemodder, "--output", codetf.name, path] + common_codemodder_args,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return codetf


@main.command()
@click.argument("path", nargs=1, required=False, type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Don't write changes to disk")
def fix(path, dry_run):
    """Find and fix vulnerabilities in your project"""
    console.print("Welcome to Pixee!", style="bold")
    console.print("Let's find and fix vulnerabilities in your project.", style="bold")
    if not path:
        path = prompt(
            "Path to the project to fix: ",
            complete_while_typing=True,
            complete_in_thread=True,
            completer=PathCompleter(),
            default=os.getcwd(),
        )

    console.print("Dry run:", dry_run, style="bold")

    # TODO: better file glob patterns
    if python_files := glob(str(Path(path) / "**" / "*.py"), recursive=True):
        console.print("Running Python codemods...", style="bold")
        python_codetf = run_codemodder(PYTHON_CODEMODDER, path, dry_run)

    if java_files := glob(str(Path(path) / "**" / "*.java"), recursive=True):
        console.print("Running Java codemods...", style="bold")
        java_codetf = run_codemodder(JAVA_CODEMODDER, path, dry_run)


@main.command()
def codemods():
    """List available codemods"""
    console.print("Available codemods:", style="bold")
    result = subprocess.run(
        [PYTHON_CODEMODDER, "--list"], stdout=subprocess.PIPE, check=True
    )
    console.print(result.stdout.decode("utf-8").splitlines())


if __name__ == "__main__":
    main()
