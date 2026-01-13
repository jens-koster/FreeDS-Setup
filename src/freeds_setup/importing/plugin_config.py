from pathlib import Path
from graphlib import TopologicalSorter
import os
import yaml
import typing
import uuid
from freeds_setup.helpers.bao_client import BaoClient


class PluginConfig:
    """
    Class to hold information about a plugin.
    """

    def __init__(self, plugin: Path | str = None):
        """Load plugin config, if Path is provided it is loaded from file else from vault."""
        if not plugin:
            plugin = os.environ.get('FDS_CURRENT_PLUGIN_NAME')
        if not plugin:
            raise ValueError(f'plugin name must be provided either as parameter or as env FDS_CURRENT_PLUGIN_NAME.')

        if isinstance(plugin, Path):
            self.plugin_data = self._read_file(plugin.resolve())
            self.config["plugin_name"] = plugin.name
            self.config["plugin_path"] = str(plugin)
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
            self.plugin_data = bao.read_plugin_config(plugin)
            if not self.plugin_data:
                raise ValueError(f'Plugin {plugin} not found in vault.')

    @property
    def name(self):
        return self.config["plugin_name"]

    @property
    def path(self) -> Path:
        return Path(self.config["plugin_path"])

    def _read_file(self, plugin: Path) -> dict:
        """
        Load the plugin.yaml file and extract the dictionary from the root element "plugin".
        """
        plugin_data_path = plugin / "plugin.yaml"
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
            env[env_name] = str(value)
        return env

    @property
    def ports(self)->list[int]:
        p = []
        for name, r in self.resources.items():
            if r['type'].lower() in ('knownport', 'ui'):
                port = r.get('params',{}).get('number',None)
                if port:
                    p.append(int(port))
        return p
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

    def __repr__(self)->str:
        return f"<PluginConfig {self.name}>"


def sort_plugins(plugin_configs: list[PluginConfig]) -> list[PluginConfig]:
    """Sort plugins in dependency order, vault is always first."""
    plugin_configs = {p.name: p for p in plugin_configs}
    vault = None
    if "vault" in plugin_configs:
        vault = plugin_configs.pop('vault')

    deps = {p.name: p.dependencies for p in plugin_configs.values()}
    ts = TopologicalSorter(deps)
    sorted_keys = list(ts.static_order())
    sorted_plugin_configs = list(plugin_configs[name] for name in sorted_keys)
    if vault:
        sorted_plugin_configs.insert(0, vault)
    return sorted_plugin_configs


def get_all_plugins()->list[PluginConfig]:
    bao = BaoClient()
    plugins= list([PluginConfig(p) for p in bao.list_plugins()])
    return sort_plugins(plugins)