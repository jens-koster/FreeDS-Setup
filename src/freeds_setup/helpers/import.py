from freeds_setup.helpers.flog import logger
from pathlib import Path
import yaml

class PluginConfig:
    """
    Class to hold information about a plugin.
    """
    def __init__(self, plugin_path: Path):
        self.dir_path = plugin_path
        self.name = self.dir_path.name
        self.has_readme = (self.dir_path / "README.md").exists()
        self.has_docker_compose = (self.dir_path / "docker-compose.yaml").exists()
        self.plugin_data = self.load_yaml()

    def load_yaml(self) -> dict:
        """
        Load the plugin.yaml file and extract the dictionary from the root element "plugin".
        """
        plugin_yaml_path = self.dir_path / "plugin.yaml"
        if not plugin_yaml_path.exists():
            raise FileNotFoundError(f"plugin.yaml not found in {self.dir_path}")

        with plugin_yaml_path.open("r") as f:
            yaml_data = yaml.safe_load(f)

        # Ensure the root element "plugin" exists
        if "plugin" not in yaml_data:
            raise ValueError(f"Root element 'plugin' not found in {plugin_yaml_path}")

        plugin_data = yaml_data["plugin"]
        return plugin_data


def handle_postgres(plugin_config: PluginConfig) -> None:
    """
    Handle postgres configs, create database, schemas and user.
    """

    for key in plugin_config.plugin_data.keys():
        key = key.lower()

        logger.info(f"Postgres Plugin Key: {key} Value: {plugin_config.plugin_data[key]}")

def handle_s3(plugin_config: PluginConfig) -> None:
    """
    Handle s3 requirements for the plugin, create folders etc.
    """

    pass  # Placeholder for actual implementation

def handle_folders(plugin_config: PluginConfig) -> None:
    """
    Handle folder requirements for the plugin.
    """

    pass  # Placeholder for actual implementation


def import_plugin(folders: Path | list[Path])-> None:
    """
    Import a plugin, reads plugin.yaml, populates databses and secrets and stores in vault.
    """

    if isinstance(folders, Path):
        folders = [folders]

    logger.commence(f"Importing {len(folders)} plugins")
    for folder in folders:
        logger.start(f"Importing plugin from folder: {folder}")
        plugin_info = PluginInfo(folder)
        logger.info(f"Plugin found: {plugin_info.name} dc: {plugin_info.has_docker_compose}")

        logger.succeed()

    logger.complete()



def scan_folder(folder: Path) -> list[Path]:
    """
    Scan folder and subfolders for plugins (folders with plugin.yaml).
    Checks if README.md or docker-compose.yaml exists in the same folder.
    """
    logger.commence(f"Scanning folder: {folder}")

    # List to store plugin folders
    plugin_folders = []

    # Recursively iterate through all subdirectories
    for subfolder in folder.rglob("*"):
        if subfolder.is_dir():
            # Check if plugin.yaml exists in the folder
            plugin_yaml = subfolder / "plugin.yaml"
            if plugin_yaml.exists():
                logger.start(f"Found plugin.yaml in: {subfolder}")

                # Check for README.md and docker-compose.yaml
                readme = subfolder / "README.md"
                docker_compose = subfolder / "docker-compose.yaml"

                if readme.exists():
                    logger.info(f"README.md found in: {subfolder}")
                else:
                    logger.warn(f"README.md missing in: {subfolder}")

                if docker_compose.exists():
                    logger.info(f"docker-compose.yaml found in: {subfolder}")
                else:
                    logger.warn(f"docker-compose.yaml missing in: {subfolder}")

                # Add the folder to the plugin list
                plugin_folders.append(subfolder)
                logger.succeed(f"Plugin folder added: {subfolder}")

    logger.complete(f"Scanning complete. Found {len(plugin_folders)} plugin(s).")
    return plugin_folders

if __name__ == "__main__":
    plugin = {
        "config":{
            "s3_client_id" : "",
            "s3_client_secret" : "",
            "s3_bucket" : "",
            "postgres_db" : "",
            "postgres_user" : "",
            "postgres_password" : "",
            "vault_uri" : "",
            "vault_token" : ""

        },

        "setup": {
            "postgres_schemas" : [],
            "s3_folders" : [],
            "data_folders" : [],
            "asset_folders" : []
        },

        "resources": {
            "ports": [
                {"number": 5432, "description": "postgres" },
            ],
            "containers": [],
        }
    }