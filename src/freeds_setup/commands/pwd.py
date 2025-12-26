import typer
import pyperclip
from freeds_setup.helpers.flog import logger
from freeds_setup.helpers.bao_client import BaoClient
pwd_app = typer.Typer(help="Get passwords to clipboard")


@pwd_app.command("bao")
def init_freeds():
    """
    Print and copy openbao admin password to clipboard.
    """
    bao = BaoClient()
    bao.retrieve_tokens_from_logs()
    print(f"Bao root token: {bao.root_token}")
    pyperclip.copy(bao.root_token)


@pwd_app.command("vault")
def init_repos():
    """
    Initialize vault.
    Requires repos to be initialized first.
    """
    logger.header("Setting up Vault")
    init.init_vault()
