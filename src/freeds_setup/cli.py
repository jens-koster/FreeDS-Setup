import os
import typer
from pathlib import Path
from freeds_setup.commands.init_cmd import init_app
from freeds_setup.helpers.root_config import root_config


app = typer.Typer(help="Freeds Setup CLI")
root_config.set_env()

app.add_typer(init_app, name="init")



@app.command("scan")
def scan(
    folder: Path = typer.Argument('.', help="Optional folder name to scan"),
    import_flag: bool = typer.Option(False, "--import", "-i", help="Import flag to enable importing")
):
    """
    Scan a folder and optionally import its contents.
    """
    if folder:
        typer.echo(f"Scanning folder: {folder}")
    else:
        typer.echo("Scanning the current directory...")

    if import_flag:
        typer.echo("Import flag is enabled. Importing contents...")
    else:
        typer.echo("Import flag is disabled. No import will be performed.")


@app.command("import")
def scan(
    folder: Path = typer.Argument(..., help="Optional folder name to scan")
):
    """
    import a plugin
    """
    if folder:
        typer.echo(f"Importing: {folder}")
