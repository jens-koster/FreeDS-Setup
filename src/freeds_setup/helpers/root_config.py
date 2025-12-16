from pathlib import Path
import os


class RootConfig:
    def __init__(self):
        self.known_location = Path.home() / ".freeds"
        if self.known_location.is_file():
            self.known_location.unlink()
        self.known_location.mkdir(exist_ok=True)
        self.freeds_prefix = "FDS_"
        self.set_env()


    def _get(self, key: str, default=None) -> str:
        file_path = self.known_location / key
        if not file_path.exists() and default:
            return default

        with open(file_path, "r") as f:
            return Path(f.read())

    def _set(self, key: str, value:str) -> str:
        with open(self.known_location / key, "w") as f:
            f.write(value)

    def make_env_name(self, plugin:str, key:str)->str:
        """Format an env variable name fomr plugin and value name (key)."""
        return f"{self.freeds_prefix}_{plugin.upper()}_{key.upper()}"

    def set_env(self)->None:
        self.get_vault_uri()
        self.get_freeds_root()

    def get_freeds_root(self)->Path:
        root = Path(self._get("freeds_dir"))
        os.environ['FREEDS_ROOT_PATH']=str(root)
        return root

    def set_freeds_root(self, freeds_root_path:Path)->None:
        os.environ['FREEDS_ROOT_PATH']=str(freeds_root_path)
        self._set("freeds_dir", str(freeds_root_path))

    def get_vault_uri(self)->str:
        vault_uri = self._get("vault_uri", "http://127.0.0.1:8200")
        os.environ['FREEDS_VAULT_URI'] = vault_uri
        return vault_uri

    def set_vault_uri(self, vault_uri)->None:
        os.environ['FREEDS_VAULT_URI'] = vault_uri
        self._set("vault_uri", vault_uri)

    @property
    def plugins_path(self)->Path:
        return self.get_freeds_root() / "plugins"

    @property
    def data_path(self)->Path:
        return self.get_freeds_root() / "data"

    @property
    def assets_path(self)->Path:
        return self.get_freeds_root() / "assets"

root_config = RootConfig()
