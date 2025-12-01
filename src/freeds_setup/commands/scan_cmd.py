import typer
from freeds_setup.helpers.flog import logger
scan_app = typer.Typer(help="Vault operations")

@scan_app.command("scan")
def scan():
    """
    Scan plugins path for plugins.
    """
    logger.commence(f"Scanning for plugins")

    logger.complete("Freeds initialized.")
