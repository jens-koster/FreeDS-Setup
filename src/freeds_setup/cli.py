import os
import typer
from pathlib import Path
from freeds_setup.commands.init_cmd import init_app
from freeds_setup.helpers.root_config import root_config


app = typer.Typer(help="Freeds Setup CLI")
root_config.set_env()

app.add_typer(init_app, name="init")
