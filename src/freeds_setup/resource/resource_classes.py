from abc import ABC, abstractmethod
import secrets
import string
from freeds_setup.helpers.root_config import root_config

class Resource(ABC):
    """
    Base class for resources (which include dependencies)
    """

    def __init__(self, plugin_name, description, name, params: dict = None):
        self.plugin_name = plugin_name
        self.description = description
        self.name = name
        self.params = params or {}
        self.config = {}

    def _get_param(self, name)->str:
        return self.params.get(name) or ''

    @abstractmethod
    def provision(self) -> None:
        """Provision the resource and update the config property."""
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
        suffix = '_' + name if name else ''
        self.config[f"datadir{suffix}"] = str(data_dir)


class PostgresDatabase(Resource):
    pass


class S3(Resource):
    pass


class InformationalResource(Resource):
    """Base class for informational resources that don't (yet) perform any actions."""

    def provision(self) -> dict[str:str]:
        """Do nothing."""
        pass


class KnownPort(InformationalResource):
    """Allow plugins to reserve specific ports, typically a well know port for some service."""

    pass


resource_classes = {
    name.lower(): cls
    for name, cls in globals().items()
    if isinstance(cls, type) and issubclass(cls, Resource) and cls is not Resource
}

if __name__ == "__main__":
    print("Dynamically populated resource_classes:")
    for name, cls in resource_classes.items():
        print(f"{name}: {cls.__name__}")
