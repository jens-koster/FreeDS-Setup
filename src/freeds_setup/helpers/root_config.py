from pathlib import Path
import os
class RootConfig:
    def __init__(self):
        self.known_location = Path.home() / ".freeds"
        if self.known_location.is_file():
            self.known_location.unlink()
        self.known_location.mkdir(exist_ok=True)

    def _get(self, key: str) -> str:
        with open(self.known_location / key, "r") as f:
            return Path(f.read())

    def _set(self, key: str, value:str) -> str:
        with open(self.known_location / key, "w") as f:
            f.write(value)

    def get_freeds_root(self)->Path:
        root = Path(self._get("freeds_dir"))
        os.environ['FREEDS_ROOT_PATH']=str(root)
        return root

    def set_freeds_root(self, freeds_root_path:Path)->None:
        os.environ['FREEDS_ROOT_PATH']=str(freeds_root_path)
        self._set("freeds_dir", str(freeds_root_path))

    def get_vault_uri(self)->str:
        return self._get("vault_uri")

    def set_vault_uri(self, vault_uri)->None:
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
