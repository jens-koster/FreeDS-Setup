import git
import time
from freeds_setup.helpers.flog import logger
from pathlib import Path
from freeds_setup.helpers.root_config import root_config
from freeds_setup.helpers.bao_client import BaoClient
from freeds_setup.helpers.dc import execute_dc
import freeds_setup.resource.provision as resource_provision
from  freeds_setup.importing.plugin_config import PluginConfig

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

    logger.commence("Initializing Vault")
    # it's a hardcoded requiremen that the vault plugin is located here
    dc_dir = root_config.plugins_path / "the-free-data-stack" / "vault"
    # do the import, except we need ot avoid using the vault before it exists
    plugin_config = PluginConfig(dc_dir)
    resource_provision.provision_all(plugin_config)
    plugin_config.set_env()
    logger.start("Starting vault")
    execute_dc(["up", "-d"], dc_dir)
    time.sleep(2)
    logger.succeed()

    bao = BaoClient()
    bao.initialize()
    bao.retrieve_tokens_from_logs()
    plugin_config.save_to_vault()
    logger.complete()


def soft_clone(name: str, url: str, target: Path) -> bool:
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
    logger.succeed()


if __name__ == "__main__":
    init_vault()
    baox = BaoClient()
    baox.retrieve_tokens_from_logs()
    import pyperclip
    pyperclip.copy(baox.root_token)
    print(baox.root_token)
