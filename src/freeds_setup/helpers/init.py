import subprocess
import git
from freeds_setup.helpers.flog import logger
from pathlib import Path
from freeds_setup.helpers.root_config import root_config
from freeds_setup.helpers.bao_client import BaoClient
from freeds_setup.helpers.dc import execute_dc
def init_freeds():
    """
    Initialize freeds basics, clone a few repos and setup base folders.
    """
    logger.commence("Initializing Freeds")
    setup_root_dir()
    clone_repos()
    logger.complete()

def init_vault():
    """
    Start and initialize vault.
    """
    root_config.set_env()
    logger.commence("Initializing Vault")
    dc_dir = root_config.plugins_path / "the-free-data-stack" / "vault"
    logger.start("Starting vault")
    execute_dc(["up", "-d"], dc_dir)
    logger.succeed()

    bao = BaoClient()
    if bao.is_initialized():
        logger.info("Vault is already initialized, skipping.")
        logger.complete()
        return
    bao.initialize_vault()
    logger.complete()

def soft_clone(name:str, url:str, target:Path)->bool:
    """Clone a git repo only if the target does not exist yet."""

    if target.exists():
        logger.info(f"Repo {name} already exists at {target}, skipping.")
        return False
    logger.info(f"Cloning repo: {url} into {target}...")
    git.Repo.clone_from(url, target)
    logger.info(f"Repo {name} cloned.")
    return True

def clone_repos() -> None:
    logger.start("Cloning git repos")

    target = root_config.get_freeds_root() / "Freeds"
    url = "https://github.com/jens-koster/FreeDS.git"
    soft_clone("Freeds CLI", url, target)
    plugins = {
        "the-free-data-stack": "https://github.com/jens-koster/the-free-data-stack.git",
    }
    for name, url in plugins.items():
        target = root_config.plugins_path / name
        soft_clone(name, url, target)
    logger.succeed()


def setup_root_dir() -> None:
    """Create system folders in the root dir and set the config."""

    root_path = Path.cwd()

    logger.start(f"Setting up root directory at {root_path}")
    root_config.set_freeds_root(root_path)

    root_config.plugins_path.mkdir(exist_ok=True)
    root_config.data_path.mkdir(exist_ok=True)
    root_config.assets_path.mkdir(exist_ok=True)
    logger.succeed()


if __name__ == '__main__':
    init_vault()