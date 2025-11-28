import typer

scan_app = typer.Typer(help="Vault operations")


@vault_app.command("vault")
def init_repos():
    """
    Initialize vault.
    Requires repos to be initialized first.
    """
    typer.echo("Initializing Freeds...")
    # Your setup logic here
    typer.echo("Freeds initialized.")
