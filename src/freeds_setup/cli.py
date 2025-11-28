import typer
from pathlib import Path
from freeds_setup.commands.scan_cmd import vault_app
from freeds_setup.commands.init_cmd import init_app

app = typer.Typer(help="Freeds Setup CLI")
app.add_typer(vault_app, name="scan")
app.add_typer(init_app, name="init")

@vault_app.command("scan")
def init_freeds(folder_name: str):
    """
    Initialize entire freeds.
    """
    typer.echo("Initializing Freeds...")
    # Your setup logic here
    typer.echo("Freeds initialized.")


@vault_app.command("init")
def vault_init():
    """
    Initialize a new vault.
    """
    typer.echo("Initializing vault...")
    # Your setup logic here
    typer.echo("Vault initialized.")


@vault_app.command("import")
def vault_import(folder_name: str = typer.Argument(..., help="Folder to import")):
    """
    Import a folder into the vault.
    """
    folder = Path(folder_name)

    if not folder.exists():
        typer.echo(f"Folder does not exist: {folder}")
        raise typer.Exit(code=1)

    typer.echo(f"Importing folder '{folder_name}' into vault...")
    # Your import logic here
    typer.echo("Import complete.")
