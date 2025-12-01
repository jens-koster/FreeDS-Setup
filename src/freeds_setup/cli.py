import os
import typer
from pathlib import Path
from freeds_setup.commands.init_cmd import init_app

app = typer.Typer(help="Freeds Setup CLI")
os.environ['FREEDS_VAULT_URI']="http://127.0.0.1:8200"

app.add_typer(init_app, name="init")

