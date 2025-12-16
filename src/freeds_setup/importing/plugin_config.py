from freeds_setup.helpers.flog import logger
from pathlib import Path
import yaml
import typing
import uuid

class PluginConfig:
    """
    Class to hold information about a plugin.
    """
    def __init__(self, plugin_path: Path):
        self.path = plugin_path.resolve()
        self.name = self.dir_path.name
        self.plugin_data = self.load_yaml()

        p = self.dir_path / "README.md"
        if p.exists():
            self.meta['readme'] = p

        p = self.dir_path / "docker-compose.yaml"
        if p.exists():
            self.meta['dc'] = p

        self.config['path'] = self.path
        self.config['name'] = self.name
        self.config['id'] = uuid.uuid4()

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


    def _assert_dict(self, root_dict:str)->dict[str, typing.Any]:
        """Create sub dict if needed and return it
        ensures manipulating these properties gets reflected in the main dict"""
        if root_dict not in self.plugin_data:
            self.plugin_data[root_dict] = {}
        return self.plugin_data.get(root_dict)

    @property
    def dependencies(self)->dict[str, typing.Any]:
        return self._assert_dict("dependencies")

    @property
    def resources(self)->dict[str, typing.Any]:
        return self._assert_dict("resources")

    @property
    def deployments(self)->dict[str, typing.Any]:
        return self._assert_dict("deployments")

    @property
    def config(self)->dict[str, typing.Any]:
        return self._assert_dict("config")

    @property
    def meta(self)->dict[str, typing.Any]:
        return self._assert_dict("meta")
