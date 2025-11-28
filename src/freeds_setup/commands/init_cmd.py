import typer

init_app = typer.Typer(help="Basic setup operations")

@init_app.command("freeds")
def init_freeds():
    """
    Initialize entire freeds.
    """
    typer.echo("Initializing Freeds...")
    # Your setup logic here
    typer.echo("Freeds initialized.")

@init_app.command("vault")
def init_repos():
    """
    Initialize vault.
    Requires repos to be initialized first.
    """
    typer.echo("Initializing Freeds...")
    # Your setup logic here
    typer.echo("Freeds initialized.")
