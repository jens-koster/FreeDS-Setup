import typer

init_app = typer.Typer(help="Basic setup operations")

@init_app.command("repos")
def init_repos():
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

@init_app.command("plugins")
def init_repos():
    """
    Initialize plugins.
    Requires vault to be initialized first.
    """
    typer.echo("Initializing Freeds...")
    # Your setup logic here
    typer.echo("Freeds initialized.")
