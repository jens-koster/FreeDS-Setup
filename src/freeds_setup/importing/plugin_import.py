from freeds_setup.helpers.flog import logger
from graphlib import TopologicalSorter
from pathlib import Path
from freeds_setup.helpers.root_config import root_config
import freeds_setup.helpers.bao_client as bao_client
import freeds_setup.helpers.dc as dc
from freeds_setup.importing.plugin_config import PluginConfig
from freeds_setup.resource.provision import provision_all


def import_plugin(folders: Path | list[Path]) -> None:
    """
    Import a plugin, reads plugin.yaml, populates databses and secrets and stores in vault.
    """

    if isinstance(folders, Path):
        folders = [folders]

    logger.commence(f"Import {len(folders)} plugins")
    for folder in folders:
        logger.start(f"Import plugin from folder: {folder}")
        plugin_config = PluginConfig(folder)
        logger.info(f"Plugin: {plugin_config.name}, {plugin_config.path} ")
        provision_all(plugin_config)
        bao = bao_client.BaoClient()
        bao.write_plugin_config(plugin_config.name, plugin_config.plugin_yaml)
        new_config = PluginConfig(plugin_name=plugin_config.name)
        dc.start_plugin(new_config)
        logger.succeed()
    logger.complete()


def scan(path: Path = None) -> list[PluginConfig]:
    """
    Scan folder and subfolders for plugins (folders with plugin.yaml).
    """
    if path is None:
        path = root_config.plugins_path

    logger.info(f"Scanning: {path}")
    plugin_configs = []

    for subfolder in path.rglob("*"):
        if subfolder.is_dir():
            if (subfolder / "plugin.yaml").exists():
                p = PluginConfig(plugin_path=subfolder)
                plugin_configs.append(p)

    logger.info(f"Found plugins: {list([p.name for p in plugin_configs])}.")
    return plugin_configs


def sort_plugins(plugin_configs: list[PluginConfig]) -> list[PluginConfig]:
    """Sort plugins in dependency order."""
    plugin_configs = {p.name: p for p in plugin_configs}
    deps = {p.name: p.dependecies for p in plugin_configs.values()}
    ts = TopologicalSorter(deps)
    sorted = list(ts.static_order())
    logger.info(f"Plugin sorted order:{sorted}")
    return list(plugin_configs[name] for name in sorted)


if __name__ == "__main__":
    scan()
    # import_plugin(Path("/Users/jens/src/myfreeds/the-free-data-stack/postgres"))

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
        "config": {},
        "meta": {},
        # The dependencies are also Resources where all attributes are defaulted.
        "dependencies": {
            "postgres": {},
            "s3": {},
            "redis": {},
            "kafka": {},
            "jupyter": {},
            "spark": {},
        },
        # files to be deployed for the plugin
        # there'll be a command to re-deploy these files
        "deployments": {
            "dags": {
                # airflow is one
                # freeds knows anbout a few plugins, where you'll want to deploy into that plugin's home folder.
                "type": "AirflowDags",
                "description": "Deploy my airflow dags",
                "params": {"dir": "dags"},
            },
            "bronze": {
                "type": "S3",
                "description": "Deploy bronze notebook folder from repo to s3 for running in the jupyter notebook plugin",
                "params": {
                    "dir": "notebooks",
                },
            },
            "init_db": {
                "type": "Sql",
                "description": "Setup my database schema.",
                # all sql files will be exocuted in alphabetical order
                "params": {
                    "dir": "sql/db_init",
                },
            },
        },
        "resources": {
            "pguser": {
                "type": "PostgresUser",
                "description": "A user account + password in postgres",
                "params": {
                    "name": "_2",  # name will be prefixed with the plugin name
                },
            },
            "pgdb": {
                "type": "PostgresDatabase",
                "description": "A database and ",
                "params": {
                    "name": "_db",  # name will be prefixed with the plugin name
                },
            },
            "data": {
                "type": "Directory",
                "description": "a directory in the plugin home directory",
                "params": {
                    "name": "logs",
                },
            },
            "kafdrop": {
                "type": "UIPort",
                "description": "Kafdrop kafka admin ui",
                "params": {
                    "ui_uri": "https://127.0.0.1:{{ FDS_KAFKA_KAFGEN_PORT }}",  # again support jinja2 templating
                },
            },
            "listening_port": {
                "type": "KnownPort",
                "description": "A port defined by accepted standards",
                "params": {"number": 5432},
            },
            "archive_bucket": {
                "type": "S3Bucket",
                "description": "extra bucket for archiving data",
                "params": {
                    "name": "schema_name",
                },
            },
            "data_dir": {
                "type": "AbsolutePath",
                "description": "Some testdata for my plugin",
                "params": {"dir": "data"},
            },
        },
    }
