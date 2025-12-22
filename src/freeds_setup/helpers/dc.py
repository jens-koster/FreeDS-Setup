from pathlib import Path
import typing
import os
import subprocess
from freeds_setup.helpers.flog import logger
from freeds_setup.importing.plugin_config import PluginConfig


def execute_dc(params: typing.List[str], work_path: Path, env:dict) -> None:
    if not (work_path / "docker-compose.yaml").exists():
        raise FileNotFoundError(f"docker-compose.yaml not found in {Path.cwd()}")
    try:
        dc = ["docker-compose", *params]
        logger.info(f"Executing: {dc}")
        full_env = env.copy()
        full_env['PATH'] =  os.environ.get('PATH')
        subprocess.run(args=dc, cwd=work_path, check=True, env=full_env)
    except subprocess.CalledProcessError as e:
        print(f"Docker compose command failed: {e}.")


def start_plugin(plugin_config: PluginConfig) -> None:
    execute_dc(["up", "-d"], work_path=plugin_config.path, env = plugin_config.get_env())


def stop_plugin(plugin_config: PluginConfig) -> None:
    plugin_config.set_env()
    execute_dc(["down"], work_path=plugin_config.path, env = plugin_config.get_env())
