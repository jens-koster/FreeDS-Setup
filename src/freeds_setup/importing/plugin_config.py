from pathlib import Path
import os
import yaml
import typing
import uuid
from freeds_setup.helpers.bao_client import BaoClient


class PluginConfig:
    """
    Class to hold information about a plugin.
    """

    def __init__(self, plugin_path: Path = None, plugin_name: str = None):

        if plugin_path and plugin_name:
            raise ValueError("plugin_path and plugin_name can't both be provided")
        if not plugin_path and not plugin_name:
            raise ValueError("plugin_path or plugin_name must be be provided")

        if plugin_path:
            self.plugin_data = self._read_file(plugin_path.resolve())
            self.config["plugin_name"] = plugin_path.name
            self.config["plugin_path"] = str(plugin_path)
            if "plugin_id" not in self.config:
                self.config["plugin_id"] = uuid.uuid4().hex
            p = self.path / "README.md"
            if p.exists():
                self.meta["readme"] = str(p)

            p = self.path / "docker-compose.yaml"
            if p.exists():
                self.meta["dc"] = str(p)
        else:
            bao = BaoClient()
            self.plugin_data = bao.read_plugin_config(plugin_name)

    @property
    def name(self):
        return self.config["plugin_name"]

    @property
    def path(self) -> Path:
        return Path(self.config["plugin_path"])

    def _read_file(self, plugin_path: Path) -> dict:
        """
        Load the plugin.yaml file and extract the dictionary from the root element "plugin".
        """
        plugin_data_path = plugin_path / "plugin.yaml"
        if not plugin_data_path.exists():
            raise FileNotFoundError(f"plugin.yaml not found in {self.path}")

        with plugin_data_path.open("r") as f:
            yaml_data = yaml.safe_load(f)
        if not yaml_data:
            raise ValueError(f"No yaml found in: {plugin_data_path}")
        # Ensure the root element "plugin" exists
        if "plugin" not in yaml_data:
            raise ValueError(f"Root element 'plugin' not found in {plugin_data_path}")
        return yaml_data["plugin"]

    def save_to_vault(self):
        bao = BaoClient()
        bao.write_plugin_config(self.name, self.plugin_data)

    def _assert_dict(self, root_dict: str) -> dict[str, typing.Any]:
        """Create sub dict if needed and return it
        ensures manipulating these properties gets reflected in the main dict"""
        if root_dict not in self.plugin_data:
            self.plugin_data[root_dict] = {}
        return self.plugin_data.get(root_dict)

    def set_env(self):
        for key, value in self.get_env().items():
            os.environ[key] = value

    def get_env(self)->dict:
        env = {}
        for key, value in self.config.items():
            env_name = f'FDS_{self.name.upper()}_{key.upper()}'
            env[env_name] = value
        return env

    @property
    def dependencies(self) -> dict[str, typing.Any]:
        return self._assert_dict("dependencies")

    @property
    def resources(self) -> dict[str, typing.Any]:
        return self._assert_dict("resources")

    @property
    def deployments(self) -> dict[str, typing.Any]:
        return self._assert_dict("deployments")

    @property
    def config(self) -> dict[str, typing.Any]:
        return self._assert_dict("config")

    @property
    def meta(self) -> dict[str, typing.Any]:
        return self._assert_dict("meta")
