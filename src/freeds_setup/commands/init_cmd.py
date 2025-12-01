import typer
import freeds_setup.helpers.init as init
from freeds_setup.helpers.flog import logger

init_app = typer.Typer(help="Basic setup operations")

@init_app.command("freeds")
def init_freeds():
    """
    Initialize entire freeds.
    """
    logger.header("Setting up The Free Data Stack (FreeDS)")
    init.init_freeds()


@init_app.command("vault")
def init_repos():
    """
    Initialize vault.
    Requires repos to be initialized first.
    """
    logger.header("Setting up Vault")
    init.init_vault()
