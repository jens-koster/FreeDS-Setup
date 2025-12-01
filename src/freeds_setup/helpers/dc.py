from pathlib import Path
import typing
import os
import subprocess
from freeds_setup.helpers.flog  import logger

def execute_dc(params: typing.List[str], work_path:Path) -> None:
    start_dir = Path.cwd()
    if work_path:
        os.chdir(work_path)
    dc = ["docker", "compose", *params]
    if not (Path.cwd() / "docker-compose.yaml").exists():
        raise FileNotFoundError(f"docker-compose.yaml not found in {Path.cwd()}")

    try:
        logger.info(f"Executing: {dc}")
        subprocess.run(dc, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Docker compose command failed: {e}.")
    finally:
        os.chdir(start_dir)
