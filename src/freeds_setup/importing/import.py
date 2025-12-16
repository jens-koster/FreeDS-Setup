from freeds_setup.helpers.flog import logger
from pathlib import Path
import yaml

import freeds_setup.helpers.bao_client as bao
from  freeds_setup.helpers.root_config import root_config


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
            logger.info(f"Checking folder: {subfolder}")
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

# we're storing the original plugin file in the vault.
# everything else is stored with the expanded env name
# thinking it makes it easier to understnad when troubleshooting.

if __name__ == "__main__":
    scan_folder(Path("./test"))
    # all plugins get:
    #    * home directory
    #    * vault folder
    #    * env vars:
    #        FDS_<PLUGIN NAME>_VAULT_URI
    #        FDS_<PLUGIN NAME>_VAULT_CLIENT_ID
    #        FDS_<PLUGIN NAME>_VAULT_CLIENT_SECRET
    #        FDS_<PLUGIN NAME>_HOME_DIR

    # Example plugin.yaml structure

    # import:
    # * load and validate plugin.yaml
    # * expand all values to env variables
    # * store in vault
    # * create any resources required by the plugin like the databbases, s3 buckets, credentials for other plugins etc
    # * initial deploy

    # re-deploy:
    # execute deployments section


    plugin = {
        # name-value for anyting the plugin wants get env variables for.
        # name will be preficed with FDS_<PLUGIN NAME>_
        "config":{},
        "meta":{},
        # The dependencies are also Resources where all attributes are defaulted.
        "dependencies": {
            'postgres':{},
            's3':{},
            'redis':{},
            "kafka":{},
            "jupyter":{},
            "spark":{}
        },
        # files to be deployed for the plugin
        # there'll be a command to re-deploy these files

        "deployments": {
            "dags" : {
                # freeds knows anbout a few plugins, where you'll want to deploy into that plugin's home folder.
                # airflow is one
                "type": "AirflowDags",
                "description": "Deploy my airflow dags",
                "params" : {
                    "dir": "dags"
                }
            },

            "bronze": {
                "type": "S3",
                "description": "Deploy bronze notebook folder from repo to s3 for running in the jupyter notebook plugin",
                "params" : {
                    "dir": "notebooks",
                    }
            },

            "init_db": {
                "type": "Sql",
                "description": "Setup my database schema.",
                # all sql files will be exocuted in alphabetical order
                "params" : {
                    "dir": "sql/db_init",
                }
            },
        },

        "resources": {
            "data":{
                "type": "Directory",
                "description": "a directory in the plugin home directory",
                "params": {
                    "name": "logs",
                }
            },

            "kafdrop":{
                "type": "UIPort",
                "description": "Kafdrop kafka admin ui",
                "params": {
                    "ui_uri": "https://127.0.0.1:{{ FDS_KAFKA_KAFGEN_PORT }}", # again support jinja2 templating
                }
            },

            "listening_port": {
                "type": "KnownPort",
                "description": "A port defined by accepted standards",
                "params": {
                    "number": 5432
                }
            },

            "archive_bucket":{
                "type": "S3Bucket",
                "description": "extra bucket for archiving data",
                "params": {
                    "name": "schema_name",
                }
            },

            "data_dir":{
                "type": "AbsolutePath",
                "description": "Some testdata for my plugin",
                "params" : {
                    "dir": "data"
                }
            },

        }
    }