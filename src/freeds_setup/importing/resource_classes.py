from abc import ABC, abstractmethod
from string import Template
import secrets
import string
from freeds_setup.helpers.root_config import root_config
from freeds_setup.importing.plugin_config import PluginConfig
from freeds_setup.importing.plugin_config import get_all_plugins

class Resource(ABC):
    """
    Base class for resources (which include dependencies)
    """

    def __init__(self, plugin_config:PluginConfig, name:str, resource:dict):
        self.plugin_config = plugin_config
        self.plugin_name = plugin_config.name
        self.description = resource.get('description')
        self.name = name
        self.params = resource.get('params' , {})
        self.config = plugin_config.config

    def _get_param(self, name)->str:
        return self.params.get(name) or ''

    def _config_name(self, config_name, suffix_name):
        suffix = '_' + suffix_name if suffix_name else ''
        return config_name + suffix

    @abstractmethod
    def provision(self) -> None:
        """Provision the resource and update the config property."""
        pass

class InformationalResource(Resource):
    """Base class for informational resources that don't (yet) perform any actions."""

    def provision(self) -> dict[str:str]:
        """Do nothing."""
        pass

class AdminAccount(Resource):
    def provision(self):
        """Provision a username (freeds) and a random password."""
        self.config["admin_user"] = "freeds"
        # character pool for the password
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # get some random chars
        password = "".join(secrets.choice(alphabet) for _ in range(10))
        self.config["admin_password"] = password


class DataDir(Resource):
    def provision(self):
        """Create a directory data/<plugin>, a name for a subdir in the folder can be proved in params."""
        name = self._get_param('name')
        data_dir = root_config.data_path / self.plugin_name / name
        data_dir.mkdir(parents=True, exist_ok=True)
        self.config[self._config_name('datadir', name)] = str(data_dir)

def get_free_port_number()->int:
    all_ports = []

    for plugin in get_all_plugins():
        all_ports.extend(plugin.ports)

    for port in range(8000,9000):
        if port not in all_ports:
            return port


class Ui(Resource):
    """Assigns a free port for the UI and resolves the uri using the config env variables"""
    def provision(self):
        """Find a free port in the ui range and resolve the uri."""
        uri = self._get_param('uri')
        name = self._get_param('name')
        number = self._get_param('number')
        known_port = self._get_param('known_port')

        if not (number or known_port):
            number = get_free_port_number()
            self.params['number'] = number
        self.config[self._config_name('ui_port', name)] = number
        tmpl = Template(uri)
        uri = tmpl.safe_substitute(self.plugin_config.get_env())
        self.config[self._config_name('ui_uri', name)] = uri

class PostgresDatabase(Resource):
    pass

class S3(Resource):
    pass



class KnownPort(InformationalResource):
    """Allow plugins to reserve specific ports, typically a well know port for some service."""
    pass


resource_classes = {
    name.lower(): cls
    for name, cls in globals().items()
    if isinstance(cls, type)
        and issubclass(cls, Resource)
        and cls is not Resource
        and cls is not InformationalResource
}

if __name__ == "__main__":
    print("Dynamically populated resource_classes:")
    for name, cls in resource_classes.items():
        print(f"{name}: {cls.__name__}")
